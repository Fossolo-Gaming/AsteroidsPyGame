
# +-------------------------+
# |       FGLib             |
# +-------------------------+
# |       pygame            |
# +-------------------------+
# |       Python            |
# +-------------------------+

import pygame, sys, os
import time, random, math
from pygame.locals import *
from pygame.time import Clock

class Image():
    def __init__(self, filename):
        self.image = pygame.image.load(filename)
        self.image.set_colorkey([0xFF, 0xFF, 0xFF], SRCCOLORKEY|RLEACCEL)
        self.image = self.image.convert_alpha()    

class Window():   
    def __init__(self, width, height, backgroundFilename):
        pygame.init()
        self.setScreen( width, height, backgroundFilename)
        self.sprites = pygame.sprite.RenderUpdates()
        self.grids = []

    def setScreen(self, width, height, backgroundFilename):
        flags = 0
        self.screen_dims = [width, height]
        self.screen = pygame.display.set_mode(self.screen_dims, flags)        
        image = Image(backgroundFilename)
        self.background = image.image
        self.screen.blit(self.background, (0, 0))
        pygame.display.update()

    def addSprite(self, sprite):
        self.sprites.add(sprite)

    def addGrid(self, grid):
        self.grids.append(grid)

    def createSprite(self, image, x, y):
        sprite = Sprite(image)
        sprite.setPosition(x, y)
        self.addSprite(sprite)
        return sprite

    def draw(self):
        self.sprites.clear(self.screen, self.background)        
        
        for grid in self.grids:
            grid.clear(self.screen, self.background)

        gridRects = []
        for grid in self.grids:
            gridRects.append(grid.draw(self.screen))
                       
        rects = self.sprites.draw(self.screen)
        if len(gridRects)>0:
            rects.extend(gridRects)
        pygame.display.update(rects)
        
    def quit(self):
        pygame.quit()

class Keyboard():
    def __init__(self):
        self.keys = None

    def readKeys(self):
        pygame.event.get()

    def isKeyPressed(self, code):
        return pygame.key.get_pressed()[code]

    def left(self):
        return self.isKeyPressed(pygame.K_LEFT)

    def right(self):
        return self.isKeyPressed(pygame.K_RIGHT)

    def up(self):
        return self.isKeyPressed(pygame.K_UP)
    
    def down(self):
        return self.isKeyPressed(pygame.K_DOWN)

    def space(self):
        return self.isKeyPressed(pygame.K_SPACE)

    def esc(self):
        return self.isKeyPressed(pygame.K_ESCAPE)    

class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, image):
        pygame.sprite.DirtySprite.__init__(self)
        self.pos = [0,0]
        self.image = None
        self.image0 = None
        self.rotAngle = 0.
        self.image0Angle = 0.        
        self.setImage(image)
        self.dirty = 2 # TO DO: need to verify a better use of dirty flag

    def setImage(self, image):
        self.image = image.image
        self.image0 = image.image
        self.rect = self.image.get_rect()
        self.dirty = 2

    def setAngle(self, angle):
        self.rotAngle = angle
        self.image = pygame.transform.rotate(self.image0, self.rotAngle + self.image0Angle)         
        rect = self.rect
        self.rect = self.image.get_rect()
        self.rect.center = rect.center

    def setPosition(self, x, y):
        self.rect[0] = x
        self.rect[1] = y

    def moveLeft(self, distance):
        self.rect[0] -= distance

    def moveRight(self, distance):
        self.rect[0] += distance

    def moveUp(self, distance):
        self.rect[1] -= distance

    def moveDown(self, distance):
        self.rect[1] += distance

    def rotateLeft(self, angle):
        newAngle = self.rotAngle + angle;
        self.setAngle(newAngle)

    def rotateRight(self, angle):
        newAngle = self.rotAngle - angle;
        self.setAngle(newAngle)

class Tileset:
    def __init__(self, tileNames):
        self.tiles = {}
        for tileData in tileNames:
            print("Loading tile:", tileData[1])
            image = Image(tileData[1])
            self.tiles[tileData[0]] = image.image

