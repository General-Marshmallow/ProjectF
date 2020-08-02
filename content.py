from enum import Enum
from abc import ABC, abstractmethod, abstractproperty


class Layer(Enum):
    TerrainLayer = 0
    BackgroundLayer = 1
    MainLayer = 2
    DecorationLayer = 3


render_order = [Layer.TerrainLayer, Layer.BackgroundLayer, Layer.MainLayer, Layer.DecorationLayer]


class Direction(Enum):
    DU = 3
    LR = 4
    UD = 5
    RL = 6


# TODO Reminder - Don't overuse enums
# TODO Reminder - Keep DataTag and defaults near each-other
class DataTag(Enum):
    direction = 7
    contents = 8
    age = 9
    textureIndex = 10
    tileType = 11


# DO NOT INCLUDE DataTag.tileType
defaults = {
    DataTag.direction: Direction.DU,
    DataTag.contents: None,
    DataTag.age: 0,
    DataTag.textureIndex: 0,
    DataTag.tileType: None
}


# Functionality classes
# =====================
class TerrainLayerTile(ABC):
    tileLayer = Layer.TerrainLayer


class BackgroundTile(ABC):
    tileLayer = Layer.BackgroundLayer


class MainLayerTile(ABC):
    tileLayer = Layer.MainLayer


class DecorationLayerTile(ABC):
    tileLayer = Layer.DecorationLayer


# =====================

layerDictionary = {
        Layer.BackgroundLayer: BackgroundTile,
        Layer.MainLayer: MainLayerTile,
        Layer.DecorationLayer: DecorationLayerTile
    }
oppositeDirDict = {
    Direction.UD: Direction.DU,
    Direction.DU: Direction.UD,
    Direction.LR: Direction.RL,
    Direction.RL: Direction.LR
}
dirDict = {
    Direction.UD: (0, 1),
    Direction.DU: (0, -1),
    Direction.LR: (1, 0),
    Direction.RL: (-1, 0)
}


class Tile(ABC):
    tileLayer: Layer = None  # Must be implemented
    texture: list = ['Empty.png']  # Must be implemented
    itemTexture: list = ['Empty.png']  # Must be implemented
    dataTags: list = []  # Must be implemented todo Make textureIndex default for Tile subclasses
    # The first dataTag of every Tile subclass is DataTag.tileClass but it's not included in Tile subclass dataTags

    # Probably a stupid idea buuuut.....
    # Returns a function???
    """
    @abstractmethod
    def script(self, gridBlockInstance):
        pass
    """


class Item(ABC):
    itemTexture = ['Empty.png']


class FarmLand(BackgroundTile, Tile):
    texture = ['FarmLand.png']
    itemTexture = ['FarmLand.png']
    dataTags = [DataTag.tileType, DataTag.textureIndex]


class FarmLandWet(BackgroundTile, Tile):
    texture = ['FarmLandWet.png']
    itemTexture = ['FarmLandWet.png']
    dataTags = [DataTag.tileType, DataTag.textureIndex]


class Plant(MainLayerTile, Tile):
    texture = ['Plant1.png', 'Plant2.png', 'Plant3.png', 'Plant4.png']
    dataTags = [DataTag.tileType, DataTag.textureIndex, DataTag.age]


class ConveyorBelt(MainLayerTile, Tile):
    age = 0  # GLOBAL (0-3) for texture update
    texture = ['ConveyorBeltDU1.png']
    itemTexture = ['ConveyorBeltItem.png']
    dataTags = [DataTag.tileType, DataTag.textureIndex, DataTag.contents, DataTag.direction]

    """
    growthDict = {
        Direction.DU:
            ('ConveyorBeltDU1.png',
             'ConveyorBeltDU2.png',
             'ConveyorBeltDU3.png',
             'ConveyorBeltDU4.png'),
        Direction.UD:
            ('ConveyorBeltUD1.png',
             'ConveyorBeltUD2.png',
             'ConveyorBeltUD3.png',
             'ConveyorBeltUD4.png'),
        Direction.LR:
            ('ConveyorBeltLR1.png',
             'ConveyorBeltLR2.png',
             'ConveyorBeltLR3.png',
             'ConveyorBeltLR4.png'),
        Direction.RL:
            ('ConveyorBeltRL1.png',
             'ConveyorBeltRL2.png',
             'ConveyorBeltRL3.png',
             'ConveyorBeltRL4.png'),
    }
    
    def __init__(self, direction: Direction):
        self.direction = direction
        self.contents = None  # ItemStack
        self.input_this_frame = False  # if something has already been put on this conveyor this frame
        if direction == Direction.DU:
            self.texture = 'ConveyorBeltDU1.png'
    elif direction == Direction.LR:
            self.texture = 'ConveyorBeltLR1.png'
        elif direction == Direction.UD:
            self.texture = 'ConveyorBeltUD1.png'
        elif direction == Direction.RL:
            self.texture = 'ConveyorBeltRL1.png'
    """


class Storage(MainLayerTile, Tile):
    texture = ['Storage.png']
    itemTexture = ['StorageItem.png']
    dataTags = [DataTag.tileType, DataTag.textureIndex, DataTag.contents]
    """
    def __init__(self, direction: Direction, contents=None):
        if contents is None:
            contents = []
        self.contents = contents
        self.direction = direction
    """


class Pavement(BackgroundTile, Tile):
    texture = ['Pavement.png']
    itemTexture = ['Pavement.png']
    dataTags = [DataTag.tileType, DataTag.textureIndex]


class Terrain(TerrainLayerTile, Tile):
    texture = ['Terrain.png']
    itemTexture = ['Terrain.png']
    dataTags = [DataTag.tileType, DataTag.textureIndex]


class OreNode(BackgroundTile, Tile):
    texture = ['Node.png']
    itemTexture = ['Node.png']
    dataTags = [DataTag.tileType, DataTag.textureIndex]


class Seed(Item):
    itemTexture = ['Seed.png']


class Fertilizer(Item):
    itemTexture = ['Pesticide.png']


class Select(Item):
    itemTexture = ['SelectItem.png']


class Trash(Item):
    itemTexture = ['Trash.png']

