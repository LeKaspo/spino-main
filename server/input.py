import asyncio
import keyboard

async def send_input():
    reader, writer = await asyncio.open_connection(HOST, 9999)
    print("verbunden")
    try:
        while True:
            msg = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            writer.write((msg + "\n").encode())
            await writer.drain()
    except KeyboardInterrupt:
        print("unterbrochen")
    finally:
        writer.close()
        await writer.wait_closed()

asyncio.run(send_input)


