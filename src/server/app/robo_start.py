import threading
import time
import paramiko
import sys

class RobotSSHController:
    def __init__(self, serverIP, host="192.168.0.145", user="jetson", password=None):
        self.IP = serverIP
        self.ssh_client = None
        self.ssh_channel = None
        self.ssh_target = f"{user}@{host}"
        self.host = host
        self.user = user
        self.password = password
        self.thread = None
        self.running = False
        self.ready = threading.Event()  # <-- SIGNAL wenn Verbindung steht

    def start_robot(self):
        remote_cmd = (
            "source spino-main/spino_venv/bin/activate && "
            f"python3 spino-main/src/robo/main/main.py {self.IP}"
        )

        try:
            print("Connecting via Paramiko SSH…")

            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            self.ssh_client.connect(
                hostname=self.host,
                username=self.user,
                password=self.password,
                allow_agent=False,
                look_for_keys=False,
                timeout=10
            )

            print("SSH connected!")

            # Startet den Befehl auf dem Jetson
            self.ssh_channel = self.ssh_client.get_transport().open_session()
            self.ssh_channel.exec_command(remote_cmd)

            # Signal: Verbindung steht!
            self.ready.set()

        except Exception as e:
            print("SSH ERROR:", e)
            self.ready.set()  # Verhindert Deadlocks
            return

    def stop_robot(self):
        self.running = False
        if self.ssh_channel:
            self.ssh_channel.close()
        if self.ssh_client:
            self.ssh_client.close()
        print("SSH connection closed.")

    def _worker(self):
        self.start_robot()
        print("Robot started via SSH.")

        while self.running:
            if self.ssh_channel.recv_ready():
                line = self.ssh_channel.recv(1024).decode("utf-8")
                if line:
                    print("\033[33m[ROBOT]\033[0m", line, end="")

            if self.ssh_channel.recv_stderr_ready():
                line = self.ssh_channel.recv_stderr(1024).decode("utf-8")
                if line:
                    print("\033[31m[ROBOT-ERR]\033[0m", line, end="")

            # Wenn Channel komplett tot → neu verbinden oder raus
            if self.ssh_channel.closed or self.ssh_channel.exit_status_ready():
                print("SSH channel closed.")
                break

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
