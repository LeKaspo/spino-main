from server.connection import connectionHändler

conn = connectionHändler.getInstance()

while True:
    scan = conn.getLidar()
    print(scan)


