import math
from pathlib import PurePath

import pygame as pg
from pygame.math import Vector2 as Vec

from project.constants import Color, HEALTHBAR, PATH_IMAGES, SHIELDBAR


class StaticHealthbar:
    """
    Represents the static healthbar, art and functionality.
    """

    def __init__(self, game, owner, x: int, y: int, width=None):
        super().__init__()
        self.game = game
        self.owner = owner
        self.screen = self.game.screen

        self.game.nonsprite.add(self)
        self.x = x
        self.y = y
        self.width = width

        self.image_hp = pg.image.load(str(PurePath(PATH_IMAGES).joinpath(HEALTHBAR))).convert_alpha()
        self.image_hp = pg.transform.scale(self.image_hp, (250, 100))
        self.image_hp.set_colorkey(Color.black)
        self.rect_hp = self.image_hp.get_rect()
        self.rect_hp.center = Vec(200, 40)

        self.image_sp = pg.image.load(str(PurePath(PATH_IMAGES).joinpath(SHIELDBAR))).convert_alpha()
        self.image_sp = pg.transform.scale(self.image_sp, (250, 100))
        self.image_sp.set_colorkey(Color.black)
        self.rect_sp = self.image_sp.get_rect()
        self.rect_sp.center = Vec(410, 40)

    def draw(self)-> None:

        self.hp = self.owner.health
        self.sp = self.owner.shield

        hp_color = Color.pure_green
        sp_color = Color.pure_blue
        if self.hp <= 0:
            self.hp = 0

        if self.hp < 40:
            hp_color = Color.red

        if self.hp == 0:
            hp_color = Color.black
        if self.sp == 0:
            sp_color = Color.black

        pg.draw.rect(self.screen, hp_color, [100, 20, self.hp*1.75, 30])

        if self.sp is not None:
            pg.draw.rect(self.screen, sp_color, [310, 20, self.sp*2.2, 30])
        self.screen.blit(self.image_hp, self.rect_hp)
        self.screen.blit(self.image_sp, self.rect_sp)


class DynamicHealthbar(pg.sprite.Sprite):
    """
    Represent a Healthbar that can be moved.

    It's a sprite unlike static Healthbar because only Sprite objects can be moved, as its main
    functionality and nature  has nothing to do with Sprites, it's on ui/ rather sprites/ folder.
    """

    def __init__(self, game, owner):
        super().__init__()
        self.game = game
        self.add(self.game.all_sprites)
        self.owner = owner
        self.screen = self.game.screen
        self.image = pg.Surface((100, 20))

        self.height_scale = {0: 5, 1: 10, 2: 5, 4: 5, 6: 5}

        self.rect = self.image.get_rect()

        self.pos = Vec(self.owner.pos.x, self.owner.pos.y)

    def update(self)-> None:
        if self.owner.health != 20:
            if self.owner.health < 0:
                self.owner.health = 0
            self.image = pg.Surface(
                (math.ceil(self.owner.health/self.owner.max_health*self.owner.rect.width * 0.8),
                 self.height_scale[self.owner.type]))
            if self.owner.health > self.owner.max_health * 0.4:
                self.image.fill(Color.pure_green)
            else:
                self.image.fill(Color.red)

            self.pos.x = self.owner.pos.x + 30
            self.pos.y = self.owner.pos.y + 32
            self.rect.midtop = self.owner.rect.midbottom + Vec(self.owner.rect.width * 0.1, 5)

            self.game.screen.blit(self.image, self.rect)
