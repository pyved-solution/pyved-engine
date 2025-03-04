"""
on expose
---------

- get_server_flag() -> int

- start_comms(host_info, port_info)

- broadcast(evtype, evcontent) -> None

- register_mediator( obj ) où obj est un objet respectant l'interface de UMediator. CAR on call mediator.post( x, y, z)

"""
import socket
import threading
import json


mediators = list()
inbound_connections = list()
ref_threads = list()

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
    def handle_client(socklisten):
        global inbound_connections, mediators
        conn, addr = socklisten.accept()  # blocking call
        inbound_connections.append(conn)
        with conn:
            print(f'Connection added, source:{addr}')
            # conn.send('hello'.encode())
            while True:
                data = conn.recv(1024)
                if not data:
                    print('error receiving data')
                    break
                txt_info = data.decode()
                partie_reception(txt_info)

    given_socket_config = host_info, port_info
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.bind(given_socket_config)
    print('start to listen on:', host_info, port_info)
    so.listen()
    for _ in range(2):
        given_thread = threading.Thread(target=handle_client, args=(so,))
        given_thread.start()


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
    pass  # TODO
