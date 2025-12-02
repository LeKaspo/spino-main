"""
Continuous speech -> Whisper (de/en) -> command execution.

- Listens to the default microphone with a lightweight energy-based VAD.
- When an utterance ends (speech followed by silence), it:
  * sends the audio to Whisper for transcription (de or en),
  * prints the transcribed text,
  * checks if it contains any known command phrases (case-insensitive),
  * if a command matches, calls the associated Python function.

Example command:
- "move forward", "go forward", "fahre geradeaus", "fahre vorwärts", "fahre nach vorne"
  -> call move.py with: --direction forward
"""

import argparse
import logging
import os
import queue
import sys
import tempfile
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy import signal
from huggingface_hub.errors import LocalEntryNotFoundError


# Faster Whisper
try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Failed to import 'faster_whisper'.", file=sys.stderr)
    print("Install it with: pip install faster-whisper", file=sys.stderr)
    sys.exit(1)

try:
    import server.sendcommands
    print("import funktioniert")
except ImportError:
    def voicecommand(cmd):
        print(f"DEBUG: Mock execution of command '{cmd}'")

logger = logging.getLogger("speechInput")

SAMPLE_RATE = 16000
FRAME_DURATION_MS = 20  # fixed 20 ms frames (legacy WebRTC-compatible size)
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
DEFAULT_MODELS_ROOT = (Path(__file__).resolve().parent.parent / "models").as_posix()


class EnergyVAD:
    """Energy-based VAD with hangover to avoid premature cut-offs."""

    THRESHOLD_MULTIPLIERS = {
        0: 1.25,
        1: 1.55,
        2: 1.8,
        3: 2.3,
    }

    def __init__(
        self,
        aggressiveness: int = 2,
        hangover_ms: int = 380,
        attack_ms: int = 55,
        min_energy: float = 40.0,
    ):
        self.aggressiveness = int(np.clip(aggressiveness, 0, 3))
        self.min_energy = float(max(1.0, min_energy))
        self.alpha = 0.995  # how quickly the noise estimate adapts to quieter frames
        self.noise_floor = max(self.min_energy, 250.0)

        frame_ms = max(1, FRAME_DURATION_MS)
        self.hangover_frames = max(1, int(hangover_ms / frame_ms))
        self.activation_frames = max(1, int(attack_ms / frame_ms))

        self._activation_run = 0
        self._hangover_left = 0

    def _frame_energy(self, frame_bytes: bytes) -> float:
        frame = np.frombuffer(frame_bytes, dtype=np.int16)
        if not frame.size:
            return 0.0
        return float(np.sqrt(np.mean(frame.astype(np.float32) ** 2)))

    def _update_noise_floor(self, energy: float, threshold: float) -> None:
        if energy <= 0.0:
            return
        if energy < threshold:
            target = max(self.min_energy, energy)
        else:
            target = max(self.min_energy, min(energy, self.noise_floor * 3))
        self.noise_floor = self.alpha * self.noise_floor + (1 - self.alpha) * target

    def is_speech(self, frame_bytes: bytes, sample_rate: int) -> bool:  # noqa: D401
        """Return True if speech is active, using hangover to smooth drops."""

        _ = sample_rate  # kept for API compatibility
        energy = self._frame_energy(frame_bytes)

        threshold = max(
            self.noise_floor * self.THRESHOLD_MULTIPLIERS[self.aggressiveness],
            self.min_energy * 2,
        )

        self._update_noise_floor(energy, threshold)

        if energy >= threshold:
            self._activation_run = min(self.activation_frames, self._activation_run + 1)
        else:
            self._activation_run = max(0, self._activation_run - 1)

        if self._activation_run >= self.activation_frames:
            self._hangover_left = self.hangover_frames
            return True

        if self._hangover_left > 0:
            self._hangover_left -= 1
            return True

        return False


