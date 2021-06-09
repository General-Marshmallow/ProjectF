from world import World
from pygame import mouse
from material import Material, Resource


class Player:

    def __init__(self):
        self.resources = {}
        


    def addResource(self, resource: Resource, amount: int):
        if resource in self.resources:
            self.resources[resource] += amount
        else:
            self.resources[resource] = amount

    def getMouseMapPos(self, cameraOffset: list) -> tuple:
        mousepos = mouse.get_pos()
        return ((mousepos[0] - cameraOffset[0]) // 50), ((mousepos[1] - cameraOffset[1]) // 50)

    # Returns game.tiles index that the mouse is hovering over
    def getTileIndexUnderMouse(self, world: World, cameraOffset: list) -> int:
        for index, tileLoc in enumerate(world.tileLocationCache):
            if tileLoc == self.getMouseMapPos(cameraOffset):
                return index
        return -1

    def getMaterialUnderMouse(self, world: World, cameraOffset: list) -> Material:
        if self.getTileIndexUnderMouse(world, cameraOffset) == -1: return Material.AIR
        return world.tiles[self.getTileIndexUnderMouse(world, cameraOffset)].material
