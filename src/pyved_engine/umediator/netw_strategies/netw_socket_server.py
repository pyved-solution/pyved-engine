"""
on expose
---------

- get_server_flag() -> int

- start_comms(host_info, port_info)

- broadcast(evtype, evcontent) -> None

- register_mediator( obj ) où obj est un objet respectant l'interface de UMediator. CAR on call mediator.post( x, y, z)

"""
import json
import socket
import threading
import time


mediators = list()
inbound_connections = list()
ref_threads = list()
socket_ref = None
shutdown_flag = False

__all__ = [
    'get_server_flag',
    'start_comms',
    'broadcast',
    'register_mediator'
]


def get_server_flag():
    return 1


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
    global ref_threads, socket_ref, shutdown_flag

    def handle_client(socklisten):
        global inbound_connections, mediators

        while not shutdown_flag:
            try:
                conn, addr = socklisten.accept()  # blocking call, but can be interrupted by timeout
                inbound_connections.append(conn)
                print(f'Connection added, source:{addr}')
                with conn:
                    while not shutdown_flag:
                        data = conn.recv(1024)
                        if not data:
                            print('error receiving data')
                            break
                        txt_info = data.decode()
                        partie_reception(txt_info)
            except socket.timeout:
                # Timeout triggered, just check if shutdown is needed
                time.sleep(0.1)  # Add a small delay to prevent 100% CPU usage
            except Exception as e:
                print(f"Error handling client: {e}")
                break

    given_socket_config = host_info, port_info
    socket_ref = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_ref.bind(given_socket_config)
    print('start to listen on:', host_info, port_info)
    socket_ref.listen()

    # Set timeout for accept() so we can handle shutdown properly
    socket_ref.settimeout(1)  # Timeout set to 1 second

    # start 2 threads no matter what,
    # and keep a ref/ptr for later use
    for _ in range(2):
        nt = threading.Thread(target=handle_client, args=(socket_ref,))
        nt.start()
        ref_threads.append(nt)


def broadcast(event_type, event_content):
    global inbound_connections
    # emit to clientS
    data = f'{event_type}#{event_content}'
    broken_c = set()
    for client in inbound_connections:
        try:  # to avoid server crashing if one connection is down -> other clients still play
            client.sendall(data.encode())
        except Exception as err:
            print('!!connection err!!', err)
            broken_c.add(client)

    for c in broken_c:
        inbound_connections.remove(c)
        print(' A connexion has just dropped')


def register_mediator(x):
    global mediators
    mediators.append(x)


def shutdown_comms():
    global inbound_connections, ref_threads

    global shutdown_flag
    shutdown_flag = True  # Set shutdown flag to true

    # Step 1: Close all inbound connections
    for conn in inbound_connections:
        try:
            conn.close()
            print(f'Closed connection: {conn}')
        except Exception as err:
            print(f'Error closing connection {conn}: {err}')
    inbound_connections.clear()
    print('connections gone ok')

    # Step 2: Exit all threads
    for thread in ref_threads:
        try:
            thread.join()  # Ensures the thread has finished before proceeding
            print(f'Thread {thread} has been joined')
        except Exception as err:
            print(f'Error stopping thread {thread}: {err}')
    ref_threads.clear()
    print('threads cleared ok')

    # Step 3: don't listen anymore that is: closing socket
    socket_ref.close()
    print('socket-based server: everything went down->ok')
