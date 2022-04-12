import asyncio
import websockets
import time

async def server(ws, path):
    print('CONNECTED')
    while True:
        await ws.send(str(time.time()))
        time.sleep(1)

        message = await ws.recv()
        print(f'Msg [{message}]')

Server = websockets.serve(server, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(Server)
asyncio.get_event_loop().run_forever()