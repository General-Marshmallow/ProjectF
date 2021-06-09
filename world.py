from abc import ABC
from tile import *
from entity import Entity
from material import Material
# World > chunk > tile.py


class World:

    def __init__(self):
        self.tiles = []
        self.tileLocationCache: list = []
        self.entities = []
        self.tileSubClasses = Tile.__subclasses__()

    def placeTile(self, newTileObject: Tile, override=False):
        location = newTileObject.location  # local is faster?
        for index, tileLocation in enumerate(self.tileLocationCache):
            if tileLocation == location:
                if override:
                    self.tiles[index] = newTileObject
                return
        self.tiles.append(newTileObject)
        self.tileLocationCache.append(newTileObject.location)

    def placeTileByMaterial(self, material: Material, location: list):
        for tileClass in self.tileSubClasses:
            if tileClass.material == material:
                self.placeTile(tileClass(location))


    def spawnEntity(self, newEntityObject: Entity):
        self.entities.append(newEntityObject)
