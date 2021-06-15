from abc import ABC, abstractmethod
from astar_python.astar import Astar
from pygame.math import Vector2
import random
from util import *


class Entity(ABC):
    texture = 'noTextureEntity.png'
    world = None  # Global world object refrence, must be updated every frame

    def __init__(self, position: list):
        if type(position[0]) == int and type(position[1]) == int:
            self.position = Vector2(position)
        else:
            raise TypeError("Incorrect location encoding")

    def tick(self):  # Called 10 times per second
        pass

    def update(self):  # Called every frame
        pass


class Rover(Entity):

    texture = 'rover_up.png'
    moveSpeed = 0.2

    def __init__(self, position):
        super().__init__(position)
        self.actionQueue = [] # List of function calls
        self.hasMoved = False
        self.hasCompletedMove = True
        self.direction = 'up'

    def moveup(self):
        self.position[1] -= self.moveSpeed
    def moveright(self):
        self.position[0] += self.moveSpeed
    def moveleft(self):
        self.position[0] -= self.moveSpeed
    def movedown(self):
        self.position[1] += self.moveSpeed

    def moveTile(self, direction: str):
        self.hasCompletedMove = False
        for i in range(int(1/self.moveSpeed)):
            if direction == 'up':
                self.actionQueue.append(self.moveup)
            elif direction == 'down':
                self.actionQueue.append(self.movedown)
            elif direction == 'left':
                self.actionQueue.append(self.moveleft)
            elif direction == 'right':
                self.actionQueue.append(self.moveright)

    def tick(self):
        if self.hasCompletedMove:
            perspective = None
            if self.direction == 'left':
                perspective = Vector2(-1, 0)
            elif self.direction == 'right':
                perspective = Vector2(1, 0)
            elif self.direction == 'up':
                perspective = Vector2(0, -1)
            elif self.direction == 'down':
                perspective = Vector2(0, 1)

            if not Entity.world.getTile(Vector2(self.position + perspective)) == None:
                self.direction = random.choice(('left','right', 'up', 'down'))
                self.tick()
            else:
                self.moveTile(self.direction)
                self.hasCompletedMove = False

            self.texture = 'rover_'+self.direction+'.png'


    def update(self):
        if len(self.actionQueue) > 0:
            self.actionQueue[0]()
            self.actionQueue.pop(0)
        else:
            self.hasCompletedMove = True