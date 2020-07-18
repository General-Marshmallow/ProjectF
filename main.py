import sys
from abc import ABC
from functools import lru_cache

import pygame
from pygame.locals import *
import pytmx
import pickle

# move around with arrow keys
# numbers 1-4 are for the inventory
# F1 to escape
# F12 to reset gridBlocks (deletes and rebuilds map but not the tiles)
# ESC to deselect a tile
# r to rotate conveyorbelts

# Initialization
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((800, 600), flags=DOUBLEBUF)
pygame.display.set_caption("Keep going! | F1 to exit")
clock = pygame.time.Clock()
# Some variables
renderSize = 50  # replace this concept with a more dynamic scaling thing
cameraOffset = [0, 0]
screenRect = pygame.Rect((0, 0), (800, 600))
counter = 0  # TEMPORARY


# todo Replace counter system with custom pygame event
# todo Fix NoneType attribute errors

# Functionality classes
# =====================
class BackgroundTile(ABC):
    tileLayer = 'Background'  # Sensitive spelling


class MainLayerTile(ABC):
    tileLayer = 'Main'  # Sensitive spelling


class DecorationLayerTile(ABC):
    tileLayer = 'Decoration'  # Sensitive spelling


# =====================

layerDictionary = {
        'Background': BackgroundTile,
        'Main': MainLayerTile,
        'Decoration': DecorationLayerTile
    }
oppositeDirDict = {
    'UD': 'DU',
    'DU': 'UD',
    'LR': 'RL',
    'RL': 'LR'
}
dirDict = {
    'UD': (0, 1),
    'DU': (0, -1),
    'LR': (1, 0),
    'RL': (-1, 0)
}


class Game(ABC):
    GRID_SIZE = 16, 16
    # renderList is rebuilt every frame, if something is removed from gameObjects, it no longer exists
    grid = []  # Stores gridBlocks
    screenObjects = []
    renderList = []
    selectedTile = None
    pressedKey = {
        pygame.K_ESCAPE: False,
        pygame.K_F1: False,
        pygame.K_F12: False,
        pygame.K_UP: False,
        pygame.K_DOWN: False,
        pygame.K_LEFT: False,
        pygame.K_RIGHT: False,
        pygame.K_1: False,
        pygame.K_2: False,
        pygame.K_3: False,
        pygame.K_4: False,
        pygame.K_r: False
    }
    item_rotation = 0  # Keeping track of placing a rotated tile

    # returns up-scaled pygame image
    @staticmethod
    @lru_cache(maxsize=100)
    def tileWrapper(textureName):
        return pygame.transform.scale(pygame.image.load('Assets/' + textureName), (renderSize, renderSize))

    @staticmethod
    def render_with_game_coordinates(textureName, pos=(0, 0)):
        Game.renderList.append(
            (Game.tileWrapper(textureName), (pos[0] * renderSize + cameraOffset[0],
                                             pos[1] * renderSize + cameraOffset[1]),))

    @staticmethod
    def rect_with_game_coordinates(pos):
        return pygame.Rect(
            (pos[0] * renderSize + cameraOffset[0], pos[1] * renderSize + cameraOffset[1]),
            (renderSize, renderSize))

    @staticmethod
    def image_to_screen(texture_name, pos):
        image = pygame.image.load('Assets/' + texture_name)
        Game.renderList.append(
            (pygame.transform.scale(image, (
                round(image.get_width() * (renderSize / 32)), round(image.get_height() * (renderSize / 32)))), pos))

    @staticmethod
    def get_gridBlock_with_LC(self_object, perspectiveX, perspectiveY):
        for index, gb in enumerate(Game.grid):
            if gb == self_object:
                # found self
                try:
                    return Game.grid[index + perspectiveY * Game.GRID_SIZE[0] + perspectiveX]
                except IndexError:
                    return None


