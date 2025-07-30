class Tile:
    idCounter = 0

    def __init__(self, image):
        self.image = image
        self.id = Tile.idCounter
        Tile.idCounter += 1