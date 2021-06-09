from abc import ABC, abstractmethod
from util import *
from astar_python.astar import Astar
from pygame.math import Vector2
import random


class Entity(ABC):
    texture = 'noTextureEntity.png'

    def __init__(self, position: list):
        if type(position[0]) == int and type(position[1]) == int:
            self.position = Vector2(position)
        else:
            raise TypeError("Incorrect location encoding")

    def tick(self):
        pass


class Rover(Entity):
    texture = 'rover.png'

    def __init__(self, position):
        super().__init__(position)
        self.x = 0
        self.nextbeat = 0

    def tick(self):
        self.x -= 1
        if self.x == 0:
            self.x = random.randrange(start= 10, stop= 40, step= 2)
            return

