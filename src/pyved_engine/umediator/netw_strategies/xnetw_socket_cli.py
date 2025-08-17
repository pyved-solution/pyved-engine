"""
Régle du jeu :
y a une >INTERFACE COMMUNE< à tous les fichiers netw_*


Ainsi, on doit exposer
----------------------

- get_server_flag() -> int

- start_comms(host_info, port_info)

- broadcast(evtype, evcontent) -> None

- register_mediator( obj ) où obj est un objet respectant l'interface de UMediator. CAR on call mediator.post( x, y, z)
  cela modifie effectivement l'état du NetworkLayer qui ne se réduit donc pas un paquet de methodes statiques


"""
import json
import threading
import time
import socket

__all__ = [
    'get_server_flag',
    'start_comms',
    'broadcast',
    'register_mediator'
]

mediators = []

ref_socket = None
_receiver_thread = None
_stop_event = threading.Event()


def get_server_flag():
    return 0


def ws_on_message(message):
    global mediators
    print(f'Received shared variable update: {message}')
    try:
        evtype, content = message.split('#', 1)
        content = json.loads(content)
    except (ValueError, json.JSONDecodeError) as e:
        print(f'Error parsing message: {e}')
        return

    print(f'Passed to {len(mediators)} mediators')
    for m in mediators:
        m.post(evtype, content, False)


def _receive_updates(host_info, port_info):
    global ref_socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host_info, port_info))
        ref_socket = s
        print("Socket connection established")
        try:
            while True:
                data = s.recv(1024)
                if not data:
                    break
                message = data.decode()
                ws_on_message(message)
        except Exception as e:
            print(f"Socket error: {e}")
        finally:
            print("Socket connection closed")
            ref_socket = None


# def start_comms(host_info, port_info):
#     global _receiver_thread, ref_socket
#     _receiver_thread = threading.Thread(target=_receive_updates, args=(host_info, port_info), daemon=True)
#     _receiver_thread.start()
#
#     while ref_socket is None:
#         time.sleep(0.1)
def start_comms(host_info, port_info):
    global _receiver_thread, ref_socket, _stop_event
    _stop_event.clear()
    _receiver_thread = threading.Thread(target=_receive_updates, args=(host_info, port_info))
    _receiver_thread.start()

    # Attendre que la connexion socket soit établie (avec un timeout)
    timeout = 5  # secondes
    start_time = time.time()
    while ref_socket is None and time.time() - start_time < timeout:
        time.sleep(0.1)
    if ref_socket is None:
        print("Failed to establish socket connection within timeout.")



def broadcast(event_type, event_content):
    global ref_socket
    if not ref_socket:
        print("No active socket connection")
        return
    if event_content is None:
        event_content = 'null'
    richmsg = f'{event_type}#{json.dumps(event_content)}'
    try:
        ref_socket.sendall(richmsg.encode())
    except Exception as e:
        print(f"Error sending data: {e}")


def register_mediator(x):
    global mediators
    mediators.append(x)


def shutdown_comms():
    global ref_socket, _receiver_thread, _stop_event
    _stop_event.set()
    if ref_socket:
        try:
            ref_socket.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            print(f"Error during socket shutdown: {e}")
        try:
            ref_socket.close()
        except Exception as e:
            print(f"Error closing socket: {e}")
        ref_socket = None
    if _receiver_thread:
        _receiver_thread.join()
        _receiver_thread = None
    print("Communication shutdown complete.")
