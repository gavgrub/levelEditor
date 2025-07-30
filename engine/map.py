import pygame, math
from engine.tile import Tile

red = pygame.Surface((100, 100), pygame.SRCALPHA)
red.fill((255, 0, 0))

# Object which stores the game's map
class Map:
    cellSize = 100 # Number of pixels per square at normal zoom
    borderSize = 4
    gridSize = 2

    borderColor = None
    gridColor = None

    # DELETE
    selectedTile = Tile(red)

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.map = [[None for x in range(self.width)] for y in range(self.height)]

    # This function gets the dimensions of the map
    def getSize(self):
        return self.width * Map.cellSize, self.height * Map.cellSize
    
    # This function adds a cell to the grid
    def add(self, tile, x, y):
        self.map[y][x] = tile

    # This function removes a cell from the grid
    def remove(self, x, y):
        self.map[y][x] = None

    # Gets what cell is hovered over by the mouse (x, y coords)
    def getHovered(self, screen, camx, camy, zoom, rotation):
        xMouse, yMouse = pygame.mouse.get_pos()

        # Center of the screen
        width, height = screen.get_size()
        dx = (xMouse - width / 2) / zoom
        dy = (yMouse - height / 2) / zoom

        # Unrotate
        cosr = math.cos(rotation)
        sinr = math.sin(rotation)
        worldX = dx * cosr - dy * sinr + camx * Map.cellSize
        worldY = dx * sinr + dy * cosr + camy * Map.cellSize

        # Offset from map origin (centered at 0, 0)
        halfWidth = self.getSize()[0] / 2
        halfHeight = self.getSize()[1] / 2

        mapX = worldX + halfWidth
        mapY = worldY + halfHeight

        # Convert to cell index
        col = int(mapX // Map.cellSize)
        row = int(mapY // Map.cellSize)

        # Check bounds
        if 0 <= row < self.height and 0 <= col < self.width:
            return row, col
        else:
            return None

    # Runs updates for the map
    def input(self, screen, camx, camy, zoom, rotation):
        xMouse, yMouse = pygame.mouse.get_pos()
        pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()

        if not self.getHovered(screen, camx, camy, zoom, rotation) is None:
            x, y = self.getHovered(screen, camx, camy, zoom, rotation)

            # Add a tile
            if pressed1:
                self.add(Map.selectedTile, x, y)

            # Remove a tile
            elif pressed3:
                self.remove(x, y)

    # Draws the map to the screen
    def draw(self, screen, camx, camy, zoom, rotation):
        halfWidth = self.getSize()[0] / 2
        halfHeight = self.getSize()[1] / 2

        cosr = math.cos(-rotation)
        sinr = math.sin(-rotation)
        width, height = screen.get_width(), screen.get_height()

        # --- Draw the cells in the grid ---
        for row in range(self.height):
            for col in range(self.width):

                cell = self.map[col][row]

                if not cell is None:

                    # World position of top-left corner of the square
                    cellX = (col + 0.5) * Map.cellSize - halfWidth
                    cellY = (row + 0.5) * Map.cellSize - halfHeight

                    # Center the square in the cell
                    dx = cellX - camx * Map.cellSize
                    dy = cellY - camy * Map.cellSize

                    # Apply rotation
                    rx = dx * cosr - dy * sinr
                    ry = dx * sinr + dy * cosr

                    # Apply zoom and screen offset
                    xScreen = rx * zoom + width / 2
                    yScreen = ry * zoom + height / 2

                    # Scale the square image if zoomed
                    scaledSize = int(Map.cellSize * zoom)
                    if scaledSize <= 0:
                        continue  # Too small to render

                    scaledSquare = pygame.transform.scale(cell.image, (scaledSize, scaledSize))
                    rotatedSquare = pygame.transform.rotate(scaledSquare, math.degrees(rotation))

                    # Compute top-left of the scaled image
                    xDraw = xScreen - rotatedSquare.get_width() // 2
                    yDraw = yScreen - rotatedSquare.get_height() // 2

                    # Cull if offscreen
                    if xDraw + rotatedSquare.get_width() < 0 or xDraw > width + rotatedSquare.get_width() / 2 or yDraw + rotatedSquare.get_height() < 0 or yDraw > height + rotatedSquare.get_height() / 2:
                        continue

                    # Blit to screen
                    screen.blit(rotatedSquare, (xDraw, yDraw))

        # --- Draw borders for each cell ---
        for row in range(self.height):
            for col in range(self.width):
                # Calculate corners in world coordinates
                left = col * Map.cellSize - halfWidth
                right = (col + 1) * Map.cellSize - halfWidth
                top = row * Map.cellSize - halfHeight
                bottom = (row + 1) * Map.cellSize - halfHeight

                cell_corners = [
                    (left, top),
                    (right, top),
                    (right, bottom),
                    (left, bottom)
                ]

                # Transform corners to screen space
                screen_corners = []
                for x, y in cell_corners:
                    dx = x - camx * Map.cellSize
                    dy = y - camy * Map.cellSize
                    rx = dx * cosr - dy * sinr
                    ry = dx * sinr + dy * cosr
                    xScreen = rx * zoom + screen.get_width() / 2
                    yScreen = ry * zoom + screen.get_height() / 2
                    screen_corners.append((xScreen, yScreen))

                # Draw only the right and bottom edges for each cell,
                # except skip for last column and last row to avoid overlapping outer border
                if col < self.width - 1:
                    # Draw right edge (corner 1 to 2)
                    start = screen_corners[1]
                    end = screen_corners[2]
                    pygame.draw.line(screen, Map.gridColor, start, end, Map.gridSize)

                if row < self.height - 1:
                    # Draw bottom edge (corner 2 to 3)
                    start = screen_corners[2]
                    end = screen_corners[3]
                    pygame.draw.line(screen, Map.gridColor, start, end, Map.gridSize)

        # --- Draw map border ---
        corners = [
            (-halfWidth, -halfHeight),
            (halfWidth, -halfHeight),
            (halfWidth, halfHeight),
            (-halfWidth, halfHeight)
        ]

        rotated = []
        for x, y in corners:
            dx = x - camx * Map.cellSize
            dy = y - camy * Map.cellSize
            rx = dx * cosr - dy * sinr
            ry = dx * sinr + dy * cosr
            xScreen = rx * zoom + width / 2
            yScreen = ry * zoom + height / 2
            rotated.append((xScreen, yScreen))

        for i in range(len(rotated)):
            start = rotated[i]
            end = rotated[(i + 1) % len(rotated)]

            pygame.draw.line(screen, Map.borderColor, start, end, Map.borderSize)
