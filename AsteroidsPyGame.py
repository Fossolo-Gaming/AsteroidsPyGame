#**********************************************************
#                   AsteroidsPyGame.py
#**********************************************************
# Developed by Stefano Pippa May 5th 2020

# This is a simple Asteroids-like game implemented in Python
# using PyGame library for the Fossolo-gaming online class
# of Python

# About Fossolo-gaming:
# Email   : fossolo.gaming@gmail.com
# Web page: fossolo-gaming.it
# FB page : http://www.facebook.com/Fossolo.Gaming.Bologna

import pygame, sys, os
import time, random, math
from pygame.locals import *

#--------------------
# Utility functions
#--------------------

def randomPosition(offset = 0):
    # generates a random position [x,y] on the screen
    # offset reduces the screen area by an offset around the border
    L = GameData.screen_dims[0] - 2 * offset
    H = GameData.screen_dims[1] - 2 * offset

    x = int(random.uniform(0, L)) + offset
    y = int(random.uniform(0, H)) + offset
    return [x, y]

def angleToXY(angle):
    # given an angle in degrees, returns a unit vector in that direction
    # Note: angle 0 deg is oriented as [0, 1], not as [1, 0]    
    rad = 3.14/180. * angle
    return [math.sin(rad), math.cos(rad)]

#--------------------
# GameData class
#--------------------

class GameData:
    # Provide a generic PyGame infrastructure for storing game data
    # and initializing PyGame

    # change this if you want to modify game window size
    screen_dims = [1024, 768]
    flags = 0

    # filenames of the images used in the game.
    # some sprites uses a single image others (VariableImageSprites) use a small list of images
    # the images are sorted using a key in the dictionary to get the list of images associated to it
    imageNames = { 'Asteroid':  ["images/meteorBrown_tiny1.png",
                                 "images/meteorBrown_small1.png",
                                 "images/meteorBrown_med3.png",
                                 "images/meteorBrown_big3.png",
                                 "images/meteorBrown_big4.png"],
                   'Shield':    ["images/shield1.png",
                                 "images/shield2.png",
                                 "images/shield3.png"],
                   'Bullet':    ["images/laserRed01.png"],
                   'Player':    ["images/playerShip2_blue.png"],
                   'PowerUp':   ["images/powerupRed_bolt.png",
                                 "images/powerupYellow_bolt.png",
                                 "images/powerupGreen_star.png",
                                 "images/star_gold.png",
                                 "images/shield_silver.png",
                                 "images/star_bronze.png"] }

    # images are loaded into images list. They can be accessed using an ImageId
    images = []

    #dictionary of imageIds. It is populated using imageNames dictionary
    imageIds = {}

    # dictionary for sounds filenames used in the game
    soundNames = { 'Fire': "sound/laser.wav",
                   'Explosion' : "sound/explosion.wav",
                   'AsteroidBreak': "sound/asteroidbreak.wav",
                   'PowerUp': "sound/powerup.wav",
                   'Shield': "sound/shield.wav",
                   'Bomb': "sound/laser2.wav",
                   'PowerUp2': "sound/powerup2.wav",
                   'Start': "sound/start.wav",
                   'GameOver': "sound/gameover.wav",
                   'Victory': "sound/victory.wav"}

    # dictionary of sounds objects. It is populated using soundNames dictionary
    sounds = {}

    screen = None      # object of the game window. Initialized later
    backGround = None  # object of the background image. Initialized later
 
    def __init__(self, backgroundFilename):
        pygame.init()
    
        GameData.screen = pygame.display.set_mode(GameData.screen_dims, GameData.flags)
        
        backGroundId = self.loadImage(backgroundFilename)
        GameData.background = GameData.images[backGroundId]
        GameData.screen.blit(GameData.background, (0, 0))
        pygame.display.flip()

        self.loadAllImages()
        self.loadAllSounds()

    def loadImage(self, filename):
        sprite_surface = pygame.image.load(filename)
        sprite_surface.set_colorkey([0xFF, 0xFF, 0xFF], SRCCOLORKEY|RLEACCEL)
        sprite_surface = sprite_surface.convert_alpha()
        GameData.images.append(sprite_surface)
        return len(GameData.images)-1

    def loadImages(self, filenames):
        imageIds = []        
        for filename in filenames:
            imageIds.append(self.loadImage(filename))
        return imageIds            

    def loadAllImages(self):
        for key, value in GameData.imageNames.items():
            GameData.imageIds[key] = self.loadImages(value)
    
    def loadAllSounds(self):
        for key, filename in GameData.soundNames.items():
            GameData.sounds[key] = pygame.mixer.Sound(filename)

                   
