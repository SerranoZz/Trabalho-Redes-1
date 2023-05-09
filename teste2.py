import pygame
import socket
import select
import time


# Initialize Pygame
pygame.init()
display_info = pygame.display.Info()
width, height = display_info.current_w, display_info.current_h
screen = pygame.display.set_mode((720+240, 720+70))

#settings
pygame.display.set_caption('Jogo da Memória')
font_size = int(width * 0.01)
font = pygame.font.SysFont("Monospace", font_size, bold=1)
font_points = pygame.font.SysFont("Monospace", font_size, bold=1)
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

class Card:
    def __init__(self, x, y, width, height, row, colum):
        self.x = x
        self.y = y
        self.row = row
        self.column = colum
        self.width = width
        self.height = height
        self.text = -1
        self.card_surface = pygame.Surface((self.width, self.height))
        self.font_color = (0, 0, 0)
        self.card_color = (255, 255, 255)
        self.font = pygame.font.SysFont("Monospace", font_size * 4, bold=1)
        self.image_path = "costas.jpg"
        self.flipped = False

    def draw(self, surface):
        pygame.draw.rect(self.card_surface, self.card_color, (0, 0, self.width, self.height), border_radius=10)

        if self.flipped or self.text == '-':
            text_surface = self.font.render(str(self.text), True, self.font_color)
            text_x = (self.width - text_surface.get_width()) // 2
            text_y = (self.height - text_surface.get_height()) // 2
            self.card_surface.blit(text_surface, (text_x, text_y))
        else:
            image_surface = pygame.image.load(self.image_path).convert_alpha()
            image_surface = pygame.transform.scale(image_surface, (self.width, self.height))
            self.card_surface.blit(image_surface, (0, 0))

        surface.blit(self.card_surface, (self.x, self.y))

    def is_clicked(self, pos):
        return self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height

    def flip(self):
        self.flipped = not self.flipped

    def update_text(self, text):
        self.text = text

class FinalMessage:
    def __init__(self, text, game):
        self.width = 600
        self.height = 200
        self.x = 240 + 720/2 - self.width/2
        self.y = 50 + 720/2 - self.height/2
        self.color = player_score_color
        self.text = text
        self.color = white
        self.restart = Button(game, self.x + self.width/4 - 150/2, self.y + self.height/2, 150, 50, 'Recomeçar', button_color, ic_color)
        self.close = Button(game, self.x + 3*self.width/4  - 150/2, self.y + self.height/2, 150, 50, 'Fechar', red, dark_red)

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), border_radius=10)
        text = font.render(self.text, True, background_color)
        window.blit(text, (self.x + self.width/2 - text.get_width()/2, self.y + self.height/4 - text.get_height()/2))
        self.restart.draw(window)
        self.close.draw(window)
        
        pygame.display.flip()
    
    def update_text(self, text):
        self.text = text

    def handle_event(self, event):
        print('passei no handle event da mensagem final')
        self.restart.handle_event(event)
        self.close.handle_event(event)

class Game:
    def __init__(self, window, host, port):
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
        self.window.fill(background_color)

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
            self.message.update_text('Jogada não computada. Clique na peça fechada!')
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
        

class GameSection:
    def __init__(self, window):
        self.window = window
        self.width = 710
        self.x = 250
        self.y = 80
        self.surface = pygame.Surface((self.width, self.width))
        self.rect = pygame.Rect(self.x, self.y, self.width, self.width)

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
        pygame.draw.rect(window, self.header_color, (self.x, self.y, self.width, 70))
        text = font.render('PLACAR', 1, white)
        window.blit(text, (self.x + self.width/2 - text.get_width()/2, self.y + 70/2 - text.get_height()/2))
        
        if self.players != None:
            for player in self.players:
                player.draw(window)
        
        pygame.display.flip()

