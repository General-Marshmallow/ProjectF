import sys
import pickle
import pygame
from pygame.locals import *
from functools import lru_cache
from old.content import *
from old.message import get_random_message

# move around with arrow keys
# F1 to escape
# F12 to reset gridBlocks
# ESC to close build menu
# e to open build menu

# Initialization
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((800, 600), flags=DOUBLEBUF)
pygame.display.set_caption(get_random_message() + " | F1 to exit")
clock = pygame.time.Clock()
# Some variables
renderSize = 64  # replace this concept with a more dynamic scaling thing                              please
cameraOffset = [0, 0]
screenRect = pygame.Rect((0, 0), (800, 600))
counter = 0  # TEMPORARY
CLEAR_MAP = False  # Use in case the map save breaks after changing attributes


# todo Replace counter system with custom pygame event
# todo Fix NoneType attribute errors
# todo Find the most efficient cache variant to use


class old_Game(ABC):
    GRID_SIZE = 16, 16
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
        pygame.K_r: False,
        pygame.K_e: False
    }
    GuiRenderList = []

    # todo Make a render function that takes enough arguments to satisfy all rendering needs

    # returns up-scaled pygame image
    @staticmethod
    @lru_cache(maxsize=1000)
    def tileWrapper(textureName):
        return pygame.transform.scale(pygame.image.load('Assets/' + textureName), (renderSize, renderSize))

    @staticmethod
    def render_with_game_coordinates(textureName, pos=(0, 0)):
        old_Game.renderList.append(
            (old_Game.tileWrapper(textureName), (pos[0] * renderSize + cameraOffset[0],
                                                 pos[1] * renderSize + cameraOffset[1]),))

    @staticmethod
    def rect_with_game_coordinates(pos):  # Don't cache this, will cause problems
        return pygame.Rect(
            (pos[0] * renderSize + cameraOffset[0], pos[1] * renderSize + cameraOffset[1]),
            (renderSize, renderSize))

    @staticmethod
    def image_to_screen(texture_name, pos):
        image = pygame.image.load('Assets/' + texture_name)
        old_Game.renderList.append(
            (pygame.transform.scale(image, (
                round(image.get_width() * (renderSize / 32)), round(image.get_height() * (renderSize / 32)))), pos))

    @staticmethod
    def trueSize_image_to_screen(texture_name, pos):
        image = pygame.image.load('Assets/' + texture_name)
        old_Game.renderList.append((image, pos))

    @staticmethod
    def get_gridBlock_with_LC(self_object, perspectiveX, perspectiveY):
        for index, gb in enumerate(old_Game.grid):
            if gb == self_object:
                # found self
                try:
                    return old_Game.grid[index + perspectiveY * old_Game.GRID_SIZE[0] + perspectiveX]
                except IndexError:
                    return None