class Recorder:
    def __init__(self, sample_rate=SAMPLE_RATE, frame_ms=FRAME_DURATION_MS):
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.frames_queue = queue.Queue()
        self._stream = None
        self.running = False

    def _callback(self, indata, frames, time_info, status):
        if status:
            print("Input stream status:", status, file=sys.stderr)
        # convert float32 [-1,1] to int16 PCM
        audio = (indata[:, 0] * 32767).astype(np.int16)
        self.frames_queue.put(audio.tobytes())

    def start(self):
        if self.running:
            return
        self.running = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self._callback,
            blocksize=FRAME_SIZE,
        )
        self._stream.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None


def frames_from_wav(path):
    """Yield 20 ms frames from a WAV file as int16 bytes at SAMPLE_RATE."""
    data, sr = sf.read(path, dtype="int16")
    mono = np.asarray(data)
    if mono.ndim > 1:
        mono = mono[:, 0]
    if sr != SAMPLE_RATE:
        mono = signal.resample(
            mono.astype(np.float32),
            int(len(mono) * SAMPLE_RATE / sr),
        ).astype(np.int16)

    step = FRAME_SIZE
    i = 0
    while i + step <= len(mono):
        chunk = mono[i : i + step].astype(np.int16)
        yield chunk.tobytes()
        i += step


