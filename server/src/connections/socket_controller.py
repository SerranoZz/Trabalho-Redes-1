
import socket
from threading import Thread

from src.decode.message_decode import MessageDecode
from src.decode.message_decode import Status
from src.game.game_match import GameMatch


class KeepAliveThread:
    def __init__(self, conn, addr, player_id, socket_controller):
        self._conn = conn
        self._addr = addr
        self._player_id = player_id
        self._socket_c = socket_controller
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        print(f"Client {self._addr} connected")

        with self._conn:
            self._conn.settimeout(120)
            while self._running:
                try:
                    data = self._conn.recv(2048)
                    if not data:
                        break

                    message = data.decode("utf-8")
                    self._socket_c.decode_message(self._conn, self._player_id, message)
                except Exception as e:
                    print(e)
            self._conn.close()

            print(f"Client {self._addr} disconnected")


class ListenThread:
    def __init__(self, socket_controller):
        self._socket_c = socket_controller
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self._socket_c.get_host(), self._socket_c.get_port()))
            print(f"Server listening in {self._socket_c.get_host()}:{self._socket_c.get_port()}")

            while self._running:
                sock.listen()
                conn, addr = sock.accept()
                self._socket_c.get_clients().append(conn)
                
                self._socket_c.update_state()

                player_id = len(self._socket_c.get_threads())
                keepalive_client = KeepAliveThread(conn, addr, player_id, self._socket_c)
                thread = Thread(target=keepalive_client.run)
                thread.daemon = True
                thread.start()

                self._socket_c.get_threads().append(keepalive_client)
                self._socket_c.ping_all()

            sock.close()


class SocketController:
    def __init__(self):
        self._server: ListenThread | None = None
        self._game_match: GameMatch | None = None
        self._decode: MessageDecode | None = None
        self._window: MainDialog | None = None
        self._server_port = 8096
        self._client_connections = []
        self._client_thread: list[KeepAliveThread] = []
        self._host = "127.0.0.1"

    def set_server_port(self, server_port):
        self._server_port = server_port

    def set_decode(self, decode, window):
        self._decode = decode
        self._window = window

    def set_game_match(self, game_match):
        self._game_match = game_match

    def get_host(self):
        return self._host

    def get_port(self):
        return self._server_port

    def get_threads(self):
        return self._client_thread
    
    def get_clients(self):
        return self._client_connections
    

    def stop_connection(self):
        print("Closing Server")
        for conn in self._client_connections:
            conn.sendall(str.encode("SERVER_CLOSED::= O server foi fechado!"))
        for thread in self._client_thread:
            thread.terminate()
        
        from src.interface.window import MainDialog

        self._client_connections = []
        self._client_thread = []
        self._window.set_game_match(GameMatch())
        self._window.prepare_to_init()
        print("End Game")

    def start_server(self):
        print("Starting Server")
        self._server = ListenThread(self)
        thread = Thread(target=self._server.run)
        thread.daemon = True
        thread.start()

    def ping_all_except(self, player_id):
        for index, conn in enumerate(self._client_connections):
            if index != player_id:
                self.ping(conn, index, self._game_match._wait)

    def alert_all(self):
        msg = F"END_GAME::= " + self._game_match.winners()
        for conn in self._client_connections:
            conn.sendall(str.encode(msg))

    def ping_all(self):
        for index, conn in enumerate(self._client_connections):
            self.ping(conn, index, self._game_match._wait)

    def ping(self, conn, player_id, wait):
        actual_player_id = self._game_match.get_actual_player()

        if(not wait):
            if player_id == actual_player_id:
                msg = f"YOUR_TURN::= "
                msg += self._game_match.table_str()
                msg += self._game_match.score_board_str()
                msg += self._game_match.choose_pieces()
                msg += self._game_match.pieces_result(player_id)
                msg += "Seu turno, por favor, especifique uma peça: "
            else:
                msg = "NOT_YOUR_TURN::= "
                msg += self._game_match.table_str()
                msg += self._game_match.score_board_str()
                msg += self._game_match.choose_pieces()
                msg += self._game_match.pieces_result(player_id)
                msg += f"Turno do jogador {actual_player_id + 1}"
        else:
            msg = "WAITING_PLAYERS::= Aguardando Jogadores..."

        conn.sendall(str.encode(msg))

    def decode_message(self, conn, player_id, message):
        status = self._decode.decode_message(player_id, message)

        if status == Status.VALID_MESSAGE:
            should_next = self._game_match.should_next()
            if should_next:
                self._game_match.next_player()

            self.ping(conn, player_id, self._game_match._wait)
            if not should_next:
                self.ping_all_except(player_id)

            if self._game_match.is_game_finish():
                self.alert_all()
                self.stop_connection()

            if should_next:
                self.ping_all_except(player_id)
        else:
            self.ping(conn, player_id, self._game_match._wait)

    def update_state(self):
        if(len(self._client_connections) == self._game_match.get_players()):
            self._game_match.set_wait(False)
        else:
            self._game_match.set_wait(True)
        

