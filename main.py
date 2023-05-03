import pygame
import socket
import select

pygame.init()
width = 240 + 720
height = 50 + 720 
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Jogo da Memória')
font = pygame.font.SysFont("Monospace", 20)

running = True
background_color = (0, 35, 0)
player_score_color = (12, 79, 9)
score_board_color = (47, 125, 35)
score_board_header_color = (32, 78, 25)
message_color = (47, 125, 35)
points_color = (47, 125, 35)
white = (255, 255, 255)
ic_color = (11, 105, 81)
start_color = (20, 105, 100)
button_color = (46,139,87)
red = (200, 0, 0)
dark_red = (150, 0, 0)

#por enquanto calculando a dimensão das cartas por aqui, mas dps a gnt muda
step = 10
host = "127.0.0.1"
port = 8096

cards_not_flipped = []
cards_flipped = []

class Card:
    def __init__(self, x0, y, dim, step):
        self._flipped = False
        self._row = y
        self._column = x0
        self._image = pygame.image.load('./assets/flipped/c2.png') if self._flipped else pygame.image.load('./assets/cartinha.png')
        self.size = (720 - step * dim)/dim
        self._image = pygame.transform.smoothscale(self._image, (self.size, self.size))
        self.margem = (720 - dim*self.size)/2
        self.x = 240  + self.margem + x0 * (self.size)
        self.y = 50 + y * (self.size  + step)
        print('x constutor', self.x)
        print('y constutor', self.y)
        self._value = -1
    
    def collided(self, x, y):
        return (x >= self.x + 17 and x < self.x + self._image.get_width() - 17 and y < self._image.get_height() + self.y and y > self.y)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if self.collided(pos[0], pos[1]):
                self.set_flip(True)
                print(f'carta clicada -> ({self._row}, {self._column})')
                print('valor da carta ->', self._value)
            self._image = pygame.image.load('./assets/flipped/c2.png') if self._flipped else pygame.image.load('./assets/cartinha.png')
            self._image = pygame.transform.smoothscale(self._image, (self.size, self.size))

    def update_value(self, value):
        self._value = value

    def draw(self, window):
        global step
        if self._value != -1:
            print('x desenho', self.x)
            print('y desenho', self.y)
            window.blit(self._image, (int(self.x), int(self.y)))

    def set_flip(self, value):
        self._flipped = value

class ScoreBoard:
    def __init__(self, window):
        self.x = 0
        self.y = 0

        self.width = 240
        self.height = window.get_height()
        self.header_color = score_board_header_color
        self.color = score_board_color
        self.players = None
    
    def update_players(self, players):
        self.players = players
    
    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(window, self.header_color, (self.x, self.y, self.width, 50))
        text = font.render('PLACAR', 1, white)
        window.blit(text, (self.x + self.width/2 - text.get_width()/2, self.y + 50/2 - text.get_height()/2))
        
        if self.players != None:
            for player in self.players:
                player.draw(window)

class Player:
    def __init__(self, y, player_id, points):
        self.player = f'Jogador {player_id}'
        self.width = 200
        self.height = 50
        self.points = points
        self.color = player_score_color
        self.x = 20
        self.y = 70 + y * (self.height + step)
    
    def update_score(self, points):
        self.points = points

    def draw(self, window):
        global font
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), border_radius=10)
        pygame.draw.rect(window, white, (self.x + 140, self.y, self.width - 140, self.height), border_bottom_right_radius=10, border_top_right_radius=10)
        player = font.render(self.player, 1, white)
        window.blit(player, (self.x + 140/2 - player.get_width()/2, self.y + self.height/2 - player.get_height()/2))
        points = font.render(f'{self.points}', 1, points_color)
        window.blit(points, (self.x + 170 - points.get_width()/2, self.y + self.height/2 - points.get_height()/2))

class Message:
    def __init__(self, window, text):
        self.text = text
        self.x = 240
        self.y = 0
        self.width = window.get_width() - 240
        self.height = 50
        self.color = message_color
    
    def update_text(self, text):
        self.text = text

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
        text = font.render(self.text, 1, white)
        window.blit(text, (self.x + self.width/2 - text.get_width()/2, self.y + self.height/2 - text.get_height()/2))