class Grid():
    def __init__(self):        
        self.tiles = []
        self.image = None

        self.drawLines = False
        self.drawGridBoundary = True
        self.drawCollision = False
        self.drawViewPort = True
        
        self.lineColor = Color(255, 0, 0)
        self.collisionRect = None
        self.highlighted = None
        

    def setTileset(self, tileset):
        self.tileset = tileset

    def setGrid(self, tiles, dx, dy, screenRect):
        self.tiles = tiles
        
        self.dx = dx
        self.dy = dy        
        self.numRows = len(self.tiles)
        self.numCols = 0        
        for row in self.tiles:
            self.numCols = max(self.numCols, len(row))
        self.rect = pygame.Rect(0, 0, self.dx * self.numCols, self.dy * self.numRows)
        self.screenRect = screenRect
        self.totalRect = pygame.Rect(0, 0, self.numCols * self.dx, self.numRows * self.dy)
        
    def setPosition(self, x, y):
        self.totalRect.topleft = (x, y)

    def getPosition(self):
        return self.totalRect.topleft;

    def setHighlightedCell(self, cell):
        self.highlighted = cell

    def removeHighlightedCell(self):
        self.highlighted = None

    def getTileValue(self, cell):
        if self.isValidCell(cell):
            return self.tiles[cell[1]][cell[0]]
        else:
            return None

    def setTileValue(self, cell, val):
        if self.isValidCell(cell):
            text = self.tiles[cell[1]]
            self.tiles[cell[1]] = text[:cell[0]] + val + text[cell[0]+1:]

    def move(self, xy):
        self.totalRect = self.totalRect.move(xy)

    def clear(self, screen, background):        
        rect = self.rect.copy()
        screen.blit(background, self.rect, self.rect)
        if self.highlighted != None:
            rect = self.getCellRect(self.highlighted)
            rect.inflate_ip(3, 3,)
            screen.blit(background, rect, rect)        
                        
    def draw(self, screen):            
        [tx, ty] = [self.totalRect[0], self.totalRect[1]]
        x0 = self.screenRect.left
        y0 = self.screenRect.top
        x1 = self.screenRect.right
        y1 = self.screenRect.bottom
        
        rectSum = self.rect.copy()
        self.rect = pygame.Rect(0,0,0,0)

        if tx < x1 and ty < y1:
            rows = [ max(0, self.yToRow(y0)), min(self.numRows, self.yToRow(y1) + 1)]
            cols = [ max(0, self.xToCol(x0)), min(self.numCols, self.xToCol(x1) + 1)]

            if rows[0] < self.numRows and rows[1] > 0 and cols[0] < self.numCols and cols[1] > 0:
                for row in range(rows[0], rows[1]):
                    cy = ty + row * self.dy
                    for col in range(cols[0], cols[1]):
                        cx = tx + col * self.dx
                        c = self.tiles[row][col]

                        # trim
                        cx0 = max(x0, cx)
                        cy0 = max(y0, cy)
                        cx1 = min(x1, cx + self.dx)
                        cy1 = min(y1, cy + self.dy)
                        w = cx1 - cx0
                        h = cy1 - cy0

                        trim = pygame.Rect(cx0-cx, cy0-cy, w, h)
                        img = self.tileset.tiles.get(c)
                        if img != None:                        
                            screen.blit(img, (cx0, cy0), trim)                            

                self.rect = self.totalRect.copy()
                self.rect = self.screenRect.clip(self.rect)

                offset = 2
                if self.drawLines:
                    for row in range(rows[0], rows[1]):
                        ry = self.rowToY(row)
                        if ry < (y0 + offset) or ry >(y1 - offset):
                            continue
                        
                        line = ((max(self.totalRect.left,  self.screenRect.left)+2,  ry),
                                (min(self.totalRect.right, self.screenRect.right)-2, ry))
                        pygame.draw.line(screen, self.lineColor, line[0], line[1], 2)

                    for col in range(cols[0], cols[1]):                        
                        rx = self.colToX(col)
                        if rx < (x0 + offset) or rx > (x1 - offset):
                            continue
                        
                        line = ((rx, max(self.totalRect.top,    self.screenRect.top)+2),
                                (rx, min(self.totalRect.bottom, self.screenRect.bottom)-2))
                        pygame.draw.line(screen, self.lineColor, line[0], line[1], 2)

                if self.drawGridBoundary:
                    rect = self.rect.copy()
                    rect.inflate_ip(-1, -1)
                    pygame.draw.rect(screen, pygame.Color(0, 0, 255), rect, 2)

                if self.drawCollision and self.collisionRect!=None:
                    pygame.draw.rect(screen, pygame.Color(255, 0, 255), self.collisionRect, 2)

                if self.highlighted!=None:
                    if self.highlighted[0] in range(cols[0], cols[1]) and self.highlighted[1] in range(rows[0], rows[1]):
                        pygame.draw.rect(screen, pygame.Color(0, 255, 0), self.getCellRect(self.highlighted), 2)

        if self.drawViewPort:
            pygame.draw.rect(screen, pygame.Color(200, 200, 200), self.screenRect, 2)

        rectSum.union(self.rect)
        return rectSum
                        

    def xToCol(self, x):
        return int((x - self.totalRect.left) / self.dx)

    def yToRow(self, y):
        return int((y - self.totalRect.top) / self.dy)

    def colToX(self, c):
        return self.totalRect.left + c * self.dx

    def rowToY(self, r):
        return self.totalRect.top + r * self.dy

    def isValidCell(self, cell):
        return cell[0]>=0 and cell[0]<self.numCols and cell[1]>=0 and cell[1]<=self.numRows;
    
    def pick(self, pos):
        cell = (self.xToCol(pos[0]), self.yToRow(pos[1]))
        if self.isValidCell(cell):
            return cell
        else:
            return None

    def getCellRect(self, cell):
        return pygame.Rect(self.colToX(cell[0]), self.rowToY(cell[1]), self.dx, self.dy)

    def getCollidedInterval(self, rect):
        cols = [ max(0, self.xToCol(rect.left)), min(self.numCols-1, self.xToCol(rect.right))+1]        
        rows = [ max(0, self.yToRow(rect.top)),  min(self.numRows-1, self.yToRow(rect.bottom))+1]
        if cols[0] < self.numCols and cols[1] > 0 and rows[0] < self.numRows and rows[1] > 0:
            return [ cols, rows ]
        else:
            return None

    def isCollided(self, rect, tileFilter):
        collided = self.getCollidedInterval(rect)
        self.collData = collided
        if collided == None:
            return False
        
        x0 = self.colToX(collided[0][0])
        x1 = self.colToX(collided[0][1])
        y0 = self.rowToY(collided[1][0])
        y1 = self.rowToY(collided[1][1])
        self.collisionRect = pygame.Rect(x0, y0, x1-x0, y1-y0)
        
        for row in range(collided[1][0], collided[1][1]):
            for col in range(collided[0][0], collided[0][1]):
                t = tiles[row][col]
                if t in tileFilter:
                    return True

        return False                    
 

    
