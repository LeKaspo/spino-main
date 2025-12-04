import subprocess
import time
import threading


class RobotSSHController:

    def __init__(self, host="192.168.0.145", user="jetson", password="12345678"):
        self.ssh_proc = None
        self.ssh_target = f"{user}@{host}"
        self.password = password
        self.thread = None
        self.running = False

    def start_robot(self):
        remote_cmd = (
            "source /home/spino-main/spino-venv/bin/activate && "
            "python3 /home/spino-main/src/robo/main/main.py"
        )

        self.ssh_proc = subprocess.Popen(
            [   
                "sshpass", "-p", self.password,
                "ssh", "-o", "StrictHostKeyChecking=no",
                self.ssh_target,
                remote_cmd
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    def stop_robot(self):
        self.running = False
        if self.ssh_proc:
            print("Stopping robot...")
            self.ssh_proc.terminate()
            try:
                self.ssh_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ssh_proc.kill()
            print("SSH connection closed.")

    def _worker(self):
        self.start_robot()
        print("Robot started via SSH.")

        while self.running and self.ssh_proc:
            line = self.ssh_proc.stdout.readline()
            if line:
                print("[ROBOT]", line, end="")
            time.sleep(0.05)

        self.stop_robot()

    def run(self):
        if self.thread and self.thread.is_alive():
            print("Robot thread already running!")
            return

        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        print("SSH thread started.")