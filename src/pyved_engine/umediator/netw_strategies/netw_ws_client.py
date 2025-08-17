import json
import threading
import websocket

# Global reference to the WebSocket
ref_ws = None
mediators = []

# Callback when a message is received
def ws_on_message(ws, message):
    global mediators
    print(f"Received shared variable update: {message}")
    try:
        evtype, raw_content = message.split('#', 1)
        content = json.loads(raw_content)
        print(f"Event: {evtype}, Content: {content}")
        # Pass message to mediators
        for m in mediators:
            m.post(evtype, content, False)
    except Exception as e:
        print(f"Error processing message: {e}")

def ws_on_error(ws, error):
    print(f"WebSocket error: {error}")

def ws_on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")


# def ws_on_open(ws):
#     global ref_ws
#     ref_ws = ws
#     print("WebSocket connection opened")

# Event to block the main thread until WebSocket is connected
ws_connected_event = threading.Event()

def ws_on_open(ws):
    global ref_ws
    ref_ws = ws
    print("WebSocket connection opened")
    # Signal that the WebSocket connection is established
    ws_connected_event.set()


def _run_client(host_info, port_info):
    url = f"ws://{host_info}:{port_info}"
    client_ws = websocket.WebSocketApp(
        url,
        on_message=ws_on_message,
        on_error=ws_on_error,
        on_close=ws_on_close,
        on_open=ws_on_open,
    )
    client_ws.run_forever()

def start_comms(host_info, port_info):
    # Run the WebSocket client in a separate thread to prevent blocking
    client_thread = threading.Thread(target=_run_client, args=(host_info, port_info))
    client_thread.start()

    # mecanisme de blocage volontaire:
    # Block until the WebSocket connection is successfully established
    print("Waiting for WebSocket connection...")
    ws_connected_event.wait()  # Block here until the connection is open
    print("WebSocket connection established and ready.")


def broadcast(event_type, event_content):
    global ref_ws
    if ref_ws is None:
        print("No active WebSocket connection")
        return
    if event_content is None:
        event_content = 'null'
    richmsg = f'{event_type}#{event_content}'
    ref_ws.send(richmsg)

def register_mediator(mediator):
    global mediators
    mediators.append(mediator)

def shutdown_comms():
    global ref_ws
    if ref_ws:
        ref_ws.close()  # Close the connection gracefully
        ref_ws = None

def get_server_flag():
    return 0
