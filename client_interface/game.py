import pygame
import socket
import select
from game_components import GameSection, ScoreBoard, Message, FinalMessage, Card, Player
from utils import *

class Game:
    def __init__(self, manager, window, host, port):
        self.manager = manager
        self.connection = socket.socket()
        self.connection.connect((host, port))
        self.window = window
        self.dim = -1
        self.players_number = -1
        self.cards = []
        self.players = []
        self.game_section = GameSection(self.window)
        self.score_board = ScoreBoard(self.window)
        self.message = Message(self.window, '')
        self.final_message = FinalMessage('', self)

    def initialize_score_board(self):
        self.score_board = ScoreBoard(self.window, self.players)

    def initialize_game(self, message, spacing):
        self.window.fill(BACKGROUND_COLOR)

        self.dim = int(message.split('|')[1])
        self.players_number = int(message.split('|')[0])
        card_width = (self.game_section.width - (spacing * self.dim)) / self.dim
        card_height = (self.game_section.width - (spacing * self.dim)) / self.dim
        for i in range(self.dim):
            for j in range(self.dim):
                card_x = self.game_section.x + (j * (card_width + spacing))
                card_y = self.game_section.y + (i * (card_height + spacing))
                self.cards.append(Card(card_x, card_y, card_height, card_width, i, j))
        
        self.players = [Player(i, i+1, 0, self.window) for i in range(self.players_number)]
        self.score_board.update_players(self.players)

        for card in self.cards:
            card.draw(self.window)


    def draw(self):
        if self.final_message.text != '':
            self.final_message.draw(self.window)

        self.score_board.draw(self.window)
        self.message.draw(self.window)


    def handle_click(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                for card in self.cards:
                    if card.is_clicked(pos):
                        self.turn_card(card)
                        return f'{card.row} {card.column}'
    
    def turn_card(self, card):
        if card.text != '-':
            card.flip()
            card.draw(self.window)
            pygame.display.update()
            pygame.time.wait(1000)
            card.flip()
            card.draw(self.window) 
            pygame.display.update()
        else:
            real_message = self.message.text.split('\n')[-1]
            self.message.update_text('Jogada não computada. Clique na carta fechada!')
            self.message.draw(self.window)
            pygame.display.update()
            pygame.time.wait(1500)
            self.message.update_text(real_message)
            return
         
    def update_cards(self, message):
        table = list(message.split('|')[0].split(' '))
        for i in range(self.dim**2):
            if table[i] != '-':
                self.cards[i].update_text(int(table[i]))
            else:
                self.cards[i].update_text(table[i])
                self.cards[i].draw(self.window)

    def update_players_score(self, message):
        score_map = message.split('/')[0].split('|')[1]
        list_score_map = score_map.split(' ')
        
        for i in range(self.players_number):
            index = int(list_score_map[i].split(':')[0])
            points = int(list_score_map[i].split(':')[1])
            print(f'pontos do jogador {index}: {points}')
        
            self.players[index-1].update_score(points)
            self.players[index-1].draw(self.window)
            
    def handle_messages(self, status, msg, connection):
        if status == "YOUR_TURN":
            self.update_cards(msg)
            self.message.update_text(msg.split('/')[1])
            self.message.draw(self.window)
            self.update_players_score(msg)
            self.score_board.draw(self.window)
            coord = self.handle_click()
            while coord == None:
                coord = self.handle_click()
            connection.send(str.encode(coord))

        elif status == "RESPONSE" or status == "NOT_YOUR_TURN":
            self.message.update_text(msg.split('/')[1])
            self.update_cards(msg)
            self.update_players_score(msg)

        elif status == "END_GAME" or status == "SERVER_CLOSED":
            print('aqui a mensagem final', msg)
            self.message.update_text('')
            self.final_message.update_text(msg)
            
            for event in pygame.event.get():
                self.final_message.close.handle_event(event)
                self.final_message.restart.handle_event(event)
        
        elif status == "SETUP":
            self.initialize_game(msg, 10)

        elif status == "WAITING_PLAYERS":
            self.message.update_text(msg.split('/')[1])
        

    def keep_alive(self):
        ready_sockets, _, _ = select.select([self.connection], [], [], 1)
        if not ready_sockets:
            return

        res = self.connection.recv(2024)
        res_message = res.decode("utf-8")
        messages = res_message.split('msg')

        print(messages)

        for i in range(len(messages)):
            if messages[i] == '':
                continue
            res_msgs = messages[i].split("::= ")
            status = res_msgs[0]
            msg = res_msgs[1]
            self.handle_messages(status, msg, self.connection)