class Button:
    def __init__(self, x, y, w, h, text, color, active_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.active_color = active_color
        self.current_color = color
        self.text = text
        self.active = False
        self.txt_surface = font.render(self.text, True, background_color) 
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.current_color =  self.active_color if self.active else self.color
            self.txt_surface = font.render(self.text, True, background_color)  if not self.active else font.render(self.text, True, white)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.text == 'Start':
                    screen_manager.change_screen(1)
                elif self.text == 'Recomeçar':
                    pass
                elif self.text == 'Fechar':
                    pygame.quit()
                    exit()

    def draw(self, window):
        pygame.draw.rect(window, self.current_color, self.rect, border_radius= 10)
        window.blit(self.txt_surface, (self.rect.x + self.rect.width/2 - self.txt_surface.get_width()/2, self.rect.y + self.rect.height/2 - self.txt_surface.get_height()/2))

class InputBox:
    def __init__(self, x, y, w, h, label, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = player_score_color
        self.active_color = (0, 180, 0)
        self.text = text
        self.label = label
        self.txt_surface = font.render(text, True, background_color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.active_color if self.active else player_score_color
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.active = False
                    
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.color = self.active_color if self.active else player_score_color
                self.txt_surface = font.render(self.text, True, player_score_color)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, window):
        label = font.render(self.label, 1, player_score_color) if not self.active else font.render(self.label, 1, self.active_color)
        window.blit(label, ((self.rect.x + self.rect.width/2 - label.get_width()/2, self.rect.y - 25)))
        pygame.draw.rect(window, self.color, self.rect, 2, border_radius= 10)
        window.blit(self.txt_surface, (self.rect.x + 10 , self.rect.y + self.txt_surface.get_height()/2))

class FinalMessage:
    def __init__(self, text):
        self.width = 400
        self.height = 200
        self.x = 240 + 720/2 - self.width/2
        self.y = 50 + 720/2 - self.height/2
        self.color = player_score_color
        self.text = text
        self.color = white
        self.restart = Button(self.x + self.width/4 - 150/2, self.y + self.height/2, 150, 50, 'Recomeçar', button_color, ic_color)
        self.close = Button(self.x + 3*self.width/4  - 150/2, self.y + self.height/2, 150, 50, 'Fechar', red, dark_red)

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), border_radius=10)
        text = font.render(self.text, True, background_color)
        window.blit(text, (self.x + self.width/2 - text.get_width()/2, self.y + self.height/4 - text.get_height()/2))
        self.restart.draw(window)
        self.close.draw(window)
    
    def handle_event(self, event):
        self.restart.handle_event(event)
        self.close.handle_event(event)

