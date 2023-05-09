import pygame
from utils import *

class Button:
    def __init__(self, screen, manager,  x, y, w, h, text, color, active_color):
        self.screen = screen
        self.manager = manager
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.active_color = active_color
        self.current_color = color
        self.text = text
        self.active = False
        self.txt_surface = FONT.render(self.text, True, BACKGROUND_COLOR) 
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.current_color =  self.active_color if self.active else self.color
            self.txt_surface = FONT.render(self.text, True, BACKGROUND_COLOR)  if not self.active else FONT.render(self.text, True, WHITE)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.text == 'Start':
                    if self.screen.ready:
                        self.screen.initialize_game_screen()
                        self.screen.window.fill(BACKGROUND_COLOR)
                        self.manager.change_screen(1)
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
        self.color = PLAYER_SCORE_COLOR
        self.active_color = (0, 180, 0)
        self.text = text
        self.label = label
        self.txt_surface = FONT.render(text, True, BACKGROUND_COLOR)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.active_color if self.active else PLAYER_SCORE_COLOR
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.active = False
                    
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.color = self.active_color if self.active else PLAYER_SCORE_COLOR
                self.txt_surface = FONT.render(self.text, True, PLAYER_SCORE_COLOR)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, window):
        label = FONT.render(self.label, 1, PLAYER_SCORE_COLOR) if not self.active else FONT.render(self.label, 1, self.active_color)
        window.blit(label, ((self.rect.x + self.rect.width/2 - label.get_width()/2, self.rect.y - 25)))
        pygame.draw.rect(window, self.color, self.rect, 2, border_radius= 10)
        window.blit(self.txt_surface, (self.rect.x + 10 , self.rect.y + self.txt_surface.get_height()/2))