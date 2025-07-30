import pygame, json, sys, math, enum
from types import SimpleNamespace

from engine.map import Map
from util.helper import *

width = 800
height = 600
fps = 60

camx = 0
camy = 0
rotation = 0
zoom = 1

# Load settings from the settings json file
def loadSettings(fileName="settings.json"):
    global colors

    with open(fileName) as f:
        file = json.load(f)
        colors = SimpleNamespace()

        colors.greyPrimary = eval(file["greyPrimary"])
        colors.greySecondary = eval(file["greySecondary"])
        colors.greyTertiary = eval(file["greyTertiary"])
        colors.accentPrimary = eval(file["accentPrimary"])
        colors.accentSecondary = eval(file["accentSecondary"])

        Map.borderColor = colors.accentPrimary
        Map.gridColor = colors.greySecondary

# Different types of menus
class Menu(enum.Enum):
    NONE = enum.auto()
    COLOR = enum.auto()

# User Input
class Controller:
    xPressed2 = -1
    rotationPressed2 = 0

    menu = Menu.NONE

    @staticmethod
    def input():
        global screen, camx, camy, zoom, rotation

        # Inputs on the map
        map.input(screen, camx, camy, zoom, rotation)

        # Inputs to the camera
        if (Controller.menu == Menu.NONE):
            Controller.camera()

        # Process input (events)
        for event in pygame.event.get():
            # Closing the window
            if event.type == pygame.QUIT:
                sys.exit()

            # Zooming in / out the camera
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    zoom *= 1.2
                if event.button == 5:
                    zoom /= 1.2
            
            # Resizing the window
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if event.type == pygame.KEYDOWN:

                # Opening the color menu
                if event.key == pygame.K_c:
                    if (Controller.menu != Menu.COLOR):
                        Controller.menu = Menu.COLOR
                    else:
                        Controller.menu = Menu.NONE
                
                # Resetting the rotation
                if event.key == pygame.K_v:
                    rotation = 0

    @staticmethod
    def camera():
        global screen, camx, camy, zoom, rotation

        keystate = pygame.key.get_pressed()
        xMouse, yMouse = pygame.mouse.get_pos()
        pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()

        # Rotating the camera
        if pressed2 and (Controller.xPressed2 == -1):
            Controller.xPressed2 = xMouse
            Controller.rotationPressed2 = rotation
        elif pressed2:
            dx = xMouse - Controller.xPressed2
            rotation = Controller.rotationPressed2 + dx * 0.005
        else:
            Controller.xPressed2 = -1

        # Moving the camera
        speed = 5 / fps / zoom
        if keystate[pygame.K_LSHIFT] or keystate[pygame.K_RSHIFT]:
            speed *= 3

        dx = 0
        dy = 0
        if keystate[pygame.K_w]:
            dy -= 1
        if keystate[pygame.K_s]:
            dy += 1
        if keystate[pygame.K_a]:
            dx -= 1
        if keystate[pygame.K_d]:
            dx += 1

        # Normalize and apply rotation
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length
            sinr = math.sin(rotation)
            cosr = math.cos(rotation)

            # Rotate movement vector to match camera orientation
            xMove = (dx * cosr - dy * sinr)
            yMove = (dx * sinr + dy * cosr)

            camx += xMove * speed
            camy += yMove * speed

class Renderer:
    uiSize = 16

    screenCache = None
    darkScreenCache = None

    rainbow = getColorMap()

    # Main rendering method
    @staticmethod
    def draw():
        if (Controller.menu == Menu.NONE):
            Renderer.screenCache = None
            Renderer.darkScreenCache = None

            screen.fill(colors.greyPrimary)
            map.draw(screen, camx, camy, zoom, rotation)

        else:
            if (Renderer.darkScreenCache == None):
                Renderer.cacheScreen()
            screen.blit(Renderer.darkScreenCache, (0, 0))

            # Color wheel menu
            if (Controller.menu == Menu.COLOR):
                screen.blit(Renderer.rainbow, (screen.get_width() / 2 - Renderer.rainbow.get_width() / 2, screen.get_height() / 2 - Renderer.rainbow.get_height() / 2))

        pygame.display.flip()

    # Method for caching the current state of the screen
    @staticmethod
    def cacheScreen():
        Renderer.screenCache = screen.copy()
        Renderer.darkScreenCache = screen.copy()

        overlay = pygame.Surface(Renderer.darkScreenCache.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))

        Renderer.darkScreenCache.blit(overlay, (0, 0))

# Create Window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Level Editor")
clock = pygame.time.Clock()

map = Map(10, 10)

loadSettings()

# Game Loop
while True:
    clock.tick(fps)
    Controller.input()
    Renderer.draw()