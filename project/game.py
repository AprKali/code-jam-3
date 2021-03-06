from pathlib import PurePath

import pygame as pg

from project.constants import Color, DEFAULT_FONT_NAME, FPS, HEIGHT, INVISIBLE, PATH_FX, WIDTH
from project.gameplay.intro import Intro, json_load
from project.sprites.character import Character
from project.ui.about import About
from project.ui.background import Background
from project.ui.main_menu import Home
from project.ui.options import Options
from project.ui.score import ScoreDisplay
from project.ui.timer import Timer
from project.ui.volume import get_volume
from project.wave_generator import WaveGenerator


class CustomGroup:
    """
    Imitates pg.sprite.Group(). It's main functionality is to handle every draw and update call for non
    Sprite class that do have and need any of those methods.
    """
    def __init__(self):
        self.elements = []

    def __len__(self):
        return len(self.elements)

    def __repr__(self):
        return f'{self.elements}'

    def add(self, element):
        self.elements.append(element)

    def draw(self):
        for element in self.elements:
            if hasattr(element, 'draw'):
                element.draw()

    def update(self):
        for element in self.elements:
            if hasattr(element, 'update'):
                element.update()


class Game:
    """
    Main Game class that controls and
    """

    def __init__(self):
        pg.init()
        pg.mixer.music.load(str(PurePath(PATH_FX).joinpath("song.mp3")))
        pg.mixer.music.play()
        pg.mouse.set_cursor(*INVISIBLE)

        self.running = True
        self.playing = True
        self.pause = True

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.font = pg.font.get_default_font()

        self.mouse_x = 0
        self.mouse_y = 0

        self.score = 0

        
        pg.display.set_caption('LAST JUDGMENT')

    def new(self):
        """
        Every time a new game starts
        """

        self.all_sprites = pg.sprite.Group()
        self.mines = pg.sprite.Group()
        self.enemy_sprites = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.others = pg.sprite.Group()
        self.enemy_projectiles = pg.sprite.Group()

        self.nonsprite = CustomGroup()

        self.background = Background('stars2.png', self, 5)

        self.devchar = Character(self, 100, 10, friction=-0.052, shield=50)

        self.timer = Timer(self, 600, WIDTH // 2 - 70, 25, DEFAULT_FONT_NAME, 50)
        self.score_display = ScoreDisplay(self, WIDTH - 160, 20, DEFAULT_FONT_NAME, 30)

        self.wave_generator = WaveGenerator(self)

        # TODO WITH SPREADSHEET IMAGE LOAD WON'T BE HERE, BUT IN EVERY SPRITE CLASS
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
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = self.playing = False

    def _update(self)-> None:
        """
        Every sprite's update will be registered here
        """

        self.all_sprites.update()
        self.nonsprite.update()

        for enemy in self.enemy_sprites:
            projectile_hit = pg.sprite.spritecollide(enemy, self.others, False)
            if projectile_hit:
                projectile_hit_mask = pg.sprite.spritecollide(enemy, self.others, False, pg.sprite.collide_mask)
                for projectile in projectile_hit_mask:
                    enemy.damage(projectile)
                    projectile.destroy()
        powerup_hit = pg.sprite.spritecollide(self.devchar, self.powerups, True, pg.sprite.collide_mask)

        if powerup_hit:
            powerup_hit[0].apply_powerup(self.devchar)

        enemy_projectiles_hit = pg.sprite.spritecollide(self.devchar, self.enemy_projectiles, False)
        if enemy_projectiles_hit:
            enemy_projectiles_hit_mask = pg.sprite.\
                spritecollide(self.devchar, self.enemy_projectiles, False, pg.sprite.collide_mask)
            for projectile in enemy_projectiles_hit_mask:
                self.devchar.damage(projectile)
                projectile.destroy()

        mine_hit = pg.sprite.spritecollide(self.devchar, self.mines, False)
        if mine_hit:
            mine_hit_mask = pg.sprite.spritecollide(self.devchar, self.mines, True, pg.sprite.collide_mask)
            if mine_hit_mask:
                self.devchar.heal(-20)

    def _draw(self)-> None:
        """
        Everything we draw to the screen will be done here

        Don't forget that we always draw first then -> pg.display.flip()
        """
        self.nonsprite.draw()
        self.all_sprites.draw(self.screen)

        pg.display.flip()

    def _destroy(self)-> None:
        self.kill()
        # TODO show end screen

    def play_intro(self):
        DATA = json_load()

        if DATA['intro_played']:
            return
        else:
            intro = Intro(self.screen)

            while intro.playing and self.running:
                intro.play()
                self.clock.tick(FPS/2)

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        intro.playing = self.running = False

    def show_start_screen(self):
        self.homepage = Home(self.screen)
        self._wait_for_input()

    def _wait_for_input(self)-> None:
        waiting = True

        while waiting:
            self.clock.tick(FPS/2)
            self.homepage.draw()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = self.running = False
                if event.type == pg.MOUSEBUTTONUP and self.homepage.buttons_hover_states['play']:
                    waiting = False
                if event.type == pg.MOUSEBUTTONUP and self.homepage.buttons_hover_states['options']:
                    self.options = Options(self.screen)
                    self.running = waiting = self.options.handle_input()
                    self.homepage.update_volume()
                if event.type == pg.MOUSEBUTTONUP and self.homepage.buttons_hover_states['about']:
                    self.about = About(self.screen)
                    self.running = waiting = self.about.handle_input()
                if event.type == pg.MOUSEBUTTONUP and self.homepage.buttons_hover_states['gitlab']:
                    self.homepage.open_gitlab()
                if event.type == pg.MOUSEBUTTONUP and self.homepage.buttons_hover_states['exit']:
                    self.running = self.playing = waiting = False
            pg.mixer.music.set_volume(get_volume())

    def draw_text(self, text: str, size: int, color: Color, x: int, y: int)-> None:
        """
        Draws basic text in the screen
        """
        font = pg.font.Font(self.font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)
