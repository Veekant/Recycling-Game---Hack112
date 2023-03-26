from cmu_graphics import *
import random
from PIL import Image
import os, pathlib

class trash:
    def __init__(self, type, x, y, width, height):
        self.type = type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # app.selected = False
    
    def __eq__(self, other):
        if not isinstance(other, trash): return False
        return (self.type == other.type and self.x == other.x
                 and self.y == other.y)
    
    def __repr__(self):
        return f"trash of type {self.type} at ({self.x},{self.y})"
    
    def inBounds(self, mouseX, mouseY):
        return ((self.x <= mouseX <= self.x+self.width) and
                (self.y <= mouseY <= self.y+self.height))

class trashBin:
    def __init__(self, x, y, width, height, type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = None
        self.type = type
        self.count = 0

    def __eq__(self, other):
        if not isinstance(other, trashBin): return False
        return (self.type == other.type and self.x == other.x
                 and self.y == other.y and self.width == other.width
                   and self.height == other.height)
    
    def __repr__(self):
        return (f"trash bin of type {self.type} at ({self.x},{self.y}) " +
                 f"with width {self.width} and height {self.height}")
    
    def inBounds(self, mouseX, mouseY):
        return ((self.x <= mouseX <= self.x+self.width) and
                (self.y <= mouseY <= self.y+self.height))
    
    def throwTrash(self, other):
        if isinstance(other, trash):
            if self.type == other.type:
                self.count += 1
                return True
        else: return False

def onAppStart(app):
    app.width, app.height = 1600, 800
    app.binSize = 100
    app.trashSize = 50
    app.trashTypes = ['Plastic', 'Organic', 'Paper', 'Glass', 'Metal']
    app.binY = 50
    importImages(app)
    importSound(app)
    reset(app)

def reset(app):
    app.trash = []
    app.selectedTrash = None
    app.spawnTimer = 0
    app.stepsPerSecond = 10
    app.score = 0
    app.lives = 5
    app.gameOver = False
    app.bgSound.play(loop=True)
    createTrashBins(app) 

def createTrashBins(app):
    app.bins = []
    for i in range(len(app.trashTypes)):
        binCenter = (i+1) * app.width // (len(app.trashTypes)+1)
        binX = binCenter - (app.binSize // 2)
        binType = app.trashTypes[i]
        newBin = trashBin(binX, app.binY, app.binSize, int(1.5*app.binSize), binType)
        app.bins.append(newBin)

def importImages(app):
    app.binImages = []
    binAddresses = ["red trash can.png", "green trash can.png", 
                    "blue trash can.png", "yellow trash can.png",
                    "gray trash can.png"]
    for address in binAddresses:
        img = Image.open(os.path.join(pathlib.Path(__file__).parent, address))
        imgScaled = img.reduce(img.width//app.binSize)
        image = CMUImage(imgScaled)
        app.binImages.append(image)
    
    app.trashImages = dict()
    app.trashDimensions = dict()
    trashAddresses = ["plastic_bottle.png", "banana_peel.png", "newspaper.png",
                      "glass_jar.png", "aluminum_can.png"]
    for i in range(len(trashAddresses)):
        address = trashAddresses[i]
        img = Image.open(os.path.join(pathlib.Path(__file__).parent, address))
        imgScaled = img.reduce(img.height//app.trashSize)
        image = CMUImage(imgScaled)
        trashType = app.trashTypes[i]
        app.trashImages[trashType] = image
        app.trashDimensions[trashType] = (imgScaled.width, imgScaled.height)

    beltAddress = "conveyor_belt.png"
    beltImg = Image.open(os.path.join(pathlib.Path(__file__).parent, beltAddress))
    app.beltHeight = beltImg.height*(app.width//beltImg.width)
    beltScaled = beltImg.resize((app.width+50, app.beltHeight))
    app.beltImage = CMUImage(beltScaled)
    
    bgAddress = "factory_background.jpg"
    bgImg = Image.open(os.path.join(pathlib.Path(__file__).parent, bgAddress))
    bgScaled = bgImg.resize((app.width, app.height))
    app.bgImage = CMUImage(bgScaled)

def redrawAll(app):
        drawBackground(app)
        drawBins(app)
        drawTrash(app)
        if not app.gameOver:
            drawScore(app)
        else:
            drawLabel("Game Over", app.width//2, app.height//2, size=50)
            drawLabel("Press r to restart", app.width//2, (app.height//2)+55, size=30)

def importSound(app):
    app.gameOverSound = Sound("http://freesoundeffect.net/sites/default/files/video-game-%28game-over-3%29-sound-effect-57269288.mp3")
    app.bgSound = Sound("https://incompetech.com/music/royalty-free/mp3-royaltyfree/Ethereal%20Relaxation.mp3")
    app.wrongSound = Sound("http://freesoundeffect.net/sites/default/files/earcon-error-failure-musical--%28ver-12%29-sound-effect-22244263.mp3")

def drawBackground(app):
    drawImage(app.bgImage, 0, 0)
    drawImage(app.beltImage, -25, app.height-app.beltHeight)

def drawScore(app):
    scoreText = f"Score: {app.score}"
    livesText = f"Lives: {app.lives}"
    drawLabel(scoreText, app.width//2, app.height//2, size=30)
    drawLabel(livesText, app.width//2, (app.height//2)+35, size=30)

def drawBins(app):
    for i in range(len(app.bins)):
        bin = app.bins[i]
        img = app.binImages[i]
        drawImage(img, bin.x, bin.y)
        drawLabel(bin.type, bin.x+(bin.width//2)+5, bin.y+bin.height//2)
        drawLabel(bin.count, bin.x+(bin.width//2)+5, bin.y+(bin.height//(1.05)))

def drawTrash(app):
    for i in range(len(app.trash)):
        piece = app.trash[i]
        img = app.trashImages[piece.type]
        drawImage(img, piece.x, piece.y)

def onStep(app):
    if not app.gameOver:
        doStep(app)
    if app.lives == 0:
        app.gameOver = True
        app.bgSound.pause()
        app.gameOverSound.play()

def doStep(app):
    app.spawnTimer += 1
    if app.spawnTimer >= 40:
        spawnTrash(app)
        app.spawnTimer = 0
    updateTrash(app)

def updateTrash(app):
    i = 0
    while i < len(app.trash):
        trashPiece = app.trash[i]
        if trashPiece == app.selectedTrash:
            i += 1
        elif trashPiece.x <= -trashPiece.width:
            app.trash.pop(i)
            app.lives -= 1
        else:
            trashPiece.x -= 5
            i += 1    
    
def spawnTrash(app):
    trashType = random.choice(app.trashTypes)
    trashX = random.randrange(app.width, app.width+25)
    width, height = app.trashDimensions[trashType]
    trashPiece = trash(trashType, trashX, app.height-app.beltHeight-height, width, height)
    app.trash.append(trashPiece)

def onMousePress(app, mouseX, mouseY):
    if not app.gameOver:
        for bin in app.bins:
            if bin.inBounds(mouseX, mouseY) and app.selectedTrash != None: 
                if bin.throwTrash(app.selectedTrash):
                    app.score += 1
                    app.trash.remove(app.selectedTrash)
                    app.selectedTrash = None
                else:
                    app.wrongSound.play()
                    app.lives -= 1
                return

        for trashPiece in app.trash:
            if trashPiece.inBounds(mouseX, mouseY) and app.selectedTrash == None:
                app.selectedTrash = trashPiece
                return
    
        if app.selectedTrash != None and mouseY >= app.height/2:
            app.selectedTrash.y = app.height-app.beltHeight-app.trashDimensions[app.selectedTrash.type][1]
            app.selectedTrash = None
            return

def onMouseMove(app, mouseX, mouseY):
    if app.selectedTrash != None and not app.gameOver:
        app.selectedTrash.x = mouseX - app.selectedTrash.width//2
        app.selectedTrash.y = mouseY - app.selectedTrash.height//2

def onKeyPress(app, key):
    if key == 'r' and app.gameOver: reset(app)

def main():
    runApp()

main()