import sys, random
from pygame import *
from tile import *
from entity import *
from world import *
from player import *
from util import *
from material import Material, Resource
from perlin_noise import PerlinNoise

init()
screen = display.set_mode((800, 600), flags=DOUBLEBUF)
clock = time.Clock()
screensize = screensizex , screensizey = display.get_window_size()

hook = []
def getWorld() -> World:
    return hook[0]
def getPlayer() -> Player:
    return hook[1]

# 1. Ära loo endale probleeme, mida sul pole
# 2. Lihtsam lahendus on parem, ära süsteemita mingit nusserdust kokku
# 3. Ära ole autist


def gameloop():

    world = World()
    player = Player()
    tools = Util()

    tilesize = 200
    cameraOffset = [0, 0]
    mouseCooldownLen = 5  # In frames
    mouseLeftCooldown = 0
    mouseRightCooldown = 0
    scrollDirection = 0

    keyUp: bool = False
    keyDown: bool = False
    keyLeft: bool = False
    keyRight: bool = False

    ENTITYTICK = USEREVENT + 1
    time.set_timer(ENTITYTICK, 100)
    eTickThisFrame = False

    # Map setup
    """
    seed = random.randrange(100, 500, 1)
    noise = PerlinNoise(octaves=7, seed=seed)
    noiseHi = PerlinNoise(octaves=1, seed=seed)
    for y in range(1, 20):
        for x in range(1,20):
            if noise([100/(x+50),100/(y+50)]) > 0.13:
                world.placeTile(OreNode((x, y)))
            elif noise([100/(x+50),100/(y+50)]) > 0.1:
                world.placeTile(Stones((x,y)))
    """
    while True:
        # Update global world object refrence for entities
        Entity.world = world


# EVENTS

        # keyboard and scroll input
        for e in event.get():
            if e.type == KEYDOWN or e.type == KEYUP:
                if e.key == K_ESCAPE or e.type == QUIT: sys.exit()
                if e.key == K_w: keyUp = not keyUp
                if e.key == K_s: keyDown = not keyDown
                if e.key == K_a: keyLeft = not keyLeft
                if e.key == K_d: keyRight = not keyRight
                if e.key == K_r: world.placeTile(Storage(player.getMouseMapPos(cameraOffset)))
            elif e.type == MOUSEWHEEL:
                scrollDirection = int(e.y / abs(e.y))
            elif e.type == ENTITYTICK:
                eTickThisFrame = True

        # move camera
        if keyUp: cameraOffset[1] += 5
        if keyDown: cameraOffset[1] -= 5
        if keyLeft: cameraOffset[0] += 5
        if keyRight: cameraOffset[0] -= 5

        # mouse related checks
        mousebuttons = mouse.get_pressed()


# TILE TICK

        # Draw buffer resets
        renderlist = []


        # Terrain background generator
        for y in range(-1, (screensizey//tilesize)+1):
            for x in range(-1, (screensizex//tilesize)+1):
                renderlist.append((tools.loadTexture('terrain2.png'), (x*tilesize+cameraOffset[0]%tilesize,y*tilesize+cameraOffset[1]%tilesize)))

        # Cycle tiles
        for tile in world.tiles:
            if Rect(tile.location[0], tile.location[1], 50, 50).colliderect(screen.get_rect()):
                renderlist.append(tools.lots(tile, cameraOffset))


# ENTITY TICK

        # Update entities
        for entity in world.entities:
            renderlist.append((tools.loadTexture((entity.texture)), (entity.position[0] * tilesize + cameraOffset[0], entity.position[1] * tilesize + cameraOffset[1])))
            entity.update()
            if eTickThisFrame:
                entity.tick()


# MISC CODE AREA

        # Put black square on storage tiles when hovering over
        if player.getMaterialUnderMouse(world, cameraOffset) == Material.STORAGE:
            renderlist.append((tools.loadTexture('blackCover.png'), world.tiles[(player.getTileIndexUnderMouse(world,cameraOffset))].getOnScreenPosition(cameraOffset)))

        # Resource collection test
        if mousebuttons[0] and tools.getScrollMaterial() == Material.AIR and not player.getMaterialUnderMouse(world, cameraOffset) == Material.AIR:
            player.addResource(player.getMaterialUnderMouse(world, cameraOffset), 1)
            world.tiles[player.getTileIndexUnderMouse(world, cameraOffset)].destroy(world)

            print(player.resources)

        # Rover spawn test
        if mousebuttons[2] and mouseRightCooldown == 0 and player.getMaterialUnderMouse(world, cameraOffset) == Material.AIR:
            world.spawnEntity(Rover(player.getMouseMapPos(cameraOffset)))

        # Scroll wheel material menu
        if not scrollDirection == 0:
            tools.updateScrollMenuSelectedSlot(scrollDirection)
            print(tools.getScrollMaterial())
        if mousebuttons[0] and mouseLeftCooldown == 0:
            world.placeTileByMaterial(tools.getScrollMaterial(),player.getMouseMapPos(cameraOffset))

        # Mouse click cooldown
        if mousebuttons[0] and mouseLeftCooldown == 0: mouseLeftCooldown = mouseCooldownLen
        if mousebuttons[2] and mouseRightCooldown == 0: mouseRightCooldown = mouseCooldownLen
        if mouseLeftCooldown > 0: mouseLeftCooldown -= 1
        if mouseRightCooldown > 0: mouseRightCooldown -= 1



        """""""""""===DEBUG AREA==="""""""""""



        """"""""""""""""""""""""""""""""""""""
        # Reset area
        scrollDirection = 0
        eTickThisFrame = False

        # Render and refresh screen
        screen.fill((3, 0, 12))
        screen.blits(renderlist)
        display.flip()
        clock.tick(30)

gameloop()
