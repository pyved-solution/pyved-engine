"""
implementation that works fine, only problem is that it looks like
we cannot implement the graceful exit just right...In the meantime its
not that bad, we will find a solution someday
"""
# TODO: fin solution for graceful exit

import asyncio
import json

import websockets


# Global variables
connections = set()
mediators = []
loop = None  # Keep a reference to the event loop for proper shutdown
executor_tasks = []  # Keep track of tasks running in executor


async def partie_reception(websocket, message):
    print(f'Received: {message}')
    try:
        parts = message.split('#')
        evtype = parts[0]
        content = parts[1]
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
    async with websockets.serve(handle_client, host_info, port_info):
        print(f"WebSocket server started on ws://{host_info}:{port_info}")
        await asyncio.Future()  # Keep the server running indefinitely


def start_comms(host_i, port_i):
    global loop
    print('host_i:', host_i, 'port_i:', port_i)

    # won't work because blocking the main event loop, so we cannot tick and tac
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(_server_start(host_i, port_i))

    print('host_i:', host_i, 'port_i:', port_i)
    loop = asyncio.get_event_loop()

    # Run the WebSocket server in an executor, means not blocking the existing event loop
    #loop.run_in_executor(None, asyncio.run, _server_start(host_i, port_i))

    # run_blocking_in_executor(blocking_task):
    task = loop.run_in_executor(None, asyncio.run, _server_start(host_i, port_i))  # Run a blocking task in executor
    print("Executor task is running in the background")
    executor_tasks.append(task)  # Track the task


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


def register_mediator(mediator):
    global mediators
    mediators.append(mediator)


# fixing this:

# def shutdown_comms():
#     print("Shutting down WebSocket server...")
#     for ws in connections:
#         try:
#             ws.close()
#         except Exception as e:
#             print(f"Error closing connection: {e}")
#     connections.clear()
#     print("Server shutdown complete.")

# with this:


async def close_connections():
    """Close all WebSocket connections gracefully."""
    for ws in connections:
        try:
            await ws.close()  # This sends a close frame to the client
            print(f"Closed connection from {ws.remote_address}")
        except Exception as e:
            print(f"Error closing connection from {ws.remote_address}: {e}")


async def _stop_server():
    """Stops the WebSocket server."""
    print("Stopping WebSocket server...")
    await close_connections()  # Close all active connections
    print("All connections closed.")


def shutdown_comms():
    """Shutdown WebSocket communications."""
    global loop
    print("Shutting down WebSocket server...")
    loop.create_task(_stop_server())  # Schedule the server shutdown

    # Wait for all tasks to complete (and shut down the event loop)
    loop.run_until_complete(loop.shutdown_asyncgens())  # Ensure async generators are closed

    # Stop the event loop and wait for the executor tasks to finish
    loop.stop()  # Stop the event loop
    print("Server shutdown complete.")


# Function to wait for all executor tasks to finish
async def shutdown_executor_tasks():
    print("Waiting for all executor tasks to finish...")
    # Wait for all executor tasks to complete
    await asyncio.gather(*executor_tasks)
    print("All executor tasks completed.")


def get_server_flag():
    return 1