def save_temp_wav(samples_bytes: bytes) -> str:
    """Save raw int16 bytes to a temporary WAV file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    arr = np.frombuffer(samples_bytes, dtype=np.int16)
    sf.write(path, arr, SAMPLE_RATE)
    return path


def configure_logging(debug: bool):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger.setLevel(level)


def samples_duration_ms(samples_bytes: bytes) -> float:
    sample_count = len(samples_bytes) / 2  # int16
    return float(sample_count / SAMPLE_RATE * 1000.0)


def average_amplitude(samples_bytes: bytes) -> float:
    arr = np.frombuffer(samples_bytes, dtype=np.int16)
    if not arr.size:
        return 0.0
    return float(np.mean(np.abs(arr)))


@dataclass
class UtteranceMeta:
    idx: int
    started_at: float
    ended_at: float
    duration_ms: float
    avg_amplitude: float
    frame_count: int


def should_drop_utterance(meta: UtteranceMeta, min_ms: int, min_amp: float) -> bool:
    if meta.duration_ms < min_ms:
        logger.debug(
            "Dropping utterance %s: too short %.1f ms < %s ms",
            meta.idx,
            meta.duration_ms,
            min_ms,
        )
        return True
    if meta.avg_amplitude < min_amp:
        logger.debug(
            "Dropping utterance %s: avg amplitude %.1f < %.1f",
            meta.idx,
            meta.avg_amplitude,
            min_amp,
        )
        return True
    return False


def dump_utterance(samples_bytes: bytes, dump_dir: str, utterance_idx: int) -> str | None:
    if not dump_dir:
        return None
    os.makedirs(dump_dir, exist_ok=True)
    path = os.path.join(dump_dir, f"utterance_{utterance_idx:05d}.wav")
    arr = np.frombuffer(samples_bytes, dtype=np.int16)
    sf.write(path, arr, SAMPLE_RATE)
    logger.debug("Saved utterance %s to %s", utterance_idx, path)
    return path


# -------------------- Command handling --------------------

COMMANDS = [
    {
        "name": "forwards",
        "phrases": [
            "move forward",
            "go forward",
            " geradeaus",
            " vorwärts",
            "nach vorne",
        ]
    },
    {
        "name": "backwards",
        "phrases": [   
            "move backward",
            "go backward",
            " rückwärts",
            "nach hinten",
        ]
    },
    {
        "name": "left",
        "phrases": [
            "turn left",
            "go left",
            "nach links",
            "biege links ab",
        ]
    },
    {
        "name": "right",
        "phrases": [
            "turn right",
            "go right",
            "nach rechts",
            "biege rechts ab",
        ]
    },
    {
        "name": "fullstop",
        "phrases": [
            " stop",
            " halt",
            " wait",
            " stopp",
            " anhalten",
            " warte",
            " stoppe"
        ]
    },
    {
        "name": "turnLeft",
        "phrases": [
            "rotate left",
            "turn around left",
            "spin left",
            "look to the left",
            "look left",
            "drehe dich nach links",
            "dreh dich nach links",
            "schaue nach links",
        ]
    },
    {
        "name": "turnRight",
        "phrases": [
            "rotate right",
            "turn around right",
            "spin right",
            "look to the right",
            "look right",
            "drehe dich nach rechts",
            "dreh dich nach rechts",
            "schaue nach rechts",
        ]
    },
    {
        "name": "turn180",
        "phrases": [
            "turn around",
            "rotate around",
            "spin around",
            "drehe dich um",
            "dreh dich um",
        ]
    }
]


def _normalize_command_text(text: str) -> str:
    cleaned = [
        (ch if (ch.isalnum() or ch.isspace()) else " ")
        for ch in text.lower()
    ]
    return " ".join("".join(cleaned).split())


def check_commands(transcript: str):
    """Case-insensitive substring match of command phrases in the transcript."""
    text = _normalize_command_text(transcript)
    for cmd in COMMANDS:
        for phrase in cmd["phrases"]:
            if _normalize_command_text(phrase) in text:
                logger.info("Command triggered: %s via phrase '%s'", cmd["name"], phrase)
                server.sendcommands.voicecommand(cmd["name"])
                return



# -------------------- Main logic --------------------


def transcribe_utterance(
    wmodel,
    samples_bytes: bytes,
    language: str,
    meta: UtteranceMeta,
    dump_dir: str | None,
):
    """Save samples to WAV, run Whisper, return transcribed text."""
    wavpath = None
    debug_path = dump_utterance(samples_bytes, dump_dir, meta.idx)
    started = time.perf_counter()
    try:
        wavpath = save_temp_wav(samples_bytes)
        logger.info(
            "Utterance %s -> Whisper start | dur=%.1f ms | amp=%.1f | frames=%s | dump=%s",
            meta.idx,
            meta.duration_ms,
            meta.avg_amplitude,
            meta.frame_count,
            debug_path or "-",
        )
        segments, _ = wmodel.transcribe(wavpath, language=language, beam_size=5)
        text = " ".join(segment.text for segment in segments).strip()
        latency = time.perf_counter() - started
        logger.info(
            "Utterance %s -> Whisper done in %.2f s | transcript=%s",
            meta.idx,
            latency,
            text if text else "<empty>",
        )
        return text
    finally:
        if wavpath and os.path.exists(wavpath):
            try:
                os.remove(wavpath)
            except Exception:
                pass


def handle_utterance(wmodel, samples, language, dump_dir, meta):
    try:
        text = transcribe_utterance(wmodel, samples, language, meta, dump_dir)
    except Exception:
        logger.exception("Utterance %s -> Whisper crashed", meta.idx)
        return

    if not text:
        print(f"Transcript [{meta.idx}]: <empty>")
        return

    print(f"Transcript [{meta.idx}]: {text}")
    check_commands(text)


def _cleanup_done_futures(pending: deque):
    while pending and pending[0][1].done():
        pending.popleft()


def resolve_model_dir(args) -> Path:
    if args.model_path:
        candidate = Path(args.model_path).expanduser().resolve()
    else:
        root = Path(args.models_root).expanduser().resolve()
        candidate = root / f"faster-whisper-{args.model}"

    if not candidate.exists():
        raise FileNotFoundError(
            f"Faster-Whisper model directory not found: {candidate}. "
            f"Place the exported model there or pass --model-path."
        )
    return candidate


def create_whisper_model(args, model_dir: Path | None = None):
    """Create a Faster-Whisper model with CLI overrides."""
    model_dir = model_dir or resolve_model_dir(args)

    try:
        return WhisperModel(
            str(model_dir),
            device=args.device,
            compute_type=args.compute_type,
            local_files_only=True,
        )
    except LocalEntryNotFoundError as err:
        logger.error("Failed to load Faster-Whisper model from %s", model_dir)
        raise err



def run_live(args):
    recorder = Recorder()
    vad = EnergyVAD(
        aggressiveness=args.vad_aggressiveness,
        hangover_ms=args.vad_hangover_ms,
        attack_ms=args.vad_attack_ms,
        min_energy=args.vad_min_energy,
    )

    model_dir = resolve_model_dir(args)
    logger.info("Loading Faster Whisper model from %s", model_dir)
    wmodel = create_whisper_model(args, model_dir)

    executor = ThreadPoolExecutor(max_workers=args.workers, thread_name_prefix="whisper")
    pending: deque = deque()

    recorder.start()
    print(f"Listening (language={args.language}). Press Ctrl-C to stop.")

    frame_buffer: list[bytes] = []
    speech = False
    silence_frames = 0
    silence_ms_threshold = args.silence_ms
    utterance_counter = 0
    speech_started_at = None

    try:
        while True:
            try:
                frame = recorder.frames_queue.get(timeout=1.0)
            except queue.Empty:
                _cleanup_done_futures(pending)
                continue

            queue_depth = recorder.frames_queue.qsize()
            if queue_depth > args.queue_warn:
                backlog_sec = queue_depth * FRAME_DURATION_MS / 1000.0
                logger.warning(
                    "Input queue backlog: %s frames (~%.1f s). Whisper still busy.",
                    queue_depth,
                    backlog_sec,
                )

            is_speech = vad.is_speech(frame, SAMPLE_RATE)
            if is_speech:
                if not speech:
                    speech_started_at = time.perf_counter()
                frame_buffer.append(frame)
                speech = True
                silence_frames = 0
            else:
                if speech:
                    silence_frames += 1
                    if silence_frames * FRAME_DURATION_MS > silence_ms_threshold:
                        frame_count = len(frame_buffer)
                        samples = b"".join(frame_buffer)
                        frame_buffer = []
                        speech = False
                        silence_frames = 0

                        if not samples:
                            continue

                        utterance_counter += 1
                        meta = UtteranceMeta(
                            idx=utterance_counter,
                            started_at=speech_started_at or time.perf_counter(),
                            ended_at=time.perf_counter(),
                            duration_ms=samples_duration_ms(samples),
                            avg_amplitude=average_amplitude(samples),
                            frame_count=frame_count,
                        )
                        logger.debug(
                            "Utterance %s captured | dur=%.1f ms | amp=%.1f | frames=%s",
                            meta.idx,
                            meta.duration_ms,
                            meta.avg_amplitude,
                            meta.frame_count,
                        )
                        if should_drop_utterance(
                            meta,
                            args.min_utterance_ms,
                            args.min_avg_amplitude,
                        ):
                            continue

                        _cleanup_done_futures(pending)
                        if len(pending) >= args.max_pending:
                            dropped_id, dropped_future = pending.popleft()
                            if not dropped_future.done():
                                logger.warning(
                                    "Cancelling utterance %s because pending queue is full.",
                                    dropped_id,
                                )
                                dropped_future.cancel()

                        future = executor.submit(
                            handle_utterance,
                            wmodel,
                            samples,
                            args.language,
                            args.dump_utterances,
                            meta,
                        )
                        pending.append((meta.idx, future))
            _cleanup_done_futures(pending)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        recorder.stop()
        executor.shutdown(wait=True)


def run_file(args):
    """Optional: process a WAV file instead of microphone (for quick testing)."""
    vad = EnergyVAD(
        aggressiveness=args.vad_aggressiveness,
        hangover_ms=args.vad_hangover_ms,
        attack_ms=args.vad_attack_ms,
        min_energy=args.vad_min_energy,
    )
    model_dir = resolve_model_dir(args)
    logger.info("Loading Faster Whisper model from %s", model_dir)
    wmodel = create_whisper_model(args, model_dir)
    print("Processing file:", args.file)

    frame_buffer: list[bytes] = []
    speech = False
    silence_frames = 0
    utterance_counter = 0
    speech_started_at = None

    for frame in frames_from_wav(args.file):
        is_speech = vad.is_speech(frame, SAMPLE_RATE)
        if is_speech:
            if not speech:
                speech_started_at = time.perf_counter()
            frame_buffer.append(frame)
            speech = True
            silence_frames = 0
        else:
            if speech:
                silence_frames += 1
                if silence_frames * FRAME_DURATION_MS > args.silence_ms:
                    frame_count = len(frame_buffer)
                    samples = b"".join(frame_buffer)
                    frame_buffer = []
                    speech = False
                    silence_frames = 0

                    if not samples:
                        continue

                    utterance_counter += 1
                    meta = UtteranceMeta(
                        idx=utterance_counter,
                        started_at=speech_started_at or time.perf_counter(),
                        ended_at=time.perf_counter(),
                        duration_ms=samples_duration_ms(samples),
                        avg_amplitude=average_amplitude(samples),
                        frame_count=frame_count,
                    )
                    if should_drop_utterance(
                        meta,
                        args.min_utterance_ms,
                        args.min_avg_amplitude,
                    ):
                        continue

                    handle_utterance(
                        wmodel,
                        samples,
                        args.language,
                        args.dump_utterances,
                        meta,
                    )
            # else: silence without active speech -> ignore

    # left-over partial utterance
    if frame_buffer:
        samples = b"".join(frame_buffer)
        meta = UtteranceMeta(
            idx=utterance_counter + 1,
            started_at=speech_started_at or time.perf_counter(),
            ended_at=time.perf_counter(),
            duration_ms=samples_duration_ms(samples),
            avg_amplitude=average_amplitude(samples),
            frame_count=len(frame_buffer),
        )
        handle_utterance(wmodel, samples, args.language, args.dump_utterances, meta)


def main():
    parser = argparse.ArgumentParser(
        description="Microphone STT with Whisper (de/en) and simple command mapping."
    )
    parser.add_argument(
        "--model",
        default="small",
        help="Whisper model name (tiny, base, small, medium, large)",
    )
    parser.add_argument(
        "--model-path",
        help="Explicit path to a Faster-Whisper model directory (skips auto lookup).",
    )
    parser.add_argument(
        "--models-root",
        default=DEFAULT_MODELS_ROOT,
        help="Directory containing faster-whisper-* folders (default: %(default)s)",
    )
    parser.add_argument(
        "--language",
        choices=["de", "en"],
        default="de",
        help="Language for Whisper transcription (de or en)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Device for Faster Whisper (cpu, cuda, auto, etc.)",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="Quantization compute type (int8, int8_float16, float16, etc.)",
    )
    parser.add_argument(
        "--vad-aggressiveness",
        type=int,
        choices=[0, 1, 2, 3],
        default=2,
        help="Energy VAD aggressiveness (0 = least, 3 = most aggressive).",
    )
    parser.add_argument(
        "--vad-hangover-ms",
        type=int,
        default=380,
        help="How long to keep speech active after energy dips (ms).",
    )
    parser.add_argument(
        "--vad-attack-ms",
        type=int,
        default=55,
        help="Minimum duration above threshold before speech is considered active (ms).",
    )
    parser.add_argument(
        "--vad-min-energy",
        type=float,
        default=40.0,
        help="Lower RMS bound to stabilize adaptive energy thresholds.",
    )
    parser.add_argument(
        "--silence-ms",
        type=int,
        default=400,
        help="Milliseconds of silence to treat as end-of-utterance.",
    )
    parser.add_argument(
        "--min-utterance-ms",
        type=int,
        default=300,
        help="Drop utterances shorter than this duration (ms).",
    )
    parser.add_argument(
        "--min-avg-amplitude",
        type=float,
        default=650.0,
        help="Drop utterances with mean absolute amplitude below this (0-32767).",
    )
    parser.add_argument(
        "--dump-utterances",
        help="Optional directory to store captured utterances for debugging.",
    )
    parser.add_argument(
        "--queue-warn",
        type=int,
        default=80,
        help="Frame queue size that triggers backlog warnings (20 ms per frame).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Number of background Whisper worker threads.",
    )
    parser.add_argument(
        "--max-pending",
        type=int,
        default=5,
        help="Maximum pending utterances before cancelling the oldest.",
    )
    parser.add_argument(
        "--file",
        help="Optional WAV file for testing instead of mic input.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug logging.",
    )

    args = parser.parse_args()

    configure_logging(args.debug)

    if args.file:
        run_file(args)
    else:
        run_live(args)


if __name__ == "__main__":
    main()