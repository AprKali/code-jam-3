import pygame

from project.constants import Color, FPS, HEIGHT, WIDTH
from project.menus.home import Home
from project.sprites.background import Background
from project.sprites.character import Character


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
        self.backgroud = Background("stars2.png", self.screen, 5)

        self.mouse_x = 0
        self.mouse_y = 0

        pygame.init()
        pygame.display.set_caption('Game in development')

    def new(self):
        """
        Every time a new game starts
        """
        self.all_sprites = pygame.sprite.Group()
        self.others = pygame.sprite.Group()  # Find a better name? Projectiles will be stored here for now
        self.devchar = Character(self, 10, 10, friction=-0.052)

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
        self.backgroud.draw()
        self.all_sprites.draw(self.screen)

        pygame.display.flip()

    def show_start_screen(self):

        self.screen.fill(Color.light_green)
        self.homepage = Home(self.screen)
        self._wait_for_input()

    def _wait_for_input(self):
        waiting = True
        while waiting:
            self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
            self.homepage.draw(self.mouse_x, self.mouse_y)

            self.clock.tick(FPS/2)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = self.running = False
                if event.type == pygame.MOUSEBUTTONUP and self.homepage.buttons_hover_states["play"]:
                    waiting = False
                if event.type == pygame.MOUSEBUTTONUP and self.homepage.buttons_hover_states["exit"]:
                    self.running = self.playing = waiting = False
