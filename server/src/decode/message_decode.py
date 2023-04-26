from enum import Enum

from src.game.game_match import GameMatch


class Status(Enum):
    NOT_YOUR_TURN = 0
    INVALID_MESSAGE = 1
    VALID_MESSAGE = 2


class MessageDecode:
    def __init__(self):
        self._game_match: GameMatch | None = None

    def set_game_match(self, game_match):
        self._game_match = game_match

    def decode_message(self, player_id, message):
        if self._game_match.get_actual_player() != player_id:
            return Status.NOT_YOUR_TURN

        msgs = message.split(" ")
        if len(msgs) != 2:
            return Status.INVALID_MESSAGE

        try:
            i = int(msgs[0])
            j = int(msgs[1])
        except ValueError:
            return Status.INVALID_MESSAGE

        if not self._game_match.open_piece(i, j, player_id):
            return Status.INVALID_MESSAGE

        return Status.VALID_MESSAGE