class GridBlock:
    def __init__(self, pos):
        self.pos = pos

        # Deprecated
        """
        self.layers = {
            Layer.BackgroundLayer: None,
            Layer.TerrainLayer: None,
            Layer.MainLayer: None,
            Layer.DecorationLayer: None
        }
        """

        self.data = {Layer.BackgroundLayer: {},
                     Layer.TerrainLayer: {},
                     Layer.MainLayer: {},
                     Layer.DecorationLayer: {}}
        old_Game.grid.append(self)

    def new_tile(self, tileClass: Tile.__subclasses__(), force_replace=False):
        if self.get_data(tileClass.tileLayer, DataTag.tileType) is None or force_replace:  # If empty or forced replace
            for dataTag in tileClass.dataTags:
                self.data[tileClass.tileLayer][dataTag] = defaults[dataTag]
            self.data[tileClass.tileLayer][DataTag.tileType] = tileClass

    def get_tile(self, layer: Layer):  # Returns tile.py class
        try:
            return self.data[layer][DataTag.tileType]
        except KeyError:
            pass

    def clear_layer(self, layer: Layer):
        self.data[layer] = {}

    def clear(self, clearTerrain=False):
        for layer in self.data:
            if layer == Layer.TerrainLayer and not clearTerrain:
                continue
            self.data[layer][DataTag.tileType] = None

    def get_data(self, layer: Layer, data: DataTag):  # Returns DataTag value
        try:
            return self.data[layer][data]
        except KeyError:
            try:
                return defaults[data]
            except KeyError:
                raise NotImplementedError

    def set_data(self, layer: Layer, data: DataTag, value):
        if data != DataTag.tileType:  # To change tileType, use new_tile()
            self.data[layer][data] = value

    def run_mouse_click_script(self):
        bm = GUI.BuildMenu
        # todo Automate tile.py rotation
        # todo (!) Create a script list for every gridBlock - performance boost

        # tile.py placing
        if bm.get_selected_item() in Tile.__subclasses__():
            self.new_tile(bm.get_selected_item(), force_replace=False)

        # seed planting
        if bm.get_selected_item() == Seed:
            if self.get_tile(FarmLandWet.tileLayer) == FarmLandWet:
                self.new_tile(Plant)

        # plant removal
        if bm.get_selected_item() == Fertilizer:
            if self.get_tile(Plant.tileLayer) == Plant:
                self.clear_layer(Plant.tileLayer)

        # tile.py removal
        if bm.get_selected_item() == Trash:
            self.clear(clearTerrain=False)

        # Possibly broken
        """
        # Selecting tile.py
        if bm.get_selected_item() == Select:
            Game.selectedTile = self.pos
        """

        """
        # Conveyor belt placing
        if bm.get_selected_item() == ConveyorBelt:
            if self.layers[MainLayerTile] is None:
                self.new_tile(ConveyorBelt(bm.get_selected_rotation()))
    
        # Storage placing
        if bm.get_selected_item() == Storage:
            if self.layers[MainLayerTile] is None:
                self.new_tile(Storage(bm.get_selected_rotation()))
        """
        """
        # TEMPORARY Seed->Storage
        if Inventory.get_selected_item() == Seed and self.get_tile(Storage.tileLayer):
            self.set_data(Storage.tileLayer, DataTag.contents, [ItemStack(Seed, 10)])
        """

    def frame_tick(self):  # Run every frame (for texture updates)

        # Plant growth
        if self.get_tile(Plant.tileLayer) == Plant:
            current_age = self.get_data(Plant.tileLayer, DataTag.age)
            self.set_data(Plant.tileLayer, DataTag.age, current_age + 1) if current_age < 350 else None
            self.set_data(Plant.tileLayer, DataTag.textureIndex, 1) if current_age > 100 else None
            self.set_data(Plant.tileLayer, DataTag.textureIndex, 2) if current_age > 200 else None
            self.set_data(Plant.tileLayer, DataTag.textureIndex, 3) if current_age > 300 else None

        # Conveyor belt texture update
        if self.get_tile(ConveyorBelt.tileLayer) == ConveyorBelt:
            self.set_data(ConveyorBelt.tileLayer, DataTag.textureIndex, self.get_data(ConveyorBelt.tileLayer,
                                                                                      DataTag.textureIndex))
            # todo +1 to index change after fixing texture list

        # Conveyor belt item rendering
        if self.get_tile(ConveyorBelt.tileLayer) == ConveyorBelt:
            contents = self.get_data(ConveyorBelt.tileLayer, DataTag.contents)
            if contents is not None:
                old_Game.render_with_game_coordinates(contents[0].item.itemTexture, self.pos)

    # todo Fix tick() horror
    # Nty... *adds pass*
    def tick(self):  # Run less often
        pass
        """
        # Items ConveyorBelt->ConveyorBelt
        if self.get_tile(ConveyorBelt.tileLayer) == ConveyorBelt:
            this_conveyor: ConveyorBelt = self.get_tile(ConveyorBelt)
            if this_conveyor.input_this_frame:
                this_conveyor.input_this_frame = False
            else:
                if this_conveyor.contents is not None:
                    if Game.get_gridBlock_with_LC(self, dirDict[this_conveyor.direction][0],
                                                  dirDict[this_conveyor.direction][1]).has_tile(ConveyorBelt):
                        if not Game.get_gridBlock_with_LC(self, dirDict[this_conveyor.direction][0],
                                                          dirDict[this_conveyor.direction][1]).get_tile(
                            ConveyorBelt).direction == oppositeDirDict[this_conveyor.direction]:
                            other_conveyor: ConveyorBelt = Game.get_gridBlock_with_LC(self,
                                                                                      dirDict[this_conveyor.direction]
                                                                                      [0],
                                                                                      dirDict[this_conveyor.direction][
                                                                                          1]).get_tile(ConveyorBelt)
                            try:
                                if other_conveyor.contents is None:
                                    # == item transfer == #
                                    other_conveyor.input_this_frame = True
                                    other_conveyor.contents = this_conveyor.contents
                                    this_conveyor.contents = None
                            except AttributeError:
                                pass
        
        # Items Storage->ConveyorBelt
        if self.get_tile(Storage.tileLayer) == Storage:
            storage: Storage = self.get_tile(Storage)
            if storage.contents:  # if contents is not empty
                output_gridBlock: GridBlock = Game.get_gridBlock_with_LC(self, dirDict[storage.direction][0],
                                                                         dirDict[storage.direction][1])
                if output_gridBlock.has_tile(ConveyorBelt):  # if has a conveyorBelt
                    conveyorBelt: ConveyorBelt = output_gridBlock.get_tile(ConveyorBelt)
                    if conveyorBelt.contents is None and not storage.direction == oppositeDirDict[
                        conveyorBelt.direction]:  # if conveyorBelt is empty and is not facing storage
                        # == item transfer == #
                        # Set conveyorBelt contents to the first Item in Storage contents
                        conveyorBelt.contents = ItemStack(storage.contents[0].item, 1)
                        # Subtract 1 from Storage contents
                        storage.contents[0] = storage.contents[0].return_itemStack_add(-1)
                        conveyorBelt.input_this_frame = True
                        if storage.contents[0] is None:
                            storage.contents.pop(0)
        """


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
        return Inventory.screen_pos[0] + Inventory.selected_slot * 64, Inventory.screen_pos[1]

    @staticmethod
    def get_slot_screen_pos(slot):
        return Inventory.screen_pos[0] + slot * 64, Inventory.screen_pos[1]

    @staticmethod
    def get_selected_item():
        return Inventory.inventory[Inventory.selected_slot].item

    @staticmethod
    def get_selected_ItemStack():
        return Inventory.inventory[Inventory.selected_slot]


