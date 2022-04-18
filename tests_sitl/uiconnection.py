import asyncio
import websockets
import time
import threading

def UIThread(connection):
    connection.run()

class UIConnection:

    _sendQueue = []
    _lock = asyncio.Lock()
    _active = False

    def __init__(self):
        thread = threading.Thread(target=UIThread, args=(self,))
        thread.start()

        self._active = True

    async def msgHandler(self, websocket, path):
        sendTask = asyncio.create_task(self.sendHandler(websocket, path))
        receiveTask = asyncio.create_task(self.receiveHandler(websocket, path))

        await asyncio.wait([sendTask, receiveTask], return_when=asyncio.FIRST_COMPLETED)

    async def sendHandler(self, websocket, _):
        while True:
            await asyncio.sleep(0.05)

            async with self._lock:
                if len(self._sendQueue) == 0:
                    continue

                message = '\n'.join(self._sendQueue)

                try:
                    await websocket.send(message)
                except websockets.exceptions.ConnectionClosedOK:
                    print('connection closed during send')

                self._sendQueue = []

    async def receiveHandler(self, websocket, _):
        async for message in websocket:
            await self.printMsg(message)

    async def printMsg(self, msg):
        return
        print(msg)

    async def main(self):
        self.stop_event = threading.Event()
        stop = asyncio.get_event_loop().run_in_executor(None, self.stop_event.wait)

        async with websockets.serve(lambda websocket, path: self.msgHandler(websocket, path), '127.0.0.1', 5678):
            await stop

    def run(self):
        asyncio.run(self.main())

    def stop(self):
        self.stop_event.set()
        self._active = False

    def active(self):
        return self._active

    async def _send(self, json):
        async with self._lock:
            self._sendQueue.append(json)

    def send(self, json):
        asyncio.run(self._send(json))

if __name__ == '__main__':
    connection = UIConnection()

    while True:
        try:
            time.sleep(1)
        except:
            break

    connection.stop()