class GridBlock:
    def __init__(self, pos):
        self.pos = pos
        # GridBlock.layers contains objects
        self.layers = {
            BackgroundTile: None,
            MainLayerTile: None,
            DecorationLayerTile: None
        }
        Game.grid.append(self)

    def new_tile(self, tileSetup):  # tileSetup has to be a class instance setup
        if tileSetup.tileLayer == 'Background':
            self.layers[BackgroundTile] = tileSetup
        elif tileSetup.tileLayer == 'Main':
            self.layers[MainLayerTile] = tileSetup
        elif tileSetup.tileLayer == 'Decoration':
            self.layers[DecorationLayerTile] = tileSetup
        else:
            print('TileLayer error: ', tileSetup.tileLayer)

    def has_tile(self, tileType):  # tileType is a Class
        if isinstance(self.layers[layerDictionary[tileType.tileLayer]], tileType):
            return True
        return False

    def get_tile(self, tileType):
        if isinstance(self.layers[layerDictionary[tileType.tileLayer]], tileType):
            return self.layers[layerDictionary[tileType.tileLayer]]
        return None

    def remove_tile(self, tileType):
        for layer in self.layers:
            if isinstance(self.layers[layer], tileType):
                self.layers[layer] = None

    def remove_all(self):
        for layer in self.layers:
            self.layers[layer] = None

    def run_mouse_click_script(self):
        # todo Automate tile placing
        # todo Automate tile rotation
        # todo Create a script list for every gridBlock
        # seed planting
        if Inventory.get_selected_item() == Seed:
            if self.has_tile(FarmLandWet):
                self.new_tile(Plant())

        # plant removal
        if Inventory.get_selected_item() == Fertilizer:
            if self.has_tile(Plant):
                self.remove_tile(Plant)

        # tile removal
        if Inventory.get_selected_item() == Trash:
            self.remove_all()

        # Selecting tile
        if Inventory.get_selected_item() == Select:
            Game.selectedTile = self.pos

        # Conveyor belt placing
        if Inventory.get_selected_item() == ConveyorBelt:
            if self.layers[MainLayerTile] is None:
                if Game.item_rotation == 0:
                    self.new_tile(ConveyorBelt('DU'))
                elif Game.item_rotation == 1:
                    self.new_tile(ConveyorBelt('LR'))
                elif Game.item_rotation == 2:
                    self.new_tile(ConveyorBelt('UD'))
                elif Game.item_rotation == 3:
                    self.new_tile(ConveyorBelt('RL'))

        # Wet farmland placing
        if Inventory.get_selected_item() == FarmLandWet:
            self.new_tile(FarmLandWet())

        # Farmland placing
        if Inventory.get_selected_item() == FarmLand:
            self.new_tile(FarmLand())

        # Storage placing
        if Inventory.get_selected_item() == Storage:
            if self.layers[MainLayerTile] is None:
                if Game.item_rotation == 0:
                    self.new_tile(Storage('DU'))
                elif Game.item_rotation == 1:
                    self.new_tile(Storage('LR'))
                elif Game.item_rotation == 2:
                    self.new_tile(Storage('UD'))
                elif Game.item_rotation == 3:
                    self.new_tile(Storage('RL'))

        # TEMPORARY Seed->Storage
        if Inventory.get_selected_item() == Seed and self.has_tile(Storage):
            self.get_tile(Storage).contents = [ItemStack(Seed, 10)]

    def frame_tick(self):  # Run every frame (for texture updates)

        # Plant growth
        if self.has_tile(Plant):
            tile: Plant = self.layers[layerDictionary[Plant.tileLayer]]
            tile.age += 1 if tile.age < 350 else tile.age
            tile.texture = tile.growthTextures[1] if tile.age > 100 else tile.texture
            tile.texture = tile.growthTextures[2] if tile.age > 200 else tile.texture
            tile.texture = tile.growthTextures[3] if tile.age > 300 else tile.texture
            self.layers[MainLayerTile] = tile

        # Conveyor belt texture update
        if self.has_tile(ConveyorBelt):
            conveyor: ConveyorBelt = self.get_tile(ConveyorBelt)
            conveyor.texture = ConveyorBelt.growthDict[conveyor.direction][ConveyorBelt.age]

        # Conveyor belt item rendering
        if self.has_tile(ConveyorBelt):
            conveyor: ConveyorBelt = self.get_tile(ConveyorBelt)
            if conveyor.contents is not None:
                Game.render_with_game_coordinates(conveyor.contents.item.itemTexture, self.pos)

    def tick(self):  # Run less often

        # Items ConveyorBelt->ConveyorBelt
        if self.has_tile(ConveyorBelt):
            this_conveyor: ConveyorBelt = self.get_tile(ConveyorBelt)
            if this_conveyor.input_this_frame:
                this_conveyor.input_this_frame = False
            else:
                if this_conveyor.contents is not None:
                    if Game.get_gridBlock_with_LC(self, dirDict[this_conveyor.direction][0], dirDict[this_conveyor.direction][1]).has_tile(ConveyorBelt):
                        if not Game.get_gridBlock_with_LC(self, dirDict[this_conveyor.direction][0], dirDict[this_conveyor.direction][1]).get_tile(ConveyorBelt).direction == oppositeDirDict[this_conveyor.direction]:
                            other_conveyor: ConveyorBelt = Game.get_gridBlock_with_LC(self, dirDict[this_conveyor.direction][0], dirDict[this_conveyor.direction][1]).get_tile(ConveyorBelt)
                            try:
                                if other_conveyor.contents is None:
                                    # == item transfer == #
                                    other_conveyor.input_this_frame = True
                                    other_conveyor.contents = this_conveyor.contents
                                    this_conveyor.contents = None
                            except AttributeError:
                                pass

        # Items Storage->ConveyorBelt
        if self.has_tile(Storage):
            storage: Storage = self.get_tile(Storage)
            if storage.contents:  # if contents is not empty
                output_gridBlock: GridBlock = Game.get_gridBlock_with_LC(self, dirDict[storage.direction][0], dirDict[storage.direction][1])
                if output_gridBlock.has_tile(ConveyorBelt):  # if has a conveyorBelt
                    conveyorBelt: ConveyorBelt = output_gridBlock.get_tile(ConveyorBelt)
                    if conveyorBelt.contents is None and not storage.direction == oppositeDirDict[conveyorBelt.direction]:  # if conveyorBelt is empty and is not facing storage
                        # == item transfer == #
                        # Set conveyorBelt contents to the first Item in Storage contents
                        conveyorBelt.contents = ItemStack(storage.contents[0].item, 1)
                        # Subtract 1 from Storage contents
                        storage.contents[0] = storage.contents[0].return_itemStack_add(-1)
                        conveyorBelt.input_this_frame = True
                        if storage.contents[0] is None:
                            storage.contents.pop(0)


