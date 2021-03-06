import logging
import math
import random
from pathlib import PurePath

import pygame as pg

from project.constants import (Color, DEFAULT_FONT_NAME, HEIGHT, PATH_IMAGES, POWERUPS, POWERUP_EFFECT,
                               PROJECTILE_IMAGE_NAME, WIDTH)
from project.sprites.sprite_internals import Physics
from project.ui.sheet import Sheet
from project.ui.timer import Timer

logger = logging.getLogger('last_judgment_logger')


class Projectile(Physics, pg.sprite.Sprite):
    """Basic Projectile Sprite

    Blaster 0 -> Green
    Blaster 1 -> Blue_marine
    Blaster 2 -> Yellow
    Blaster 3 -> Orange
    Blaster 4 -> Red
    Blaster 5 -> Purple  For double shots
    Blaster 6 -> Blue
    """
    blasters = {'green': pg.image.load(str(PurePath(PATH_IMAGES).joinpath(PROJECTILE_IMAGE_NAME[0]))),
                'blue_marine': pg.image.load(str(PurePath(PATH_IMAGES).joinpath(PROJECTILE_IMAGE_NAME[1]))),
                'yellow': pg.image.load(str(PurePath(PATH_IMAGES).joinpath(PROJECTILE_IMAGE_NAME[2]))),
                'orange': pg.image.load(str(PurePath(PATH_IMAGES).joinpath(PROJECTILE_IMAGE_NAME[3]))),
                'red': pg.image.load(str(PurePath(PATH_IMAGES).joinpath(PROJECTILE_IMAGE_NAME[4]))),
                'purple': pg.image.load(str(PurePath(PATH_IMAGES).joinpath(PROJECTILE_IMAGE_NAME[5]))),
                'blue': pg.image.load(str(PurePath(PATH_IMAGES).joinpath(PROJECTILE_IMAGE_NAME[6])))
                }

    def __init__(self, game, owner, angle: float, damage: int=2, penetration: int=0, spawn_point=None):
        super().__init__()
        self.game = game
        self.owner = owner
        if owner.evil:
            self.add(self.game.all_sprites, self.game.enemy_projectiles)
        else:
            self.add(self.game.all_sprites, self.game.others)

        self.angle = angle
        self.damage = damage
        self.penetration = penetration

        if self.owner.type == 1:
            self.image = Projectile.blasters['green']
        if self.owner.type == 5:
            self.image = Projectile.blasters['purple']
        if self.owner.type == 4:
            self.image = Projectile.blasters['red']
        if self.owner.type == 6:
            self.image = Projectile.blasters['orange']

        self.image = pg.transform.scale(self.image, (round(self.owner.projectile_scale*90),
                                                     round(self.owner.projectile_scale*40)))
        self.image = pg.transform.rotate(self.image, angle * 180 / math.pi)
        if spawn_point is None:
            self.pos = owner.rect.midright
        else:
            self.pos = spawn_point

        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pg.mask.from_surface(self.image)

    def destroy(self):
        # TODO FIX THIS BUG

        self.kill()
        try:
            self.owner.projectiles.remove(self)
        except ValueError:
            pass

    def update(self):
        """
        Overrides pg.sprite.Sprite update function and gets called in /game.py/Game class

        Basic projectiles phisics, it supports multi directional projectiles
        """

        self.friction = 0.012
        super().update()

        self.vel.y = -10 * math.sin(self.angle)
        self.vel.x = 10 * math.cos(self.angle)

        self.max_speed = 20

        if self.pos.y > HEIGHT:
            self.destroy()
        if self.pos.y < 0:
            self.destroy()
        if self.pos.x > WIDTH:
            self.destroy()
        if self.pos.x < 0:
            self.destroy()


class Item(pg.sprite.Sprite):
    """Represents Items such as drops

    red: + soft hp
    pink: + full hp
    purple: temporary double shot x seconds
    blue: + max shield
    yellow: temporary immunity
    white: temporary extra fire rate
    green: + armor
    w_green: permanent extra damage
    """
    def __init__(self, game, color: str = None):
        super().__init__()
        self.game = game
        self.color = color
        self.add(self.game.all_sprites, self.game.powerups)

        self.color_location = {'red': (0, 0, 130, 130),
                               'pink': (129, 0, 130, 130),
                               'purple': (255, 0, 130, 130),
                               'blue': (385, 0, 130, 130),
                               'yellow': (0, 130, 130, 130),
                               'white': (129, 130, 130, 130),
                               'green': (255, 130, 130, 130),
                               'w_green': (385, 130, 130, 130)
                               }
        if self.color is None:
            self.type = random.choices(
                ['red', 'pink', 'purple', 'blue', 'yellow', 'white', 'green', 'w_green'],
                weights=[15, 5, 3, 7, 3, 3, 10, 10],
                k=1
            )[0]
        else:
            self.type = self.color

        self.image = Sheet(str(PurePath(PATH_IMAGES).joinpath(POWERUPS))).get_image(*self.color_location[self.type])
        self.image.set_colorkey(Color.black)
        self.image = pg.transform.scale(self.image, (35, 35))
        self.rect = self.image.get_rect()

        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = (random.randint(200, 700), random.randint(200, 700))
        logger.debug(f'Spawned a {self.type} powerup at {self.rect.center}')

    def apply_powerup(self, character: pg.sprite.Sprite):
        """
        Calls Character functions that handle the powerup effects
        :param character: pg.sprite.Sprite (Character)
        """
        Timer(self.game, 5, 100, 100, DEFAULT_FONT_NAME, 25, True, _type=self.type)
        if self.type in ['purple', 'yellow', 'white']:
            Timer(self.game, POWERUP_EFFECT[self.type], 15, 20, DEFAULT_FONT_NAME, 25, _type=self.type)

        if self.type == 'red':
            character.heal(POWERUP_EFFECT[self.type])
            character.image_code = 2
        if self.type == 'pink':
            character.heal(POWERUP_EFFECT[self.type])
            character.image_code = 3
        if self.type == 'purple':
            character.double_shot(POWERUP_EFFECT[self.type])
            character.image_code = 4
        if self.type == 'blue':
            character.heal_shield()
        if self.type == 'yellow':
            character.immune(POWERUP_EFFECT[self.type])
            character.image_code = 5
        if self.type == 'white':
            character.fast_fire(POWERUP_EFFECT[self.type])
            character.image_code = 6
        if self.type == 'green':
            if character.armor >= 4:
                return
            character.armor += POWERUP_EFFECT[self.type]
            character.image_code = 7
        if self.type == 'w_green':
            character.attack += POWERUP_EFFECT[self.type]
            character.image_code = 8