#--------------------
# Timer class
#--------------------

class Timer:
    # This is an utility class. Defines a timer with a duration.
    # You can start the timer and check if time is up.
    # Remember to update timer status before checking its enabled status.
    # Otherwise use checkEnabled method that returns the updated enabled status
    def __init__(self, enabled, duration):
        self.enabled = enabled
        self.startTime = time.time()
        self.duration = duration

    def start(self):
        self.enabled = True
        self.startTime = time.time()

    def update(self):
        if self.enabled:
            currTime = time.time()
            elapsedTime = currTime - self.startTime
            if elapsedTime>self.duration:
                self.enabled = False
                
    def checkEnabled(self):
        self.update()
        return self.enabled   
   
#--------------------
# BasicSprite class
#--------------------

class BasicSprite(pygame.sprite.DirtySprite):
    # This is the base class of all the sprites used in the game.
    # It simply gets its image from GameData.images through an id passed as input
    def __init__(self, imageId, pos):
        pygame.sprite.DirtySprite.__init__(self)
        self.pos = pos
        self.image = GameData.images[imageId]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.dirty = 2 # TO DO: need to verify a better use of dirty flag

#--------------------
# MovingSprite class
#--------------------

class MovingSprite(BasicSprite):
    # Base class used by all the moving objects on the screens.
    # It extends BasicSprite functionalities by adding a velocity vector and a rotation angle.
    # It is able to rotate the image of the sprite.
    # When update is called the sprite is moved using velocity vector (vel)
    # If the sprites touches the screen borders it bounds (is reboundOnBorders flag is enabled)
    def __init__(self, imageId, pos):
        BasicSprite.__init__(self, imageId, pos)
        self.image0 = self.image
        self.vel = [0., 0.]
        self.rotAngle = 0.
        self.image0Angle = 0.
        self.reboundOnBorders = True       

    def rotate(self, angle):
        self.rotAngle = angle
        self.image = pygame.transform.rotate(self.image0, self.rotAngle + self.image0Angle)
        delta = [0., 0.]            
        rect = self.rect
        self.rect = self.image.get_rect()
        self.rect.center = rect.center
        self.pos[0] +=  float(self.rect[0]-rect[0])
        self.pos[1] +=  float(self.rect[1]-rect[1])

    def update(self):
        dims = [self.image.get_rect().width, self.image.get_rect().height]
        for i in [0, 1]:
            nv = float(self.pos[i] + self.vel[i])
            if self.reboundOnBorders:
                if nv >= float(GameData.screen_dims[i]-dims[i]) or nv < 0:
                    self.vel[i] = -self.vel[i]
                    nv = self.rect[i] + 2. * self.vel[i]            
            self.pos[i] = nv
            self.rect[i] = int(self.pos[i])

#---------------------------
# VariableImageSprite class
#---------------------------

class VariableImageSprite(MovingSprite):
    # This extends MovingSprite class by supporting multiple images

    def __init__(self, imageIds, index, pos):   
        MovingSprite.__init__(self, imageIds[index], pos)
        self.size = index 

    def recenter(self, newCenter):
        shift = [0.,0.]
        for i in [0,1]:
            shift[i] = newCenter[i] - self.rect.center[i]
            self.pos[i] += float(shift[i])
        self.rect.center = newCenter

#--------------------
# TextSprite class
#--------------------

class TextSprite(pygame.sprite.DirtySprite):
    # This sprite is used to write text on the screen
    def __init__(self, text, fontName, size, color, pos):
        pygame.sprite.DirtySprite.__init__(self)
        
        self.fontName = fontName
        self.size = size
        self.color = color
        self.font = pygame.font.SysFont(self.fontName, size)
        self.pos = pos
        self.updateText(text)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.dirty = 2

    def updateText(self, text):
        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos        

#--------------------
# SubGroup class
#--------------------

class SubGroup(pygame.sprite.Group):
    # Sprites are collected into groups.
    # There is a main group that is stored inside Game class
    # that stores all the sprites to be displayed.
    # However I need to collect sprites also basing on their types (asteroids, bullets, powerUps)
    # so I need to create also other groups or better subgroups of the main one.
    # This SubGroup class helps me in maintaining such subgorups.
    # its add methods not only adds the sprite to this (sub)group, but also to its parent (Game.sprites group)
    
    def __init__(self, parent):
        sprites = pygame.sprite.Group()
        self.parent = parent
        pygame.sprite.Group.__init__(self, sprites)

    def add(self, sprite):
        pygame.sprite.Group.add(self, sprite)
        self.parent.add(sprite)

