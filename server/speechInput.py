"""
Continuous speech -> Whisper (de/en) -> command execution.

- Listens to the default microphone with WebRTC VAD.
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

import numpy as np
import sounddevice as sd
import soundfile as sf
import webrtcvad
from scipy import signal

# Whisper: make sure this is openai-whisper
try:
    import whisper
except Exception as e:
    print("Failed to import the 'whisper' module:", e, file=sys.stderr)
    print("Install it with: pip install -U openai-whisper", file=sys.stderr)
    sys.exit(1)

from sendcommands import voicecommand

logger = logging.getLogger("speechInput")

SAMPLE_RATE = 16000
FRAME_DURATION_MS = 20  # 10/20/30 ms allowed for WebRTC VAD
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)


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
            "fahre geradeaus",
            "fahre vorwärts",
            "fahre nach vorne",
        ]
    },
    {
        "name": "backwards",
        "phrases": [   
            "move backward",
            "go backward",
            "fahre rückwärts",
            "fahre nach hinten",
        ]
    },
    {
        "name": "left",
        "phrases": [
            "turn left",
            "go left",
            "fahre nach links",
            "biege links ab",
        ]
    },
    {
        "name": "right",
        "phrases": [
            "turn right",
            "go right",
            "fahre nach rechts",
            "biege rechts ab",
        ]
    },
    {
        "name": "fullstop",
        "phrases": [
            "stop",
            "halt",
            "wait",
            "stopp",
            "anhalten",
            "warte",
            "stoppe"
        ]
    },
    {
        "name": "turnLeft",
        "phrases": [
            "rotate left",
            "turn around left",
            "spin left",
            "look to the left",
            "look left"
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


def check_commands(transcript: str):
    """Case-insensitive substring match of command phrases in the transcript."""
    text = transcript.lower()
    for cmd in COMMANDS:
        for phrase in cmd["phrases"]:
            if phrase.lower() in text:
                logger.info("Command triggered: %s via phrase '%s'", cmd["name"], phrase)
                voicecommand(cmd["name"])
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
        res = wmodel.transcribe(wavpath, language=language)
        text = res.get("text", "").strip()
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


def run_live(args):
    recorder = Recorder()
    vad = webrtcvad.Vad(args.vad_aggressiveness)

    logger.info("Loading Whisper model: %s", args.model)
    wmodel = whisper.load_model(args.model)

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
    vad = webrtcvad.Vad(args.vad_aggressiveness)
    logger.info("Loading Whisper model: %s", args.model)
    wmodel = whisper.load_model(args.model)
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
        "--language",
        choices=["de", "en"],
        default="de",
        help="Language for Whisper transcription (de or en)",
    )
    parser.add_argument(
        "--vad-aggressiveness",
        type=int,
        choices=[0, 1, 2, 3],
        default=2,
        help="WebRTC VAD aggressiveness (0 = least, 3 = most aggressive).",
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
        default=500.0,
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
        default=1,
        help="Number of background Whisper worker threads.",
    )
    parser.add_argument(
        "--max-pending",
        type=int,
        default=2,
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
