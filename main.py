import sys
from abc import ABC
from functools import lru_cache

import pygame
from pygame.locals import *
from pygame.image import *
import pytmx
import pickle

# move around with arrow keys
# numbers 1-4 are for the inventory
# F1 to escape
# ESC to deselect a tile

# Initialization
pygame.init()
pygame.font.init()
flags = DOUBLEBUF
screen = pygame.display.set_mode((800, 600), flags)
pygame.display.set_caption("Keep going! | F1 to exit")
clock = pygame.time.Clock()
mapData = pytmx.TiledMap('gameMap.tmx')
# Some variables
renderSize = 50
cameraOffset = [250, 200]
screenRect = pygame.Rect((0, 0), (800, 600))


# todo Are the functionality classes really necessary?
# Functionality classes
# =====================
class BackgroundTile:
    tileLayer = 'Background'


class MainLayerTile:
    tileLayer = 'MainLayer'


class DecorationLayerTile:
    tileLayer = 'Decoration'


# Only accessible by the game
class TopLayerTile:
    tileLayer = 'TopLayer'


class ScriptableObject:
    scriptable = True
# =====================


class Game(ABC):
    # renderList is rebuilt every frame, if something is removed from gameObjects, it no longer exists
    # todo Add layers to the game
    gameObjects = []  # Holds all tiles
    screenObjects = []  # Holds gameObjects that collide with the screen
    renderList = []  # Holds tiles to be rendered next frame
    selectedTile = None
    pressedKey = {
        pygame.K_ESCAPE: False,
        pygame.K_F1: False,
        pygame.K_UP: False,
        pygame.K_DOWN: False,
        pygame.K_LEFT: False,
        pygame.K_RIGHT: False,
        pygame.K_1: False,
        pygame.K_2: False,
        pygame.K_3: False,
        pygame.K_4: False
    }

    # todo Fix this mess of staticmethods and their naming

    # returns up-scaled pygame image
    @staticmethod
    @lru_cache(maxsize=10)
    def _tileWrapper(textureName):
        return pygame.transform.scale(pygame.image.load('Assets/' + textureName), (renderSize, renderSize))

    @staticmethod
    def _imageWrapper(textureName, ):
        return pygame.image.load('Assets/' + textureName)

    @staticmethod
    def tileGameObjectToRender(textureName, pos=(0, 0)):
        Game.renderList.append(
            (Game._tileWrapper(textureName), (pos[0] * renderSize + cameraOffset[0],
                                             pos[1] * renderSize + cameraOffset[1]),)
        )

    @staticmethod
    def tileRenderObjectToRender(textureName, pos=(0, 0)):
        Game.renderList.append(
            (Game._tileWrapper(textureName), (pos[0], pos[1]))
        )

    @staticmethod
    def tile_gameObject_to_screen_rect(pos=(0, 0)):
        return pygame.Rect(
            (pos[0] * renderSize + cameraOffset[0], pos[1] * renderSize + cameraOffset[1]),
            (renderSize, renderSize))

    @staticmethod
    def image_to_screen(texture_name, pos):
        image = pygame.image.load('Assets/' + texture_name)
        Game.renderList.append(
            (pygame.transform.scale(image, (round(image.get_width()*(renderSize/32)), round(image.get_height()*(renderSize/32)))), pos))

    @staticmethod
    def position_contains(pos, obj):
        for gameObject in Game.gameObjects:
            if gameObject.pos == pos and isinstance(gameObject, obj):
                return True
        return False

    @staticmethod
    def position_contains_return_index(pos, obj):
        for count, gameObject in enumerate(Game.gameObjects):
            if gameObject.pos == pos and isinstance(gameObject, obj):
                return count
        return -1


class GameObject(ABC):
    # Default values of a gameObject
    tileLayer = 'MainLayer'
    scriptable = False
    # Must be implemented
    texture = None

    def __init__(self, x=0, y=0):
        self.pos = [x, y]
        Game.gameObjects.append(self)