class Tile(ABC):
    tileLayer = None  # Must be implemented
    texture = None  # Must be implemented
    itemTexture = 'Empty.png'  # Must be implemented


class Item(ABC):
    stackable = False
    itemTexture = 'Empty.png'


class FarmLand(BackgroundTile, Tile):
    texture = 'FarmLand.png'
    itemTexture = 'FarmLand.png'


class FarmLandWet(BackgroundTile, Tile):
    texture = 'FarmLandWet.png'
    itemTexture = 'FarmLandWet.png'


class Plant(MainLayerTile, Tile):
    texture = 'Plant1.png'
    growthTextures = [
        'Plant1.png',
        'Plant2.png',
        'Plant3.png',
        'Plant4.png'
    ]

    def __init__(self, age=0):
        self.age = age


class ConveyorBelt(MainLayerTile, Tile):
    age = 0  # (0-3) for texture update
    texture = 'ConveyorBeltDU1.png'
    itemTexture = 'ConveyorBeltItem.png'

    growthDict = {
        'DU':
            ('ConveyorBeltDU1.png',
             'ConveyorBeltDU2.png',
             'ConveyorBeltDU3.png',
             'ConveyorBeltDU4.png'),
        'UD':
            ('ConveyorBeltUD1.png',
             'ConveyorBeltUD2.png',
             'ConveyorBeltUD3.png',
             'ConveyorBeltUD4.png'),
        'LR':
            ('ConveyorBeltLR1.png',
             'ConveyorBeltLR2.png',
             'ConveyorBeltLR3.png',
             'ConveyorBeltLR4.png'),
        'RL':
            ('ConveyorBeltRL1.png',
             'ConveyorBeltRL2.png',
             'ConveyorBeltRL3.png',
             'ConveyorBeltRL4.png'),
    }

    def __init__(self, direction):
        self.direction = direction
        self.contents = None  # ItemStack
        self.input_this_frame = False  # if something has already been put on this conveyor this frame


class Storage(MainLayerTile, Tile):
    texture = 'Storage.png'
    itemTexture = 'StorageItem.png'

    def __init__(self, direction, contents=None):
        if contents is None:
            contents = []
        self.contents = contents
        self.direction = direction


class Pavement(BackgroundTile, Tile):
    texture = 'Pavement.png'
    itemTexture = 'Pavement.png'


class Seed(Item):
    itemTexture = 'Seed.png'


class Fertilizer(Item):
    itemTexture = 'Pesticide.png'


class Select(Item):
    itemTexture = 'SelectItem.png'


class Trash(Item):
    itemTexture = 'Trash.png'


class ItemStack:
    def __init__(self, item, count):
        self.item = item
        self._count = count

    def return_itemStack_add(self, amount):
        if self._count + amount >= 1:
            return ItemStack(self.item, self._count + amount)
        return None

    def __str__(self):
        return str(self._count) + ", " + self.item.itemTexture

    def __repr__(self):
        return str(self._count) + ", " + self.item.itemTexture