class Message:
    def __init__(self, window, text):
        self.text = text
        self.x = 240
        self.y = 0
        self.width = window.get_width() - 240
        self.height = 70
        self.color = message_color
    
    def update_text(self, text):
        self.text = text

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
        lines = self.text.split('\n')
        if len(lines) == 1:
            text = font.render(self.text, 1, white)
            window.blit(text, (self.x + self.width/2 - text.get_width()/2, self.y + self.height/2 - text.get_height()/2))
        else:
            y = 20
            for i in range(len(lines)-1):
                text = font.render(lines[i], 1, white)
                window.blit(text, (self.x + self.width/2 - text.get_width()/2, y))
                y += 20
            pygame.display.flip()
            pygame.time.wait(2500)
            self.update_text(lines[len(lines)-1])
            self.draw(window)
            

class Player:
    def __init__(self, y, player_id, points, window):
        self.player = f'Jogador {player_id}'
        self.score_board = ScoreBoard(window)
        self.width = self.score_board.width * 0.75
        self.height = self.score_board.width * 0.2
        self.points = points
        self.color = player_score_color
        self.x = (self.score_board.width - self.width) / 2
        self.y = 100 + y * (self.height + 10)
    
    def update_score(self, points):
        self.points = points

    def draw(self, window):
        global font
        
        box = pygame.Surface((self.width, self.height))
        invisible = (0, 0, 0)  
        box.set_colorkey(invisible)
        pygame.draw.rect(box, score_board_header_color, (0, 0, self.width * 0.75, self.height), border_bottom_left_radius=10, border_top_left_radius=10)
        pygame.draw.rect(box, white, (self.width * 0.75, 0, self.width * 0.25, self.height), border_bottom_right_radius=10, border_top_right_radius=10)

        player = font.render(self.player, True, white)
        box.blit(player, (((self.width - player.get_width()) / 2) * 0.4, (self.height - player.get_height()) / 2))
        
        points = font_points.render(f'{self.points}', True, points_color)
        box.blit(points, (self.width * 0.83, (self.height - points.get_height()) / 2))

        window.blit(box, (self.x, self.y))
        #pygame.display.flip()

class Button:
    def __init__(self, screen, x, y, w, h, text, color, active_color):
        self.screen = screen
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
                    if self.screen.ready:
                        self.screen.initialize_game_screen()
                        self.screen.window.fill(background_color)
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


class ScreenManager:
    def __init__(self, window):
        self.window = window
        self.screens = [MenuScreen(self)]
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
            
                if self.current_screen == self.screens[0]:
                    self.current_screen.handle_event(event)
            
            if len(self.screens) > 1 and self.current_screen == self.screens[1]:
                self.current_screen.keep_alive()

            self.current_screen.draw()

            time0 = time1
            
            pygame.display.update()

class MenuScreen:
    def __init__(self, manager):
        self.manager = manager
        self.window = window
        self.image = pygame.image.load('./assets/ic.png')
        self.image = pygame.transform.smoothscale(self.image, (3*self.image.get_width()/4, 3*self.image.get_height()/4))
        self.ip_input = InputBox(3*window.get_width()/8 - 200/2, 5*window.get_height()/8 - 50/2, 200, 50, 'IP')
        self.port_input = InputBox(5*window.get_width()/8 - 200/2, 5*window.get_height()/8 - 50/2, 200, 50, 'Porta')
        self.ready = False
        self.start_button = Button(self, window.get_width()/2 - 100/2, 6*window.get_height()/8 - 50/2, 100, 50, 'Start', button_color, ic_color)
        

    def set_ready(self):
        self.ready = True

    def handle_event(self, event):
        self.start_button.handle_event(event)
        self.port_input.handle_event(event)
        self.ip_input.handle_event(event)
        if self.ip_input.text != '' and self.port_input.text != '':
            self.set_ready()
                    
    def draw(self):
        self.window.fill(white)
        self.window.blit(self.image, (self.window.get_width()/2 - self.image.get_width()/2, 0))
        self.ip_input.draw(window)
        self.port_input.draw(window)
        self.start_button.draw(window)
    
    def initialize_game_screen(self):
        self.manager.screens.append(Game(self.window, self.ip_input.text, int(self.port_input.text)))
    

host = "127.0.0.1"
port = 8096
width = 240 + 720
height = 50 + 720 
window = pygame.display.set_mode((width, height))
screen_manager = ScreenManager(window) 
screen_manager.run()

