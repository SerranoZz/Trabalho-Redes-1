import sys

from PyQt5.QtWidgets import QApplication

from src.decode.message_decode import MessageDecode
from src.game.game_match import GameMatch
from src.connections.socket_controller import SocketController
from src.interface.window import MainDialog


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = MainDialog(app)
    socket_controller = SocketController()
    game_match = GameMatch()
    decode = MessageDecode()

    dialog.set_socket_controller(socket_controller)
    dialog.set_decode(decode)
    dialog.set_game_match(game_match)
    dialog.show()

    sys.exit(app.exec_())