#--------------------
# Asteroids class
#--------------------

class Asteroids(SubGroup):
    # SubGroups that manages the asteroids
    
    speed = 3. # asteroids default speed
    
    def __init__(self, parent):
        SubGroup.__init__(self, parent)

    def initialize(self, Sm, SM):
        size = int(random.uniform(Sm, SM))
        [x, y] = randomPosition()
        
        angle = random.uniform(-180, 180)
        return self.create(size, x, y, angle, Asteroids.speed)
    
    def create(self, size, x, y, angle, speed):
        asteroid = VariableImageSprite(GameData.imageIds['Asteroid'], size-1, [x,y])
        self.add(asteroid)
        
        asteroid.rotate(angle)
        asteroid.vel = angleToXY(angle)
        asteroid.vel[0] *= speed
        asteroid.vel[1] *= speed
        return asteroid

    def destroy(self, asteroid, bullet):                                    
        if asteroid.size>1:
            newSize = asteroid.size-1
            angle = bullet.rotAngle + 90.
            angle2 = angle + 180.
            speed = 3
            x = asteroid.pos[0]
            y = asteroid.pos[1]        
            self.create(newSize+1, x, y, angle, speed)        
            self.create(newSize+1, x, y, angle2, speed)

        asteroid.kill()
        GameData.sounds['AsteroidBreak'].play()

    def update(self):
        for asteroid in self:
            asteroid.rotate(asteroid.rotAngle + 1)

#--------------------
# Shield class
#--------------------
    
class Shield(VariableImageSprite):
    # Class for displaying the player ship shield.
    # It follows the ship position and continuously rotate (only a visual FX)
    
    def __init__(self, size, playerShip):
        pos = playerShip.pos.copy()
        VariableImageSprite.__init__(self, GameData.imageIds['Shield'], size-1, pos)        
        self.playerShip = playerShip
        self.recenter(playerShip.rect.center)

    def update(self):
        self.rect.center = self.playerShip.rect.center
        self.rotate(self.rotAngle+10.0)

#--------------------
# Bullets class
#--------------------

class Bullets(SubGroup):
    # SubGroup that manages the bullets in the game
    
    speed = 10. # default bullet speed
    
    def __init__(self, parent):
        SubGroup.__init__(self, parent)

    def create(self, pos):
        bullet = MovingSprite(GameData.imageIds['Bullet'][0], pos)
        self.add(bullet)
        return bullet

    def destroyOnBoundary(self):
        for bullet in self:
            destroy = False
            for i in [0,1]:
                coord = int(bullet.pos[i])
                if coord < 0 or coord > GameData.screen_dims[i]:
                    destroy = True
                    break
            if destroy:
                bullet.kill()

#--------------------
# Player class
#--------------------

