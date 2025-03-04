import json
import socket
import threading


class NetworkLayer:
    def __init__(self, server_flag: int):
        self._mediators = list()
        assert(isinstance(server_flag, int) and -1 < server_flag < 2)
        self._server_flag = server_flag

        # client
        self.socket_remote_host = None
        self.receiver_thread = None
        # server
        self.inbound_connections = list()
        self.ref_threads = list()

    def register_mediator(self, mediator):
        self._mediators.append(mediator)

    def start_comms(self, host_info, port_info):
        given_socket_config = host_info, port_info

        if self._server_flag:
            so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            so.bind(given_socket_config)
            so.listen()
            for _ in range(2):
                given_thread = threading.Thread(target=self.handle_client, args=(so,))
                given_thread.start()
            print(f'Server ready! Config: {host_info}:{port_info}...')
            print('mediators:', self._mediators)
        else:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_remote_host = s_obj
            self.socket_remote_host.connect(given_socket_config)
            receiver_thread = threading.Thread(target=self.cli_receives_updates, args=(s_obj, self._mediators))
            receiver_thread.start()

    def get_server_flag(self):
        return self._server_flag

    # -----------------------------
    #  client side
    # -----------------------------
    def cli_receives_updates(self, clisocket, li_media):
        # ev_manager = EvManager.instance()
        while True:
            data = clisocket.recv(1024)
            if not data:
                break
            msg_payload = data.decode()
            print(' client recoit update:', msg_payload)
            print(len(li_media))
            parts = msg_payload.split('#')
            evtype = parts[0]
            evcontent = parts[1]
            for mee in li_media:
                mee.post(evtype, evcontent, False)

    def shutdown_comms(self):
        if self._server_flag:
            # server is shutting down comms
            for connection in self.inbound_connections:
                connection.close()
            self.ref_threads.join()
        else:
            # client is shutting down comms
            if self.receiver_thread:
                self.receiver_thread.join()
            if self.socket_remote_host:
                self.socket_remote_host.close()

    def send_rawtext(self, x):
        self.socket_remote_host.sendall(x.encode())
        print('NetworkLayer transmet sur socket....', x)

    # CI-DESSOUS DES RESTES

    # qu'etaient rattachés à la fonction:
    # <  def cli_broadcast(self, event_type, event)  >

    # target_mtype : who we target 1 to target the server
    # for a_mediator in self._mediators:
    #    if a_mediator.server_side_flag() == target_mtype:
    #        a_mediator.post(event_type, event, enable_event_forwarding=False)

    # def send_special_event(self, event_type, event, source_mediator):
    #     message = process_data(event_type, event)
    #     # Call JavaScript function to send data
    #     print('netw layer pushing::', message)
    #     __pragma__('js', '{}', 'sendToClients')(message)
    #
    # def inject_packed_ev(self, serialized_event):
    #     tmp = serialized_event.split('#')
    #     evtype = tmp[0]
    #     evcontent = json_loads(tmp[1])
    #     for m in self.mediators:
    #         m.post(evtype, evcontent, False)

    # -----------------------------
    #  server side
    # -----------------------------
    def handle_client(self, socklisten):
        conn, addr = socklisten.accept()  # blocking call
        self.inbound_connections.append(conn)
        with conn:
            print(f'Connection added, source:{addr}')
            # conn.send('hello'.encode())
            while True:
                data = conn.recv(1024)
                if not data:
                    print('error receiving data')
                    break
                txt_info = data.decode()
                print(f'reception:{txt_info}')

                # unpack event & transmit to mediators
                parts = txt_info.split('#')
                evtype = parts[0]
                content = json.loads(parts[1])
                print('handle client fait le passage a un/des mediator(s) count:', len(self._mediators))
                for m in self._mediators:
                    m.post(evtype, content, False)

    def broadcast(self, event_type, event_content):
        emit_to_what = self._server_flag ^ 1  # flip the flag

        if 0 == emit_to_what:  # emit to clientS
            data = f'{event_type}#{event_content}'
            broken_c = set()
            for client in self.inbound_connections:
                try:  # to avoid server crashing if one connection is down -> other clients still play
                    client.sendall(data.encode())
                except Exception as err:
                    print('!!connection err!!', err)
                    broken_c.add(client)

            for c in broken_c:
                self.inbound_connections.remove(c)
                print(' A connexion has just dropped')
            return

        if 1 == emit_to_what:  # emit to server
            json_str = json.dumps(event_content)
            serial = f'{event_type}#{json_str}'
            self.send_rawtext(serial)
            return

        raise ValueError
