import pygame
from menu import *

pygame.init()

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

