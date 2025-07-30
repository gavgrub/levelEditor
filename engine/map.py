import pygame, math

# Object which stores the game's map
class Map:
    cellSize = 100 # Number of pixels per square at normal zoom
    borderSize = 4
    gridSize = 2

    borderColor = None
    gridColor = None

    def __init__(self):
        self.width = 5
        self.height = 5

    # Draws the map to the screen
    def draw(self, screen, camx, camy, zoom, rotation):
        halfWidth = self.width / 2 * Map.cellSize
        halfHeight = self.height / 2 * Map.cellSize

        cosr = math.cos(-rotation)
        sinr = math.sin(-rotation)
        width, height = screen.get_width(), screen.get_height()

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
                    if not (end[0] < 0 or start[0] > width or end[1] < 0 or start[1] > height):
                        pygame.draw.line(screen, Map.gridColor, start, end, Map.gridSize)

                if row < self.height - 1:
                    # Draw bottom edge (corner 2 to 3)
                    start = screen_corners[2]
                    end = screen_corners[3]
                    if not (end[0] < 0 or start[0] > width or end[1] < 0 or start[1] > height):
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

            xMin = min(start[0], end[0])
            xMax = max(start[0], end[0])
            yMin = min(start[1], end[1])
            yMax = max(start[1], end[1])

            if xMax >= 0 and xMin <= width and yMax >= 0 and yMin <= height:
                pygame.draw.line(screen, Map.borderColor, start, end, Map.borderSize)