class Inventory(ABC):
    inventory = {
        0: None,
        1: None,
        2: None,
        3: None
    }
    selected_slot = 0
    screen_pos = (300, 540)

    @staticmethod
    def get_selected_slot_screen_pos():
        return Inventory.screen_pos[0] + Inventory.selected_slot * 50, Inventory.screen_pos[1]

    @staticmethod
    def get_slot_screen_pos(slot):
        return Inventory.screen_pos[0] + slot * 50, Inventory.screen_pos[1]

    @staticmethod
    def get_selected_item():
        return Inventory.inventory[Inventory.selected_slot].item

    @staticmethod
    def get_selected_ItemStack():
        return Inventory.inventory[Inventory.selected_slot]


# ===================================
# _______________SETUP_______________

# pickle.dump(Game.gameObjects, open('map.pickle', 'wb'))
Game.grid = (pickle.load(open('map.pickle', 'rb')))

Inventory.inventory = {0: ItemStack(Seed, 1),
                       1: ItemStack(Trash, 1),
                       2: ItemStack(ConveyorBelt, 1),
                       3: ItemStack(Storage, 1)}

while True:
    Game.renderList.clear()
    Game.screenObjects.clear()

    # Exit game
    if Game.pressedKey[pygame.K_F1]:
        pickle.dump(Game.grid, open('map.pickle', 'wb'))
        pygame.quit()
        sys.exit()

    # Rebuild gridBlocks
    if Game.pressedKey[pygame.K_F12]:
        Game.grid = []
        for y in range(0, Game.GRID_SIZE[1]):
            for x in range(0, Game.GRID_SIZE[0]):
                GridBlock((x, y))

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
    for gridBlock in Game.grid:
        objRect = Game.rect_with_game_coordinates(gridBlock.pos)
        if screenRect.colliderect(objRect):
            Game.screenObjects.append(gridBlock)
            for layer in gridBlock.layers:
                if gridBlock.layers[layer] is not None:
                    Game.render_with_game_coordinates(gridBlock.layers[layer].texture, gridBlock.pos)

    # GridBlock related stuff
    ConveyorBelt.age += 1
    if ConveyorBelt.age == 3:
        ConveyorBelt.age = -1

    for gridBlock in Game.grid:
        gridBlock.frame_tick()
        # Mouse collide script
        collideRect = Game.rect_with_game_coordinates(gridBlock.pos)
        if collideRect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
            if pygame.mouse.get_pressed()[0] == 1:
                # v======v mouse pressed and located v======v
                gridBlock.run_mouse_click_script()

            # v======v mouse located v======v
            # Tile hover effect rendering
            Game.render_with_game_coordinates('HoverEffect.png', gridBlock.pos)

    # Timed events
    counter += 1
    if counter > 31:
        counter = 0
    if counter in (10, 20, 30):
        for gridBlock in Game.grid:
            gridBlock.tick()
    if counter in (5, 10, 15, 20, 25, 30):
        # todo Fix single tap case
        if Game.pressedKey[pygame.K_r]:
            Game.item_rotation += 1
            if Game.item_rotation > 3:
                Game.item_rotation = 0

    # Tile select effect rendering
    Game.selectedTile = None if Game.pressedKey[pygame.K_ESCAPE] or Inventory.get_selected_item() != Select else Game.selectedTile
    try: Game.render_with_game_coordinates('SelectEffect.png', Game.selectedTile)
    except TypeError: pass

    # Inventory
    Game.image_to_screen('Inventory.png', Inventory.screen_pos)
    Game.image_to_screen('InventorySelect.png', Inventory.get_selected_slot_screen_pos())
    Inventory.selected_slot = 0 if Game.pressedKey[pygame.K_1] else Inventory.selected_slot
    Inventory.selected_slot = 1 if Game.pressedKey[pygame.K_2] else Inventory.selected_slot
    Inventory.selected_slot = 2 if Game.pressedKey[pygame.K_3] else Inventory.selected_slot
    Inventory.selected_slot = 3 if Game.pressedKey[pygame.K_4] else Inventory.selected_slot
    for key in Inventory.inventory:
        if Inventory.inventory[key] is not None:
            Game.image_to_screen(Inventory.inventory[key].item.itemTexture, Inventory.get_slot_screen_pos(key))

    # debug fps
    print("fps: " + str(round(clock.get_fps())) + " | objects: " + str(len(Game.renderList)))

    """ 
    # debug gridBlock rendering
    print(Game.grid[17].layers[MainLayerTile])
    """

    # The actual blitting part
    screen.fill(pygame.Color("Black"))
    screen.blits(Game.renderList)

    # Screen refresh
    pygame.display.flip()
    clock.tick(30)
