"""
Module for recording a video stream (e.g., MJPEG) to a buffer and saving it to disk.
"""

import cv2
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional

# Default configuration
DEFAULT_STREAM_URL = "http://192.168.0.145:8090/?action=stream"
DEFAULT_BUFFER_DURATION = 30
DEFAULT_FPS = 30


class StreamRecorder:
    """
    Records a video stream to a circular buffer and allows saving the buffer to a file.
    """

    def __init__(self, stream_url: str | int, buffer_duration: int = DEFAULT_BUFFER_DURATION, fps: int = DEFAULT_FPS):
        """
        Initialize the recorder.

        Args:
            stream_url: The URL of the MJPEG stream or device index (0 for webcam).
            buffer_duration: How many seconds of video to keep in memory.
            fps: The expected framerate of the stream.
        """
        self.stream_url = stream_url
        self.fps = fps
        self.buffer_duration = buffer_duration
        self.max_frames = buffer_duration * fps
        
        # Deque automatically discards the oldest items when full
        self.frame_buffer = deque(maxlen=self.max_frames)
        
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

    def start(self):
        """Starts the background recording thread."""
        if self.running:
            print("Recorder is already running.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._record_loop, name="StreamRecorderThread", daemon=True)
        self.thread.start()
        print(f"Started recording stream from {self.stream_url}")

    def _record_loop(self):
        """Internal loop to capture frames."""
        while self.running:
            cap = cv2.VideoCapture(self.stream_url)
            
            if not cap.isOpened():
                print(f"Warning: Could not open video stream at {self.stream_url}. Retrying in 5 seconds...")
                time.sleep(5)
                continue

            print("Stream connected successfully. Buffering frames...")

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    print("Warning: Lost connection to stream. Reconnecting...")
                    break
                
                with self.lock:
                    self.frame_buffer.append(frame)
                    
            cap.release()
            
        print("Stream capture thread stopped.")

    def save_last_seconds(self, output_filename: Optional[str] = None, output_dir: str = "recordings"):
        """
        Saves the current buffer to a file.

        Args:
            output_filename: Name of the output file. If None, a timestamped name is generated.
            output_dir: Directory to save the file in. Defaults to "recordings".
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"recording_{timestamp}.mp4"

        full_path = output_path / output_filename

        with self.lock:
            # Create a snapshot of the buffer to write to disk
            # This minimizes the time we hold the lock
            frames_to_write = list(self.frame_buffer)

        if not frames_to_write:
            print("Buffer is empty, nothing to save.")
            return

        print(f"Saving {len(frames_to_write)} frames to {full_path}...")
        
        # Get dimensions from the first frame
        height, width, _ = frames_to_write[0].shape
        size = (width, height)
        
        # 'mp4v' is a widely supported codec for .mp4
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(full_path), fourcc, self.fps, size)

        for frame in frames_to_write:
            out.write(frame)
            
        out.release()
        print(f"Saved successfully to {full_path}")

    def stop(self):
        """Stops the recording thread."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        print("Recorder stopped.")


# Singleton instance
_recorder_instance: Optional[StreamRecorder] = None


def get_recorder() -> StreamRecorder:
    """
    Returns the singleton instance of the StreamRecorder.
    Creates it if it doesn't exist.
    """
    global _recorder_instance
    if _recorder_instance is None:
        _recorder_instance = StreamRecorder(
            DEFAULT_STREAM_URL, 
            buffer_duration=DEFAULT_BUFFER_DURATION, 
            fps=DEFAULT_FPS
        )
    return _recorder_instance


if __name__ == "__main__":
    # If the robot is not online, you can change this to 0 to use your local webcam for testing
    # STREAM_URL = 0 
    
    recorder = StreamRecorder(DEFAULT_STREAM_URL, buffer_duration=30, fps=30)
    recorder.start()

    print("\n--- Video Buffer Test ---")
    print("Type 'save' to save the last 30 seconds.")
    print("Type 'q' to quit.")

    try:
        while True:
            cmd = input("> ").strip().lower()
            if cmd == 'save':
                recorder.save_last_seconds()
            elif cmd == 'q':
                break
    except KeyboardInterrupt:
        pass
    finally:
        recorder.stop()