class Tile(GameObject):
    pass


class Item:
    stackable = False
    texture = 'Empty.png'


class FarmLand(Tile, BackgroundTile):
    texture = 'FarmLand.png'


class FarmLandWet(Tile, BackgroundTile):
    texture = 'FarmLandWet.png'


class Plant(Tile, MainLayerTile):
    texture = 'Plant1.png'
    growthTextures = [
        'Plant1.png',
        'Plant2.png',
        'Plant3.png',
        'Plant4.png'
    ]

    def __init__(self, x=0, y=0, age=0):
        super().__init__(x, y)
        self.age = age


class ConveyorBelt(Tile, MainLayerTile):
    age = 0  # (0-3) for texture update
    texture = 'ConveyorBelt1.png'
    growthTextures = [
        'ConveyorBelt1.png',
        'ConveyorBelt2.png',
        'ConveyorBelt3.png',
        'ConveyorBelt4.png'
    ]

    def __init__(self, x, y, direction):
        self.direction = direction
        super().__init__(x, y)


class Pavement(Tile, BackgroundTile):
    texture = 'Pavement.png'


class Seed(Item):
    texture = 'Seed.png'


class Fertilizer(Item):
    texture = 'Pesticide.png'


class Select(Item):
    texture = 'SelectItem.png'


class Trash(Item):
    texture = 'Trash.png'


class Empty(Item):
    pass


# todo setup Tile classes in such a way that these separate Item classes are not necessary
class ConveyorBeltItem(Item):
    texture = 'ConveyorBeltItem.png'


# Unused
class ItemStack:
    def __init__(self, item, count):
        self.item = item
        self.count = count


class Inventory(ABC):
    inventory = {
        0: Empty,
        1: Empty,
        2: Empty,
        3: Empty
    }
    selected_slot = 0
    screen_pos = (300, 540)

    @staticmethod
    def get_selected_slot_pos():
        return Inventory.screen_pos[0] + Inventory.selected_slot * 50, Inventory.screen_pos[1]

    @staticmethod
    def get_slot_screen_pos(slot):
        return Inventory.screen_pos[0] + slot * 50, Inventory.screen_pos[1]

    @staticmethod
    def get_selected_item():
        return Inventory.inventory[Inventory.selected_slot]


tileDictionary = {
    1: FarmLandWet,
    2: Pavement,
    3: FarmLand,
    4: Plant
}
# ===================================
# _______________SETUP_______________
"""
# Puts map tiles to gameObjects list
for layer in mapData.layers:
    for x, y, id in layer:
        if not id == 0:
            if id in tileDictionary:
                tileDictionary[id](x, y)
            else:
                raise NotImplementedError
"""
# pickle.dump(Game.gameObjects, open('map.pickle', 'wb'))
Game.gameObjects = (pickle.load(open('map.pickle', 'rb')))


Inventory.inventory = {0: Seed,
                       1: Fertilizer,
                       2: Trash,
                       3: ConveyorBeltItem}


