from connection import connectionHändler

conn = connectionHändler.getInstance()

while True:
    print("HelloWorld!")
    scan = conn.getLidar()
    print(scan)