class Player:
    # class that defines the player concept
    # It is contains:
    # - player stats (lives, score, bombs, etc.)
    # - player ship
    # - ship shield
    # It supports methods for moving and firing
    
    baseShotTime = 0.5
    speedShotTime = 0.125
    invulnerabilityDuration = 3.0    
    
    def __init__(self, game):        
        self.game = game
        self.lives = 3
        self.score = 0
        
        #shot
        self.fireTimer = Timer(False, Player.baseShotTime)
        self.tripleShot = False

        #bombs
        self.bombTimer = Timer(False, Player.baseShotTime)
        self.bombs = 3

        #invulnerability
        self.invulnerability = Timer(False, Player.invulnerabilityDuration)
        
        #ship initialization
        self.ship = None
        self.shieldLevel = 0           
        self.reset()

    def reset(self):        
        if self.ship!=None:
            self.ship.kill()
        pos = [GameData.screen_dims[0]/2, GameData.screen_dims[1]/2]
        self.angle = 0.
        self.ship = MovingSprite(GameData.imageIds['Player'][0], pos)
        self.game.sprites.add(self.ship)
        self.removePowerUpsAndRestoreShield()

    def removePowerUpsAndRestoreShield(self):
        self.tripleShot = False
        self.shotTime = Player.baseShotTime
        self.setShieldLevel(1)

    def setShieldLevel(self, level):
        if self.shieldLevel>0:
            self.shield.kill()

        self.shieldLevel = level
        if self.shieldLevel>0:
            self.shield = Shield(level, self.ship)
            self.game.sprites.add(self.shield)

    #ship controls
    def rotateShip(self, dir):
        angleDiff = 5.
        if dir<0:
            angleDiff = -angleDiff

        self.angle += angleDiff
        self.ship.rotate(int(self.angle))

    def accelerateShip(self, dir):
        acc = 0.5
        if dir>0:
            acc = -acc

        xy = angleToXY(self.angle)
        self.ship.vel[0] += acc * xy[0]
        self.ship.vel[1] += acc * xy[1]

    def fireBullet(self, angle):
        bulletAngle = self.angle + angle
        pos = self.ship.pos.copy()    
        bullet = self.game.bullets.create(pos)
        bullet.rotate(bulletAngle)        
        bullet.rect.center = self.ship.rect.center
        pos[0] = float(bullet.rect[0])
        pos[1] = float(bullet.rect[1])
        
        xy = angleToXY(bulletAngle)
        bullet.vel[0] = -xy[0] * Bullets.speed
        bullet.vel[1] = -xy[1] * Bullets.speed
        bullet.reboundOnBorders = False
        self.game.bullets.add(bullet)

    def fire(self):
        if self.fireTimer.checkEnabled():
            return        
        self.fireTimer.start()

        self.fireBullet(0)
        if self.tripleShot:
            self.fireBullet(20)
            self.fireBullet(-20)

        GameData.sounds['Fire'].play()

    def fireBomb(self):
        if self.bombTimer.checkEnabled():
            return
        if self.bombs<1:
            return
        self.bombTimer.start()        
        self.bombs -= 1
        angle = 0.
        for i in range(0,12):            
            self.fireBullet(angle)
            angle += 30.
        self.game.updateTitle()
        GameData.sounds['Bomb'].play()

    def activateInvulnerability(self):
        self.invulnerability.start()

    def isInvulnerable(self):
        return self.invulnerability.checkEnabled()

    def powerUp(self, bonusType):
        #0: triple shot,
        #1: speed shot,
        #2: +1 lives,
        #3: +20 score,
        #4: shield,
        #5: +3 bombs
        if bonusType==0:
            self.tripleShot = True
        elif bonusType==1:
            self.fireTimer.duration = Player.speedShotTime
        elif bonusType==2:
            self.lives += 1
        elif bonusType==3:
            self.score += 20
        elif bonusType==4:
            self.setShieldLevel(3)
        elif bonusType==5:
            self.bombs += 3                                                

#--------------------
# PowerUp class
#--------------------

class PowerUp(VariableImageSprite):
    # sprite for showing the powerUps that appear on the screen
    def __init__(self):
        pos = randomPosition(60)        
        imageList = GameData.imageIds['PowerUp']
        self.bonusType = random.randint(0, len(imageList)-1)                
        VariableImageSprite.__init__(self, imageList, self.bonusType, pos)

    def activate(self, player):
        player.powerUp(self.bonusType)   
        self.kill()                

#--------------------
# PowerUps class
#--------------------

class PowerUps(SubGroup):
    # SubGroup that handles the powerUps
    # Every 3 seconds a new powerUp is spawned on a random position on the screen
    
    def __init__(self, game):
        SubGroup.__init__(self, game.sprites)
        self.timer = Timer(False, 3.0)

    def create(self):
        powerUp = PowerUp()
        self.add(powerUp)
        self.timer.start()

    def checkAndCreate(self):
        if self.timer.checkEnabled()==False:
            self.create()
            GameData.sounds['PowerUp2'].play()

    def reset(self):    
        for powerUp in self:
            powerUp.kill()
        self.timer.enabled = False

#--------------------
# Game class
#--------------------

