import subprocess
import time
import sys


class RobotSSHController:

    def __init__(self, host="192.168.0.145", user="jetson", password="12345678"):
        self.ssh_proc = None
        self.ssh_target = f"{user}@{host}"
        self.password = password

    def start_robot(self):
        # SSH-Kommandokette vorbereiten
        remote_cmd = (
            "source /home/spino-main/spino-venv/bin/activate && "
            "python3 /home/spino-main/src/robo/main/main.py"
        )

        # SSH starten
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
        if self.ssh_proc:
            print("Stopping robot...")
            self.ssh_proc.terminate()
            try:
                self.ssh_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ssh_proc.kill()
            print("SSH connection closed.")

    def run(self):
        try:
            self.start_robot()
            print("Robot started via SSH.")

            while True:
                line = self.ssh_proc.stdout.readline()
                if line:
                    print("[ROBOT]", line, end="")
                time.sleep(0.1)

        except KeyboardInterrupt:
            pass

        finally:
            self.stop_robot()