import time

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QIcon

from src.interface.labelled_input import LabelledIntField
from src.connections.socket_controller import SocketController
from src.game.game_match import GameMatch
from src.decode.message_decode import MessageDecode


class MainDialog(QDialog):
    def __init__(self, q_app):
        QDialog.__init__(self, parent=None)

        self._q_app = q_app
        self._socket_controller: SocketController | None = None
        self._decode: MessageDecode | None = None
        self._game_match: GameMatch | None = None
        self.port_div: LabelledIntField | None = None
        self.players_div: LabelledIntField | None = None
        self.table_size: LabelledIntField | None = None
        self.stop_button: QPushButton | None = None
        self.start_button: QPushButton | None = None

        self._players_size = 0
        self._table_size = 0
        self._server_port = 0

        self.setWindowTitle("TBM Server")
        self.setFixedSize(500, 150)

        v_layout = QVBoxLayout()
        self.setLayout(v_layout)

        self.add_int_inputs_panel(v_layout)
        v_layout.addStretch()
        self.add_button_panel(v_layout)

    def set_socket_controller(self, socket_controller):
        self._socket_controller = socket_controller

    def set_decode(self, decode):
        self._decode = decode
        self._socket_controller.set_decode(decode, self)

    def set_game_match(self, game_match):
        self._game_match = game_match
        self._decode.set_game_match(game_match)
        self._socket_controller.set_game_match(game_match)

    def add_int_inputs_panel(self, parent_layout):
        h_layout = QHBoxLayout()
        self.port_div = LabelledIntField("Porta", 8096)
        self.players_div = LabelledIntField("Jogadores", 2)
        self.table_size = LabelledIntField("Tamanho do Tabuleiro", 2)

        h_layout.addWidget(self.port_div)
        h_layout.addWidget(self.players_div)
        h_layout.addWidget(self.table_size)
        h_layout.addStretch()

        parent_layout.addLayout(h_layout)

    def add_button_panel(self, parent_layout):
        self.stop_button = QPushButton("ENCERRAR")
        self.stop_button.clicked.connect(self.stop_button_action)

        self.start_button = QPushButton("INICIAR")
        self.start_button.clicked.connect(self.start_button_action)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.stop_button)
        h_layout.addStretch()
        h_layout.addWidget(self.start_button)

        parent_layout.addLayout(h_layout)
        self.stop_button.hide()

    def prepare_to_init(self):
        self._game_match.set_players(self._players_size)
        self._game_match.set_table_size(self._table_size)
        self._game_match.new_table()

    def start_button_action(self):
        self._server_port = self.port_div.get_value()
        self._table_size = self.table_size.get_value()
        self._players_size = self.players_div.get_value()

        if(self._table_size % 2 != 0 or self._table_size < 2 or self._table_size > 10):
            self.messagebox("Error: Dimensão Inválida (Par entre 2 e 10)")
        else:
            self.port_div.hide()
            self.players_div.hide()
            self.table_size.hide()
            self.start_button.hide()
            self.stop_button.show()
            self.prepare_to_init()
            self._socket_controller.set_server_port(self._server_port)
            self._socket_controller.start_server()


    def stop_button_action(self):
        self._socket_controller.stop_connection()
        time.sleep(0.5)
        self._q_app.quit()

    def messagebox(self, text):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(text)
        msg_box.setWindowTitle("Error")
        msg_box.exec_()