class Game():
    # Main game class

    # Level parameters:
    # N: initial number of asteroids
    # Sm: min size of asteroids
    # SM: max size of asteroids
    # Sp: speed of asteroids

    levelData = [ [2, 3, 3, 3.],
                  [4, 4, 5, 3.],
                  [6, 5, 5, 3.],
                  [8, 5, 5, 3.]
                ]
    
    def __init__(self):
        self.sprites = pygame.sprite.RenderUpdates()
                        
        self.level = 1

        #initialize sprite entities
        self.player = Player(self)
        self.asteroids = Asteroids(self.sprites)
        self.bullets = Bullets(self.sprites)        
        self.powerUps = PowerUps(self)
        self.title = None #title will be initialized later

        self.clock = pygame.time.Clock()


    def tearDown(self):
        pygame.quit()

    def update(self):
        self.sprites.clear(GameData.screen, GameData.background)
        self.sprites.update()

        rects = self.sprites.draw(GameData.screen)
        pygame.display.update(rects)

    def reset(self):
        self.player.reset()
        self.asteroids.empty()
        self.bullets.empty()
        if self.title!=None:
            self.title.kill()
        self.sprites.empty()

    def createTitle(self):
        size = 30
        x = GameData.screen_dims[0]/2
        y = size/2
        self.title = TextSprite("title", "Arial", size, (255,0,0,255), (x,y))
        self.sprites.add(self.title)

    def updateTitle(self):
        text = "Level: " + str(self.level) + " Lives: " + str(self.player.lives) + " Score: " + str(self.player.score) + " Bombs: " + str(self.player.bombs)
        self.title.updateText(text)

    def initializeLevel(self):
        data = Game.levelData[self.level-1]
        N = data[0]
        Sm = data[1]
        SM = data[2]
        Asteroids.speed = data[3]
   
        self.asteroids.empty()        
        for i in range(0, N):
            self.asteroids.initialize(Sm, SM)

    def splashScreen(self, text, sound):
        size = 100
        x = GameData.screen_dims[0]/2
        y = GameData.screen_dims[1]/2
        startText = TextSprite(text, "Arial", size, (255,0,0,255), (x,y))
        self.sprites.add(startText)

        text2 = "Score: " + str(self.player.score)
        scoreText = TextSprite(text2, "Arial", 50, (255,0,0,255), (x,y+120))
        self.sprites.add(scoreText)
        
        self.update()
        GameData.sounds[sound].play()
        time.sleep(3.0)
        startText.kill()
        scoreText.kill()
    

    def startLevel(self):
        text = "Level " + str(self.level)
        sound = 'Start'
        self.splashScreen(text, sound)

    def gameWin(self):
        text = "Victory!"
        sound = 'Victory'
        self.splashScreen(text, sound)

    def gameOver(self):
        text = "Game Over!"
        sound = 'GameOver'
        self.splashScreen(text, sound)


    def doKeyboardEvents(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.rotateShip(+1)
        if keys[pygame.K_RIGHT]:
            self.player.rotateShip(-1)
        if keys[pygame.K_UP]:
            self.player.accelerateShip(+1)
        if keys[pygame.K_DOWN]:
            self.player.accelerateShip(-1)
        if keys[pygame.K_SPACE]:
            self.player.fire()
        if keys[pygame.K_x]:
            self.player.fireBomb()
        if keys[pygame.K_ESCAPE]:
            self.tearDown()

    def main(self):
        while self.player.lives>0 and self.level<len(Game.levelData):
            self.reset()
            self.startLevel()
            self.createTitle()
            self.updateTitle()
            self.player.reset()
            self.initializeLevel()

            self.player.activateInvulnerability()
            self.powerUps.reset()
            self.powerUps.create()

            collision = False
            while collision == False:
                pygame.event.pump()
                self.update()
                                     
                time.sleep(0.02)

                self.doKeyboardEvents()

                # slow down ship
                self.player.ship.vel[0] *= 0.99
                self.player.ship.vel[1] *= 0.99
                
                self.asteroids.update()

                self.bullets.destroyOnBoundary()

                if self.player.isInvulnerable() == False:
                    hits = pygame.sprite.spritecollide(self.player.ship, self.asteroids, False, pygame.sprite.collide_circle_ratio(0.7))
                    if hits:
                        if self.player.shieldLevel==0:
                            collision = True
                            self.player.lives -= 1
                            GameData.sounds['Explosion'].play()
                        else:
                            self.player.activateInvulnerability()
                            self.player.setShieldLevel(self.player.shieldLevel-1)
                            GameData.sounds['Shield'].play()
                        

                for bullet in self.bullets:
                    hits = pygame.sprite.spritecollide(bullet, self.asteroids, False, pygame.sprite.collide_circle_ratio(0.7))
                    if hits:
                        for asteroid in hits:
                            self.asteroids.destroy(asteroid, bullet)
                            self.player.score += 1
                        bullet.kill()
                        self.updateTitle()

                        if len(self.asteroids) == 0:
                            self.level += 1
                            collision = True                        
                            break

                if len(self.powerUps)>0:
                    hits = pygame.sprite.spritecollide(self.player.ship, self.powerUps, False, pygame.sprite.collide_circle_ratio(0.7))
                    if hits:
                        for powerUp in hits:
                            powerUp.activate(self.player)
                        self.updateTitle()
                        GameData.sounds['PowerUp'].play()

                self.powerUps.checkAndCreate()                                
                self.clock.tick()        

        if self.player.lives==0:
            self.gameOver()
        else:
            self.gameWin()

#--------------------
# program start
#--------------------

gameData = GameData("images/background2.png")

game = Game()
game.main()
