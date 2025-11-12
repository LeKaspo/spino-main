import asyncio

async def handle_client(self, reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"connection from {addr}")
    try:
        while data := await reader.readline():
           print(f"[{addr}] {data.decode().strip()}")
    except asyncio.cancelledError:
        pass
    finally:
        print("Verbindung geschlossen")
        writer.close()
        await writer.wait_closed()

async def main():
      server = await asyncio.start_server(handle_client, '0.0.0.0', 9999)
      print("Server läuft auf Port 9999")
      async with server:
            await server.serve_forever()

asyncio.run(main())