while True:
    Game.renderList.clear()
    Game.screenObjects.clear()

    # Exit game
    if Game.pressedKey[pygame.K_F1]:
        pickle.dump(Game.gameObjects, open('map.pickle', 'wb'))
        pygame.quit()
        sys.exit()

    # Pressed keys event checking
    for event in pygame.event.get():
        try:
            if event.key in Game.pressedKey:
                if event.type == pygame.KEYDOWN:
                    Game.pressedKey[event.key] = True
                if event.type == pygame.KEYUP:
                    Game.pressedKey[event.key] = False
        except AttributeError:
            continue

    # Camera scrolling with arrow keys for debug purposes
    if Game.pressedKey[pygame.K_LEFT]:
        cameraOffset[0] += 10
    if Game.pressedKey[pygame.K_RIGHT]:
        cameraOffset[0] -= 10
    if Game.pressedKey[pygame.K_UP]:
        cameraOffset[1] += 10
    if Game.pressedKey[pygame.K_DOWN]:
        cameraOffset[1] -= 10

    # Rebuilding screenObjects and renderList
    for gameObject in Game.gameObjects:
        objRect = Game.tile_gameObject_to_screen_rect(gameObject.pos)
        if screenRect.colliderect(objRect):
            Game.screenObjects.append(gameObject)
            Game.tileGameObjectToRender(gameObject.texture, gameObject.pos)

    for obj in Game.screenObjects:
        # todo move to Plant class
        # Plant growth
        if isinstance(obj, Plant):
            obj.age += 1 if obj.age < 350 else obj.age
            obj.texture = obj.growthTextures[1] if obj.age > 100 else obj.texture
            obj.texture = obj.growthTextures[2] if obj.age > 200 else obj.texture
            obj.texture = obj.growthTextures[3] if obj.age > 300 else obj.texture

        # todo Move to ConveyorBelt class
        # Conveyor belt texture update
        if isinstance(obj, ConveyorBelt):
            ConveyorBelt.texture = ConveyorBelt.growthTextures[ConveyorBelt.age]
            ConveyorBelt.age += 1
            ConveyorBelt.age = 0 if ConveyorBelt.age == 3 else ConveyorBelt.age

        # Mouse collide script
        collideRect = Game.tile_gameObject_to_screen_rect(obj.pos)
        if collideRect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
            if pygame.mouse.get_pressed()[0] == 1:
                # v======v mouse pressed and located v======v
                # todo Organize all inventory based item scripts to their own classes

                # seed planting
                if Inventory.get_selected_item() == Seed:
                    # todo Make a tile placement function that does the first check automatically *functionality classes
                    if not Game.position_contains(obj.pos, Plant) and Game.position_contains(obj.pos, FarmLandWet):
                        Plant(obj.pos[0], obj.pos[1])

                # plant removal
                if Inventory.get_selected_item() == Trash:
                    if Game.position_contains_return_index(obj.pos, Plant) != -1:
                        Game.gameObjects.pop(Game.position_contains_return_index(obj.pos, Plant))

                # Selecting tile
                if Inventory.get_selected_item() == Select:
                    Game.selectedTile = obj.pos

                # Conveyor belt placing
                if Inventory.get_selected_item() == ConveyorBeltItem:
                    print('cb')
                    ConveyorBelt(obj.pos[0], obj.pos[1], 'NS')

            # v======v mouse located v======v

            # Tile hover effect rendering
            Game.tileGameObjectToRender('HoverEffect.png', obj.pos)

    Game.selectedTile = None if Game.pressedKey[pygame.K_ESCAPE] or Inventory.get_selected_item() != Select else Game.selectedTile
    # Tile select effect rendering
    try: Game.tileGameObjectToRender('SelectEffect.png', Game.selectedTile)
    except TypeError: pass

    # Inventory
    Game.image_to_screen('Inventory.png', Inventory.screen_pos)
    Game.image_to_screen('InventorySelect.png', Inventory.get_selected_slot_pos())
    Inventory.selected_slot = 0 if Game.pressedKey[pygame.K_1] else Inventory.selected_slot
    Inventory.selected_slot = 1 if Game.pressedKey[pygame.K_2] else Inventory.selected_slot
    Inventory.selected_slot = 2 if Game.pressedKey[pygame.K_3] else Inventory.selected_slot
    Inventory.selected_slot = 3 if Game.pressedKey[pygame.K_4] else Inventory.selected_slot
    for key in Inventory.inventory:
        if not Inventory.inventory[key] == Empty:
            Game.image_to_screen(Inventory.inventory[key].texture, Inventory.get_slot_screen_pos(key))

    # debug fps
    print("fps: "+str(round(clock.get_fps()))+" | objects: "+str(len(Game.renderList)))

    # The actual blitting part
    screen.fill(pygame.Color("Black"))
    screen.blits(Game.renderList)

    # Screen refresh
    pygame.display.flip()
    clock.tick(30)