class GuiElement(ABC):  # A box shaped rectangle

    def __init__(self, pos: tuple, size: tuple):
        self.pos = pos
        self.size = self.width, self.height = size

    @lru_cache(maxsize=100)
    def get_rect(self):
        return pygame.Rect(self.pos, (self.width, self.height))


class ImageButton(GuiElement):

    def __init__(self, pos: tuple, size: tuple, image: str):
        super().__init__(pos, size)
        self.image = image


# todo Fix the unsorted buildMenu situation
class GUI(ABC):
    mouse_collide_element = None  # The gui element currently under mouse
    build_menu_active = False
    build_menu = []

    @staticmethod
    def new_element(guiElementSetup):
        old_Game.GuiRenderList.append(guiElementSetup)

    @staticmethod
    def get_mouse_element():
        for element in old_Game.GuiRenderList:
            if element.get_rect().collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                return element
        return None

    class BuildMenu(GuiElement, ABC):
        selected_slot = None

        @staticmethod
        def get_selected_item():
            if GUI.BuildMenu.selected_slot is None:
                return None
            return GUI.build_menu[GUI.BuildMenu.selected_slot]

        """
        @staticmethod
        def get_selected_rotation():  # todo Find a solution to this approach
            try:
                return GUI.build_menu[GUI.BuildMenu.selected_slot].direction
            except AttributeError:
                return Direction.DU
        """


# ===================================
# _______________SETUP_______________
# ===================================

# pickle.dump(Game.gameObjects, open('map.pickle', 'wb'))
old_Game.grid = (pickle.load(open('map.pickle', 'rb')))

Inventory.inventory = {0: ItemStack(Seed, 1),
                       1: ItemStack(Trash, 1),
                       2: ItemStack(ConveyorBelt, 1),
                       3: ItemStack(Storage, 1)}

GUI.build_menu = [FarmLand, FarmLandWet,
                  Seed, Pavement, Terrain, OreNode,
                  ConveyorBelt,
                  Storage,
                  Select, Trash, Fertilizer]


