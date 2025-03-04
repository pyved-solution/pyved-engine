import json
import threading
import time

import websocket


__all__ = [
    'get_server_flag',
    'start_comms',
    'broadcast',
    'register_mediator'
]

mediators = list()
# inbound_connections = list()
ref_threads = list()

# old?
ref_ws = None
_receiver_thread = None

# ----------- private stuff --------------
def ws_on_message(ws, message):
    global mediators
    serial = message
    print(f'Received shared variable update: {serial}')
    evtype, content = serial.split('#')

    print('ws on message [[[[ ', evtype)
    print('ws on message <Content> ', content)
    k = len(mediators)
    print(f'passed to {k} mediators')
    for m in mediators:
        m.post(evtype, content, False)


def ws_on_error(ws, error):
    print(f"WebSocket error: {error}")


def ws_on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")


def ws_on_open(ws_handle):
    global ref_ws
    ref_ws = ws_handle
    print("WebSocket connection opened")


def _receive_updates(host_info, port_info):
    global ref_ws
    websocket.enableTrace(True)
    websocket.WebSocketApp(
        f'ws://{host_info}:{port_info}/',
        on_open=ws_on_open, on_message=ws_on_message, on_error=ws_on_error,
        on_close=ws_on_close
    ).run_forever()


def get_server_flag():
    return 0


def partie_reception(raw_txt):
    print(f'reception:{raw_txt}')
    # unpack event & transmit to mediators
    parts = raw_txt.split('#')
    evtype = parts[0]
    content = json.loads(parts[1])
    print('handle client fait le passage a un/des mediator(s) count:', len(mediators))
    for m in mediators:
        m.post(evtype, content, False)


def start_comms(host_info, port_info):
    global _receiver_thread, ref_ws
    _receiver_thread = threading.Thread(target=_receive_updates, args=(host_info, port_info))
    _receiver_thread.start()

    # because we wish to keep a sync program(not async)
    # we force the wait. this is effectively like typing 'await' in JS
    while ref_ws is None:
        time.sleep(0.1)


def broadcast(event_type, event_content):
    global ref_ws
    # emit to clientS
    if event_content is None:
        event_content = 'null'
    richmsg = f'{event_type}#{event_content}'
    ref_ws.send(richmsg.encode())


def register_mediator(x):
    global mediators
    mediators.append(x)


def shutdown_comms():
    global _receiver_thread, _client_socket
    if _receiver_thread:
        _receiver_thread.join()
    if client_socket:
        client_socket.close()

# -------------------------------------


#
# class NetwPusher(EvListener):
#     def on_netw_send(self, ev):
#         send_data((ev.evt+'#"'+ev.serial+'"').encode())  # after the sym #: you need to find real json format!!!
#
#     def on_exit_network(self, ev):
#         stop_network()
#
#     def turn_on(self):
#         super().turn_on()
#         start_client()
