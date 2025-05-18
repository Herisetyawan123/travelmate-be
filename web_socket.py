import asyncio
import json
from aiohttp import web
import websockets

clients = set()

async def websocket_handler(websocket):
    print("Client connected")
    clients.add(websocket)

    try:
        async for message in websocket:
            data = json.loads(message)
            print("Received:", data)
            # Broadcast ke semua client kecuali sender
            for client in clients:
                if client != websocket:
                    await client.send(json.dumps({
                        "event": "broadcast",
                        "data": data
                    }))
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        clients.remove(websocket)

# HTTP handler untuk menerima POST /trigger
async def trigger(request):
    try:
        data = await request.json()
        print("Trigger received:", data)

        # Broadcast ke semua client WebSocket
        message = json.dumps({
            "event": data.get("event", "triggered"),
            "data": data
        })

        for client in clients.copy():
            try:
                await client.send(message)
            except:
                clients.remove(client)

        return web.json_response({"status": "ok"})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def main():
    # start websocket server
    ws_server = await websockets.serve(websocket_handler, "localhost", 8001)

    # start aiohttp http server
    app = web.Application()
    app.router.add_post('/trigger', trigger)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8002)
    await site.start()

    print("WebSocket server running on ws://localhost:8001")
    print("HTTP trigger server running on http://localhost:8002/trigger")

    # Run forever
    await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
