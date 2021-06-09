from abc import ABC, ABCMeta
from pygame.math import Vector2
from material import Material



class Tile(ABC):
    texture: str = 'noTexture.png'
    material: Material = Material.AIR

    def __init__(self, location: list):
        if type(location[0]) == int and type(location[1]) == int:
            self.location = Vector2(location)
        else:
            raise TypeError("Incorrect location encoding")

    def getOnScreenPosition(self, cameraOffset: list) -> tuple:
        return self.location[0]*50 + cameraOffset[0], self.location[1]*50+cameraOffset[1]

    def destroy(self, world):
        for index, me in enumerate(world.tiles):
            if self.location == me.location:
                world.tiles.pop(index)
                world.tileLocationCache.pop(index)
                return
        raise ReferenceError("Couldn't find tile from world.")


class oreNode(Tile):
    texture = 'Node.png'
    material = Material.ORENODE


class storage(Tile):
    texture = 'Small_Crate.png'
    material = Material.STORAGE

    def __init__(self, location):
        super().__init__(location)
        self.hasMiner: bool = False


class plant(Tile):
    texture = 'plant4.png'
    material = Material.PLANT


class barrel(Tile):
    texture = 'barrel.png'
    material = Material.BARREL
