from random import randint


class GameMatch:
    def __init__(self):
        self._players = 4
        self._table_size = 4
        self._score_board: list[int] | None = None
        self._table: list[list[int]] | None = None
        self._found_pars = 0
        self._pars = (self._table_size ** 2) // 2
        self._actual_player = 0
        self._pieces = []
        self._temp_index = [0] * 4
        self._temp_player_id = 0
        self._index = 0
        self._check = False
        self._wait = True

    def set_players(self, players):
        self._players = players
        self._score_board = [0 for _ in range(self._players)]

    def set_table_size(self, table_size):
        self._table_size = table_size
        self._pars = (self._table_size ** 2) // 2
        self._table = [
            [0 for _ in range(self._table_size)]
            for _ in range(self._table_size)
        ]

    def set_wait(self, value):
        self._wait = value

    def new_table(self):
        available_positions = []
        for i in range(0, self._table_size):
            for j in range(0, self._table_size):
                available_positions.append((i, j))

        for j in range(0, self._table_size // 2):
            for i in range(1, self._table_size + 1):
                for _ in range(2):
                    max_pos = len(available_positions)
                    rand_index = randint(0, max_pos - 1)
                    r_i, r_j = available_positions.pop(rand_index)

                    self._table[r_i][r_j] = -i

    def table_str(self):
        result = "     "
        for i in range(self._table_size):
            result += "{0:2d} ".format(i)
        result += "\n-----"
        for i in range(self._table_size):
            result += "---"
        result += "\n"

        for i in range(self._table_size):
            result += "{0:2d} | ".format(i)
            for j in range(self._table_size):
                if self._table[i][j] == "-":
                    result += " - "
                elif self._table[i][j] >= 0:
                    result += "{0:2d} ".format(self._table[i][j])
                else:
                    result += " ? "
            result += "\n"
        return result

    def score_board_str(self):
        result = "Placar:\n---------------------\n"
        for i in range(self._players):
            result += "Jogador {0}: {1:2d}\n".format(i + 1, self._score_board[i])
        return result

    def choose_pieces(self):
        if self._check:
            i1 = self._temp_index[0]
            j1 = self._temp_index[1]
            i2 = self._temp_index[2]
            j2 = self._temp_index[3]
            return "Peças escolhidas --> ({0}, {1}) e ({2}, {3})\n".format(i1, j1, i2, j2)
        return ""

    def pieces_result(self, player_id):
        if self._check:
            i1 = self._temp_index[0]
            j1 = self._temp_index[1]
            i2 = self._temp_index[2]
            j2 = self._temp_index[3]
            if self._table[i1][j1] == self._table[i2][j2]:
                if self._temp_player_id == player_id:
                    self._score_board[self._temp_player_id] += 1
                    self._found_pars += 1
                self.remove_piece(i1, j1)
                self.remove_piece(i2, j2)
                return "Peças casam! Ponto para o jogador {0}.\n".format(self._temp_player_id + 1)
            else:
                self.close_piece(i1, j1)
                self.close_piece(i2, j2)
                return "Peças não casam!\n"
        return ""

    def open_piece(self, i, j, player_id):
        if self._table[i][j] == '-':
            return False
        elif self._table[i][j] < 0:
            self._table[i][j] = -self._table[i][j]
            self._pieces.append((i, j))
            if len(self._pieces) == 2:
                self._temp_index[0] = self._pieces[0][0]
                self._temp_index[1] = self._pieces[0][1]
                self._temp_index[2] = self._pieces[1][0]
                self._temp_index[3] = self._pieces[1][1]
                self._temp_player_id = player_id
                self._check = True
            else:
                self._check = False
            return True
        return False

    def winners(self):
        max_point = max(self._score_board)
        winners = []
        for i in range(self._players):
            if self._score_board[i] == max_point:
                winners.append(i)

        if len(winners) > 1:
            result = "Houve um empate entre os jogadores "
            for i in winners:
                result += str(i + 1) + " "
            result += "\n"
        else:
            result = "O jogador {0} foi o vencedor!\n".format(winners[0] + 1)

        return result

    def remove_piece(self, i, j):
        if self._table[i][j] != '-':
            self._table[i][j] = "-"

    def close_piece(self, i, j):
        if self._table[i][j] != '-' and self._table[i][j] > 0:
            self._table[i][j] = -self._table[i][j]

    def should_next(self):
        if(len(self._pieces) == 2):
            i1 = self._temp_index[0]
            j1 = self._temp_index[1]
            i2 = self._temp_index[2]
            j2 = self._temp_index[3]
            if self._table[i1][j1] == self._table[i2][j2]:
                self._pieces = []
                return False
            else:
                return True
        else:
            return False

    def get_actual_player(self):
        return self._actual_player
    
    def get_players(self):
        return self._players

    def is_game_finish(self):
        return self._found_pars >= self._pars

    def next_player(self):
        self._index += 1
        self._pieces = []
        self._actual_player = self._index % self._players