class Game:
    def __init__(self, window):
        self.dim = -1
        self.players_number = -1
        self.window = window
        self.cards = []
        self.players = []
        self.message = Message(self.window, '')
        self.score_board = ScoreBoard(self.window)
        #self.final_message = FinalMessage(window, 'Você ganhou!!')
    
    def initialize_score_board(self):
        self.score_board = ScoreBoard(window, self.players)

    def handle_event(self, event):
        for card in self.cards:
            card.handle_event(event)
        
        #self.final_message.handle_event(event)

    def clean_screen(self):
        for card in self.cards:
            card.set_flip(False)

    #atualizando o valor das cartas
    def update_cards(self, message):
        table = list(message.split('|')[0].split(' '))
        print(table)
        for i in range(self.dim):
            self.cards[i].update_value(int(table[i]))
    
    def update_players_score(self, message):
        score_map = message.split('/')[0].split('|')[1]
        list_score_map = score_map.split(' ')
        
        for i in range(self.players_number - 1):
            index = int(list_score_map[i].split(':')[0])
            points = int(list_score_map[i].split(':')[1])
        
            self.players[index].update_score(points)

    def initialize_game(self, message):
        self.dim = int(message.split('|')[1])
        self.players_number = int(message.split('|')[0])
        self.cards = []
        for i in range(self.dim):
            for j in range(self.dim):
                self.cards.append(Card(i, j, self.dim, step))
        self.players = [Player(i, i+1, 0) for i in range(self.players_number)]
        self.score_board.update_players(self.players)

    def handle_messages(self, status, msg):
        if status == "YOUR_TURN":
            # self.clean_screen()
            # message = input(msg)
                # while not read_coords(msg, message):
            #     message = input("Especifique uma peca: ")
            # connection.send(str.encode(message))
            self.message.update_text(msg.split('/')[1])
            self.update_cards(msg)
            self.update_players_score(msg)
            pass
        elif status == "RESPONSE" or status == "NOT_YOUR_TURN":
            #self.clean_screen()
            self.message.update_text(msg.split('/')[1])
            self.update_cards(msg)
            self.update_players_score(msg)
            print(msg.split('/')[0].split('|')[1])
        elif status == "END_GAME" or status == "SERVER_CLOSED":
            #self.clean_screen()
            self.message.update_text(msg.split('/')[1])
            self.update_cards(msg)
            self.update_players_score(msg)
            return
        elif status == "SETUP":
            self.initialize_game(msg)
        elif status == "WAITING_PLAYERS":
            #self.clean_screen()
            self.message.update_text(msg.split('/')[1])

    def keep_alive(self, connection):
        ready_sockets, _, _ = select.select([connection], [], [], 1)
        if not ready_sockets:
            return

        res = connection.recv(2024)
        res_message = res.decode("utf-8")
        messages = res_message.split('msg')
        print(messages)

        for i in range(len(messages)):
            if messages[i] == '':
                continue
            res_msgs = messages[i].split("::= ")
            print(res_msgs)
            status = res_msgs[0]
            print(status)
            msg = res_msgs[1]
            print(msg)
            self.handle_messages(status, msg)
            print(res_msgs)
            print(msg)

    def draw(self):
        window.fill(background_color)
        for card in self.cards:
            card.draw(self.window)

        self.score_board.draw(self.window)
        self.message.draw(self.window)
        #self.final_message.draw(self.window)

class ScreenManager:
    def __init__(self, window):
        self.window = window
        self.screens = [MenuScreen(self.window), Game(self.window)]
        self.current_screen = self.screens[0]

    def change_screen(self, index):
        self.current_screen = self.screens[index]

    def run(self):
        time0 = pygame.time.get_ticks()

        while True:
            time1 = pygame.time.get_ticks()

            if (time1 - time0 < 100/6):
                continue

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
                self.current_screen.handle_event(event)
                if self.current_screen == self.screens[1]:
                    self.current_screen.keep_alive(client)
                self.current_screen.draw()

            time0 = time1
            
            pygame.display.update()

class MenuScreen:
    def __init__(self, window):
        self.window = window
        self.image = pygame.image.load('./assets/ic.png')
        self.image = pygame.transform.smoothscale(self.image, (3*self.image.get_width()/4, 3*self.image.get_height()/4))
        self.ip_input = InputBox(3*window.get_width()/8 - 200/2, 5*window.get_height()/8 - 50/2, 200, 50, 'IP')
        self.port_input = InputBox(5*window.get_width()/8 - 200/2, 5*window.get_height()/8 - 50/2, 200, 50, 'Porta')
        self.start_button = Button(window.get_width()/2 - 100/2, 6*window.get_height()/8 - 50/2, 100, 50, 'Start', button_color, ic_color)

    def handle_event(self, event):
        self.start_button.handle_event(event)
        self.port_input.handle_event(event)
        self.ip_input.handle_event(event)
                    
    def draw(self):
        self.window.fill(white)
        self.window.blit(self.image, (self.window.get_width()/2 - self.image.get_width()/2, 0))
        self.ip_input.draw(window)
        self.port_input.draw(window)
        self.start_button.draw(window)

client = socket.socket()
client.connect((host, port))

screen_manager = ScreenManager(window) 
screen_manager.run()
