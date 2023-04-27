import pygame

#início de uma tela bonitinha e etc

pygame.init()
width = 720
height = 720
window = pygame.display.set_mode((width, height))
screen = pygame.display.get_surface()

pygame.display.flip()

running = True
background_color = (23, 25, 33)
step = 10
cards = []
dim = 4
size = (height - step * dim)/dim

class Card:
    def __init__(self, x, y, image_flipped):
        global step, size
        self._image = pygame.image.load('./assets/not_flipped/card_not_flipped.png')
        self._image_flipped = pygame.image.load('./assets/flipped/'+image_flipped)
        self._image = pygame.transform.smoothscale(self._image, (size, size))
        self._image_flipped = pygame.transform.smoothscale(self._image_flipped, (size, size))
        self._x = x  * (self._image.get_width() + step)
        self._y = y * (self._image.get_height() + step)
        self._flipped = False
        self._value = -1
    
    def collided(self, x, y):
        return (x >= self._x and x < self._x + self._image.get_width() and y < self._image.get_height() + self._y and y > self._y)
        
    def draw(self, window):
        global step
        if(not self._flipped):
            window.blit(self._image, (self._x, self._y))
        else:
            window.blit(self._image_flipped, (self._x, self._y))

    def flip(self):
        self._flipped = True


for i in range(dim):
    for j in range(dim):
        cards.append(Card(j, i, 'c2.png'))

while running:
    window.fill(background_color)

    for event in pygame.event.get():   
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            for i in range(len(cards)):
                if(cards[i].collided(pos[0], pos[1])):
                    cards[i].flip()
                    print('posicao clicada:', i//dim, i%dim)
    
    for card in cards:
        card.draw(window)

    
    pygame.display.update()

#window = Window(1280, 720)
#window.set_title("TBM")

#while True:
    #window.update()
