"""
this is supposed to contain the implementation
of a network layer (server-side) that uses websocket
for transporting game events (special cross events only)
"""
import asyncio
import websockets
import json

mediators = []
connections = set()

__all__ = [
    'get_server_flag',
    'start_comms',
    'broadcast',
    'register_mediator'
]


def get_server_flag():
    return 1


async def partie_reception(websocket, message):
    print(f'Received: {message}')
    try:
        parts = message.split('#')
        evtype = parts[0]
        content = json.loads(parts[1])
    except (IndexError, json.JSONDecodeError) as e:
        print('Error parsing message:', e)
        return

    print(f'Transmitting to mediators ({len(mediators)} registered)')
    for m in mediators:
        m.post(evtype, content, False)


async def handle_client(ws_obj):
    global connections
    connections.add(ws_obj)
    print(f'New connection from {ws_obj.remote_address}')
    try:
        async for message in ws_obj:
            await partie_reception(ws_obj, message)

    except websockets.exceptions.ConnectionClosed as e:
        print(f'Connection closed: {ws_obj.remote_address} ({e})')
    finally:
        connections.remove(ws_obj)
        print('A connection has dropped')


async def _server_start(host_info, port_info):
    """Starts the WebSocket server."""
    # host, port = "localhost", 8765
    async with websockets.serve(handle_client, host_info, port_info):
        print(f"WebSocket server started on ws://{host_info}:{port_info}")
        await asyncio.Future()  # Keep the server running indefinitely


def start_comms(host_i, port_i):
    print('host_i:', host_i, 'port_i:', port_i)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_server_start(host_i, port_i))


async def async_broadcast(event_type, event_content):
    global connections
    data = f'{event_type}#{json.dumps(event_content)}'
    broken_connections = set()
    for ws in connections:
        try:
            await ws.send(data)
        except Exception as err:
            print('!! Connection error !!', err)
            broken_connections.add(ws)
    for ws in broken_connections:
        connections.remove(ws)
        print('A connection has dropped')


def broadcast(event_type, event_content):
    asyncio.run(async_broadcast(event_type, event_content))


def register_mediator(x):
    global mediators
    mediators.append(x)


def shutdown_comms():
    pass  # TODO
