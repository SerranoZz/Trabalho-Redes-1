import pygame
from utils import *
from interface_interaction import Button

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
        self.header_color = SCORE_BOARD_HEADER_COLOR
        self.color = SCORE_BOARD_COLOR
        self.players = None
        self.font = FONT
    
    def update_players(self, players):
        self.players = players
    
    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(window, self.header_color, (self.x, self.y, self.width, 70))
        text = self.font.render('PLACAR', 1, WHITE)
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
        self.color = MESSAGORE_COLOR
        self.font = FONT
    
    def update_text(self, msg):
        message = msg
        if len(msg.split('/')) > 1:
            message = msg.split('/')[1]
        self.text = message

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
        lines = self.text.split('\n')
        if len(lines) == 1:
            text = self.font.render(self.text, 1, WHITE)
            window.blit(text, (self.x + self.width/2 - text.get_width()/2, self.y + self.height/2 - text.get_height()/2))
        else:
            y = 20
            for i in range(len(lines)-1):
                text = self.font.render(lines[i], 1, WHITE)
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
        self.color = PLAYER_SCORE_COLOR
        self.x = (self.score_board.width - self.width) / 2
        self.y = 100 + y * (self.height + 10)
        self.font = FONT
    
    def update_score(self, points):
        self.points = points

    def draw(self, window):
        
        box = pygame.Surface((self.width, self.height))
        invisible = (0, 0, 0)  
        box.set_colorkey(invisible)
        pygame.draw.rect(box, SCORE_BOARD_HEADER_COLOR, (0, 0, self.width * 0.75, self.height), border_bottom_left_radius=10, border_top_left_radius=10)
        pygame.draw.rect(box, WHITE, (self.width * 0.75, 0, self.width * 0.25, self.height), border_bottom_right_radius=10, border_top_right_radius=10)

        player = self.font.render(self.player, True, WHITE)
        box.blit(player, (((self.width - player.get_width()) / 2) * 0.4, (self.height - player.get_height()) / 2))
        
        points = self.font.render(f'{self.points}', True, POINTS_COLOR)
        box.blit(points, (self.width * 0.83, (self.height - points.get_height()) / 2))

        window.blit(box, (self.x, self.y))
        #pygame.display.flip()

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
        self.font = pygame.font.SysFont("Monospace", FONT_SIZE * 4, bold=1)
        self.image_path = './assets/verso_carta.png'
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
    def __init__(self, text):
        self.width = 600
        self.height = 200
        self.x = 240 + 720/2 - self.width/2
        self.y = 50 + 720/2 - self.height/2
        self.color = SCORE_BOARD_COLOR
        self.text = text
        self.font = FONT

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), border_radius=10)
        text = self.font.render(self.text, True, WHITE)
        window.blit(text, (self.x + self.width/2 - text.get_width()/2, self.y + self.height/2 - text.get_height()/2))
        
    
    def update_text(self, text):
        self.text = text.split('\n')[0]

    def handle_event(self):
        for event in pygame.event.get():
            self.restart.handle_event(event)
            self.close.handle_event(event)
