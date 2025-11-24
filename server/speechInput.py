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
import os
import queue
import subprocess
import sys
import tempfile
import time

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
                voicecommand(cmd["name"])
                return



# -------------------- Main logic --------------------


def transcribe_utterance(wmodel, samples_bytes: bytes, language: str) -> str:
    """Save samples to WAV, run Whisper, return transcribed text."""
    wavpath = None
    try:
        wavpath = save_temp_wav(samples_bytes)
        print("Transcribing utterance...")
        # language is 'de' or 'en'
        res = wmodel.transcribe(wavpath, language=language)
        text = res.get("text", "").strip()
        return text
    finally:
        if wavpath and os.path.exists(wavpath):
            try:
                os.remove(wavpath)
            except Exception:
                pass


def run_live(args):
    recorder = Recorder()
    vad = webrtcvad.Vad(2)  # 0-3 (aggressiveness); 2 is reasonable

    print("Loading Whisper model:", args.model)
    wmodel = whisper.load_model(args.model)

    recorder.start()
    print(f"Listening (language={args.language}). Press Ctrl-C to stop.")

    frame_buffer = []
    speech = False
    silence_frames = 0
    silence_ms_threshold = args.silence_ms

    try:
        while True:
            try:
                frame = recorder.frames_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            is_speech = vad.is_speech(frame, SAMPLE_RATE)
            if is_speech:
                frame_buffer.append(frame)
                speech = True
                silence_frames = 0
            else:
                if speech:
                    silence_frames += 1
                    if silence_frames * FRAME_DURATION_MS > silence_ms_threshold:
                        # End of utterance
                        samples = b"".join(frame_buffer)
                        frame_buffer = []
                        speech = False
                        silence_frames = 0

                        if not samples:
                            continue

                        text = transcribe_utterance(wmodel, samples, args.language)
                        if not text:
                            print("Empty transcription, ignoring.")
                        else:
                            print("Transcript:", text)
                            check_commands(text)
                # else: just silence without active speech -> ignore
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        recorder.stop()


def run_file(args):
    """Optional: process a WAV file instead of microphone (for quick testing)."""
    vad = webrtcvad.Vad(2)
    print("Loading Whisper model:", args.model)
    wmodel = whisper.load_model(args.model)
    print("Processing file:", args.file)

    frame_buffer = []
    speech = False
    silence_frames = 0

    for frame in frames_from_wav(args.file):
        is_speech = vad.is_speech(frame, SAMPLE_RATE)
        if is_speech:
            frame_buffer.append(frame)
            speech = True
            silence_frames = 0
        else:
            if speech:
                silence_frames += 1
                if silence_frames * FRAME_DURATION_MS > args.silence_ms:
                    samples = b"".join(frame_buffer)
                    frame_buffer = []
                    speech = False
                    silence_frames = 0

                    if not samples:
                        continue

                    text = transcribe_utterance(wmodel, samples, args.language)
                    if not text:
                        print("Empty transcription, ignoring.")
                    else:
                        print("Transcript:", text)
                        check_commands(text)
            # else: silence without active speech -> ignore

    # left-over partial utterance
    if frame_buffer:
        samples = b"".join(frame_buffer)
        text = transcribe_utterance(wmodel, samples, args.language)
        if text:
            print("Transcript (last):", text)
            check_commands(text)


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
        "--silence-ms",
        type=int,
        default=400,
        help="Milliseconds of silence to treat as end-of-utterance.",
    )
    parser.add_argument(
        "--file",
        help="Optional WAV file for testing instead of mic input.",
    )

    args = parser.parse_args()

    if args.file:
        run_file(args)
    else:
        run_live(args)


if __name__ == "__main__":
    main()