while True:
    old_Game.renderList.clear()
    old_Game.screenObjects.clear()
    old_Game.GuiRenderList.clear()

    """
    # == Events == #
    """

    # Exit game
    if old_Game.pressedKey[pygame.K_F1]:
        pickle.dump(old_Game.grid, open('map.pickle', 'wb'))
        pygame.quit()
        sys.exit()

    # Open / close build menu
    if old_Game.pressedKey[pygame.K_e]:
        GUI.build_menu_active = True
    if old_Game.pressedKey[pygame.K_ESCAPE]:
        GUI.build_menu_active = False

    # Rebuild gridBlocks
    if old_Game.pressedKey[pygame.K_F12] or CLEAR_MAP:
        old_Game.grid = []
        for y in range(0, old_Game.GRID_SIZE[1]):
            for x in range(0, old_Game.GRID_SIZE[0]):
                GridBlock((x, y))
        for element in old_Game.grid:
            element.new_tile(Terrain, force_replace=True)

    # Pressed keys event checking
    # todo Fix sticky keys (around every 5 frames should do it)
    for event in pygame.event.get():
        try:
            if event.key in old_Game.pressedKey:
                if event.type == pygame.KEYDOWN:
                    old_Game.pressedKey[event.key] = True
                if event.type == pygame.KEYUP:
                    old_Game.pressedKey[event.key] = False
        except AttributeError:
            continue

    # Camera scrolling with arrow keys for debug purposes
    if old_Game.pressedKey[pygame.K_LEFT]:
        cameraOffset[0] += 5
    if old_Game.pressedKey[pygame.K_RIGHT]:
        cameraOffset[0] -= 5
    if old_Game.pressedKey[pygame.K_UP]:
        cameraOffset[1] += 5
    if old_Game.pressedKey[pygame.K_DOWN]:
        cameraOffset[1] -= 5

    # Rebuilding screenObjects and renderList
    for gridBlock in old_Game.grid:
        objRect = old_Game.rect_with_game_coordinates(gridBlock.pos)
        if screenRect.colliderect(objRect):
            old_Game.screenObjects.append(gridBlock)
            for layer in render_order:
                try:
                    old_Game.render_with_game_coordinates(gridBlock.get_data(layer, DataTag.tileType).tileTexture[gridBlock.get_data(layer, DataTag.textureIndex)], gridBlock.pos)
                except AttributeError:
                    pass
            """    
            for layer in gridBlock.layers:
                if gridBlock.layers[layer] is not None:
                    Game.render_with_game_coordinates(
                        gridBlock.layers[layer].texture[gridBlock.get_data(layer)[DataTag.textureIndex]], gridBlock.pos)"""

    # GridBlock related stuff
    ConveyorBelt.age += 1
    if ConveyorBelt.age == 3:
        ConveyorBelt.age = -1

    # Timed events
    counter += 1
    if counter > 31:
        counter = 0
    if counter in (10, 20, 30):
        for gridBlock in old_Game.grid:
            gridBlock.tick()
    if counter in (5, 10, 15, 20, 25, 30):
        # todo Fix single tap case (sticky keys)
        if old_Game.pressedKey[pygame.K_r]:
            old_Game.item_rotation += 1
            if old_Game.item_rotation > 3:
                old_Game.item_rotation = 0

    """
    # == Rendering == #
    """

    # tile.py select effect rendering
    old_Game.selectedTile = None if old_Game.pressedKey[
                                    pygame.K_ESCAPE] or Inventory.get_selected_item() != Select else old_Game.selectedTile
    try:
        old_Game.render_with_game_coordinates('SelectEffect.png', old_Game.selectedTile)
    except TypeError:
        pass

    # Build menu
    if GUI.build_menu_active:
        index = 0
        for y in range(10):
            for x in range(2):
                try:
                    old_Game.GuiRenderList.append(ImageButton((x * 32, y * 32), (32, 32), GUI.build_menu[index].texture[0]))
                    index += 1
                except AttributeError:
                    old_Game.GuiRenderList.append(
                        ImageButton((x * 32, y * 32), (32, 32), GUI.build_menu[index].itemTexture[0]))
                    index += 1
                except IndexError:
                    pass

    # Currently replaced by build menu
    """
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
    """

    for gridBlock in old_Game.grid:
        gridBlock.frame_tick()
        # Mouse collide script
        collideRect = old_Game.rect_with_game_coordinates(gridBlock.pos)
        if collideRect.collidepoint(pygame.mouse.get_pos()[0],
                                    pygame.mouse.get_pos()[1]) and GUI.get_mouse_element() is None:
            if pygame.mouse.get_pressed()[0] == 1:
                # v======v mouse pressed and located v======v
                gridBlock.run_mouse_click_script()

            # v======v mouse located v======v
            # tile.py hover effect rendering
            old_Game.render_with_game_coordinates('HoverEffect.png', gridBlock.pos)

    # GUI render
    for element in old_Game.GuiRenderList:
        old_Game.trueSize_image_to_screen(element.image, element.pos)
    if GUI.build_menu_active:
        # todo Will cause problems in the near future (GUI has other stuff than buildMenu)
        #  - make GUI mouse collision detection automatic
        for i, element in enumerate(old_Game.GuiRenderList):
            if element.get_rect().collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                old_Game.trueSize_image_to_screen('HoverEffect.png', element.pos)
                if pygame.mouse.get_pressed()[0] == 1:
                    GUI.BuildMenu.selected_slot = i
    if old_Game.pressedKey[pygame.K_ESCAPE]:
        GUI.BuildMenu.selected_slot = None

    try:
        old_Game.trueSize_image_to_screen('SelectEffect.png', old_Game.GuiRenderList[GUI.BuildMenu.selected_slot].pos)
    except TypeError:
        pass

    # debug fps
    print("fps: " + str(round(clock.get_fps())) + " | objects: " + str(len(old_Game.renderList)))

    """ 
    # debug gridBlock rendering
    print(Game.grid[17].layers[MainLayerTile])
    """

    # The actual blitting part
    screen.fill((3, 0, 12))
    screen.blits(old_Game.renderList)

    # Screen refresh
    pygame.display.flip()
    clock.tick(60)
