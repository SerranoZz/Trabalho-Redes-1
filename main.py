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
dim = 10
n_jogadores = 10
size = (720 - step * dim)/dim

host = "127.0.0.1"
port_a = 8096

cards_not_flipped = []
cards_flipped = []

class Card:
    def __init__(self, x, y):
        global step, size
        self._flipped = False
        self._image = pygame.image.load('./assets/flipped/c2.png') if self._flipped else  pygame.image.load('./assets/cartinha.png')
        self._image = pygame.transform.smoothscale(self._image, (size, size))
        self.margem = (720 - dim*self._image.get_width())/2
        self._x = 240  + self.margem + x * (self._image.get_width())
        self._y = 50 + y * (self._image.get_height()  + step)
        self._value = -1
    
    def collided(self, x, y):
        return (x >= self._x + 17 and x < self._x + self._image.get_width() - 17 and y < self._image.get_height() + self._y and y > self._y)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if self.collided(pos[0], pos[1]):
                self.set_flip(True)

    def draw(self, window):
        window.blit(self._image, (self._x, self._y))

    def set_flip(self, value):
        self._flipped = value

class ScoreBoard:
    def __init__(self, window, players):
        self.x = 0
        self.y = 0
        self.width = 240
        self.height = window.get_height()
        self.header_color = score_board_header_color
        self.color = score_board_color
        self.players = players
    
    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(window, self.header_color, (self.x, self.y, self.width, 50))
        text = font.render('PLACAR', 1, white)
        window.blit(text, (self.x + self.width/2 - text.get_width()/2, self.y + 50/2 - text.get_height()/2))
        
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
    def __init__(self, window, text):
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
    def __init__(self, window, dim, players_number):
        self.dim = dim
        self.players_number = players_number
        self.window = window
        self.cards = [Card(j, i) for i in range(self.dim) for j in range(self.dim)]
        self.players = [Player(i, i+1, 0) for i in range(self.players_number)]
        self.message = Message(self.window, 'Vez do fulaninho')
        self.score_board = ScoreBoard(self.window, self.players)
    
    def initialize_score_board(self):
        self.score_board = ScoreBoard(window, self.players)

    def handle_event(self, event):
        for card in self.cards:
            card.handle_event(event)

    def clean_screen(self):
        for card in self.cards:
            card.set_flip(False)

    def draw(self):
        window.fill(background_color)

        for card in self.cards:
            card.draw(self.window)

        self.score_board.draw(self.window)
        self.message.draw(self.window)
        pygame.display.update()

class ScreenManager:
    def __init__(self, window):
        self.window = window
        self.screens = [MenuScreen(self.window), Game(self.window, 10, 10)]
        self.current_screen = self.screens[0]

    def change_screen(self, index):
        self.current_screen = self.screens[index]
    
    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
                if self.current_screen is not None:
                    self.current_screen.handle_event(event)
                    self.current_screen.draw()
            
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

        
screen_manager = ScreenManager(window) 
screen_manager.run()

# def main():
#     running = True
#     game = Game(window, 4, 10)
#     game.initialize_players()
#     game.initialize_cards()

#     while running:
#         game.redraw_window()
#         for event in pygame.event.get():   
#             if event.type == pygame.QUIT:
#                 running = False
        
#             game.handle_event(event)

#main()
