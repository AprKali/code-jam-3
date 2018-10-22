import pygame
from constants import Color, FPS, HEIGHT, WIDTH
from sprites import dev_character


class Game:
    """
    Main Game class
    """
    def __init__(self):
        self.running = True
        self.playing = True

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.get_default_font()

        pygame.init()
        pygame.display.set_caption('Game in development')

    def new(self):
        """
        Every time a new game starts
        """
        self.all_sprites = pygame.sprite.Group()
        self.devchar = dev_character.Character(self)

        self._run()

    def _run(self)-> None:

        while self.playing:
            self.clock.tick(FPS)
            self._events()
            self._update()
            self._draw()

    def _events(self)-> None:
        """
        Every event will be registered here
        """
        key = pygame.key.get_pressed()

        if key[pygame.K_ESCAPE]:
            self.running = self.playing = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = self.playing = False

    def _update(self)-> None:
        """
        Every sprite's update will be registered here
        """
        self.all_sprites.update()

    def _draw(self)-> None:
        """
        Everything we draw to the screen will be done here

        Don't forget that we always draw first then -> pygame.display.flip()
        """
        #  self._draw_text(50, 'TEST ONE TWO THREE', Color.white, (HEIGHT/2, WIDTH/7))
        self.screen.fill(Color.white)
        self.all_sprites.draw(self.screen)

        pygame.display.flip()

    def _draw_text(self, size: int, text: str, color: Color, cords: tuple):
        font = pygame.font.Font(self.font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = cords
        self.screen.blit(text_surface, text_rect)