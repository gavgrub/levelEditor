import pygame, json, sys, math
from types import SimpleNamespace

from engine.map import Map

width = 800
height = 600
fps = 60

camx = 0
camy = 0
rotation = 0
zoom = 1

xPressed2 = -1
rotationPressed2 = 0

# Load settings from the settings json file
def loadSettings(fileName="settings.json"):
    global colors

    with open(fileName) as f:
        file = json.load(f)
        colors = SimpleNamespace()

        colors.greyPrimary = eval(file["greyPrimary"])
        colors.greySecondary = eval(file["greySecondary"])
        colors.greyTertiary = eval(file["greyPrimary"])
        colors.accentPrimary = eval(file["accentPrimary"])
        colors.accentSecondary = eval(file["accentSecondary"])

        Map.borderColor = colors.accentPrimary
        Map.gridColor = colors.greySecondary

# User Input
def input():
    global screen, camx, camy, zoom, rotation
    global xPressed2, rotationPressed2

    keystate = pygame.key.get_pressed()
    xMouse, yMouse = pygame.mouse.get_pos()
    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()

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

    # Resetting the rotation
    if keystate[pygame.K_v]:
        rotation = 0

    # Rotating the camera
    if pressed2 and (xPressed2 == -1):
        xPressed2 = xMouse
        rotationPressed2 = rotation
    elif pressed2:
        dx = xMouse - xPressed2
        rotation = rotationPressed2 + dx * 0.005
    else:
        xPressed2 = -1

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

# Create Window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Level Editor")
clock = pygame.time.Clock()

map = Map()

loadSettings()

# Game Loop
while True:
    clock.tick(fps)
    input()
    screen.fill(colors.greyPrimary)
    map.draw(screen, camx, camy, zoom, rotation)
    pygame.display.flip()

