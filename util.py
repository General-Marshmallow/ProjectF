from pygame import image, transform
from functools import lru_cache
from tile import Tile
from material import Material
from world import World
from player import Player


class MapCoordinate:
    def __init__(self, x, y):
        if type(x) == int and type(y) == int:
            self.location = (x, y)
        else:
            raise TypeError("Initiated MapCoordinate with incorrect arguments")

    def __repr__(self):
        return self.location

    def __str__(self):
        return self.location

    def __getitem__(self, key):
        return self.location[key]

    def __eq__(self, other):
        if type(other) == type(self) and self.location == other.location:
            return True
        return False


class Util:

    _scrollMenu = [Material.AIR, Material.ORENODE, Material.PLANT, Material.STORAGE, Material.BARREL]
    _currentMenuSlot = 0

    @staticmethod
    @lru_cache(50)
    def loadTexture(textureName: str):
        return transform.scale(image.load('Assets/' + textureName), (200, 200))

    @staticmethod
    @lru_cache(50)
    def loadTextureRotated(textureName: str, angle: float):
        return transform.rotate(Util.loadTexture(textureName), angle)

    @staticmethod
    def lots(tile: Tile, cameraOffset: list): # Load offset tile surface
        return (Util.loadTexture(tile.texture), (tile.location[0] * 50 + cameraOffset[0], tile.location[1] * 50 + cameraOffset[1]))

    def isValidCoordinate(self, coordinate: list) -> bool:
        return len(coordinate) == 2 and type(coordinate[0]) == 0 and type(coordinate[1]) == 0

    def getScrollMaterial(self):
        return self._scrollMenu[self._currentMenuSlot]

    def updateScrollMenuSelectedSlot(self, direction: int):
        if 0 <= self._currentMenuSlot+direction < len(self._scrollMenu):
            self._currentMenuSlot += direction

