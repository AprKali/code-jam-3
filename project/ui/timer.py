import pygame as pg

from project.constants import Color


class Timer:

    def __init__(self, screen: pg.Surface, time: int, x: int, y: int, font: str, font_size:str):
        self.screen = screen

        self.x = x
        self.y = y

        self.font = pg.font.SysFont(font, font_size)
        self.time = time
        self.start = pg.time.get_ticks()

    def draw(self)->None:

        self.current = (pg.time.get_ticks() - self.start) // 1000

        if self.current <= self.time:
            self.text = self.font.render(self.min_sec(self.time - self.current), True, Color.white)
        else:
            self.text = self.font.render("0:00", True, Color.white)

        self.screen.blit(self.text, (self.x, self.y))

    def min_sec(self, sec: int)->str:
        return f"{int((sec - sec % 60) / 60)}:{sec % 60:02}"
