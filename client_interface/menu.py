import pygame
from utils import *
from game import *
from interface_interaction import Button, InputBox

class MenuScreen:
    def __init__(self, manager):
        self.manager = manager
        self.window = WINDOW
        self.image = pygame.image.load('./assets/ic.png')
        self.image = pygame.transform.smoothscale(self.image, (3*self.image.get_width()/4, 3*self.image.get_height()/4))
        self.ip_input = InputBox(3*self.window.get_width()/8 - 200/2, 5*self.window.get_height()/8 - 50/2, 200, 50, 'IP')
        self.port_input = InputBox(5*self.window.get_width()/8 - 200/2, 5*self.window.get_height()/8 - 50/2, 200, 50, 'Porta')
        self.ready = False
        self.start_button = Button(self, self.manager, self.window.get_width()/2 - 100/2, 6*self.window.get_height()/8 - 50/2, 100, 50, 'Start', BUTTON_COLOR,IC_COLOR)
        

    def set_ready(self):
        self.ready = True

    def handle_event(self, event):
        self.start_button.handle_event(event)
        self.port_input.handle_event(event)
        self.ip_input.handle_event(event)
        if self.ip_input.text != '' and self.port_input.text != '':
            self.set_ready()
                    
    def draw(self):
        self.window.fill(WHITE)
        self.window.blit(self.image, (self.window.get_width()/2 - self.image.get_width()/2, 0))
        self.ip_input.draw(self.window)
        self.port_input.draw(self.window)
        self.start_button.draw(self.window)
    
    def initialize_game_screen(self):
        self.manager.screens.append(Game(self.manager, self.window, self.ip_input.text, int(self.port_input.text)))
    