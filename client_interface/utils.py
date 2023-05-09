import pygame

pygame.init()

#settings
pygame.display.set_caption('Jogo da Memória')
WIDTH = 240 + 720
HEIGHT = 50 + 720 
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
FONT_SIZE = 20
TIME = 1500
FONT = pygame.font.SysFont("Monospace", FONT_SIZE, bold=1)
BACKGROUND_COLOR = (0, 35, 0)
PLAYER_SCORE_COLOR = (12, 79, 9)
SCORE_BOARD_COLOR = (47, 125, 35)
SCORE_BOARD_HEADER_COLOR = (32, 78, 25)
MESSAGORE_COLOR = (47, 125, 35)
POINTS_COLOR = (47, 125, 35)
WHITE = (255, 255, 255)
IC_COLOR = (11, 105, 81)
START_COLOR = (20, 105, 100)
BUTTON_COLOR = (46,139,87)
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)

