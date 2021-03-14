# +-------------------------+
# |     Voi siete qui       |
# +-------------------------+
# |       FGLib             |
# +-------------------------+
# |       pygame            |
# +-------------------------+
# |       Python            |
# +-------------------------+

# import della libreria
from FGLib import *

# parametri del gioco
lives = 3
level = 0
score = 0

speed = 5
bulletSpeed = 10
minFireTime = 0.25

# creazione finestra di PyGame
window = Window(1024, 768, 'images/background2.png')
keyboard = Keyboard()
sound = Sound()

# Creazione sprite

# Immagine Esplosione
explosionImage = Image("images/boom.png")

# astronave giocatore (player ship)
shipImage = Image("images/playerShip2_blue.png")
ship = window.createSprite(shipImage, 512, 650)

# proiettile (bullet)
bulletImage = Image("images/laserRed01.png")
bullets = pygame.sprite.Group()

# power ups
powerUps = pygame.sprite.Group()
powerUpsImages = [Image("images/powerupRed_bolt.png"),
                  Image("images/powerupYellow_bolt.png"),
                  Image("images/powerupGreen_star.png"),
                  Image("images/star_gold.png"),
                  Image("images/shield_silver.png"),
                  Image("images/star_bronze.png")]
powerUpElapsedTime = 3.0

# nemici
numEnemy = 3
enemyImages = [Image("images/enemyBlue3.png"),
               Image("images/enemyBlack4.png"),
               Image("images/enemyGreen2.png")]

enemies = pygame.sprite.Group()

# Dizionario con i filename dei suoni
soundNames = { 'Fire':          "sound/laser.wav",
               'Explosion' :    "sound/explosion.wav",
               'AsteroidBreak': "sound/asteroidbreak.wav",
               'PowerUp':       "sound/powerup.wav",
               'Shield':        "sound/shield.wav",
               'Bomb':          "sound/laser2.wav",
               'PowerUp2':      "sound/powerup2.wav",
               'Start':         "sound/start.wav",
               'GameOver':      "sound/gameover.wav",
               'Victory':       "sound/victory.wav"}

for key, filename in soundNames.items():
    sound.load(key, filename)

# creazione orologio
clock = Clock()


red = (255, 0, 0, 255) #RGBA = (rosso, giallo, blu, alpha = opacita')
titleText = window.createText("", "Arial", 20, red, 500, 20)

def randomPosition(offset = 0):
    # generates a random position [x,y] on the screen
    # offset reduces the screen area by an offset around the border
    L = 1024 - 2 * offset
    H = 765 - 2 * offset

    x = int(random.uniform(0, L)) + offset
    y = int(random.uniform(0, H)) + offset
    return [x, y]

def splashScreen(text, soundKey):
      bigText = window.createText(text, "Arial", 150, red, 512, 350)
      window.draw()
      sound.play(soundKey)
      pygame.time.wait(3000)
      bigText.kill()
      window.draw()           

def updateGameStats():
      text = "Level: " + str(level) + " Lives: " + str(lives) + " Score: " + str(score)
      titleText.updateText(text)
      

def initLevel(level):
      for enemy in enemies:
            enemy.kill()

      # ridisegna lo schermo, produce il suono "let's start!" e attende 3 secondi
      updateGameStats()

      splashScreen("Level: " + str(level), 'Start')

      #inizializza il livello      
      if   level==0:
            enemy0 = window.createSprite(enemyImages[0], 700, 300)
            enemy0.speed = 3
            enemies.add(enemy0)            
            
      elif level==1:
            enemy0 = window.createSprite(enemyImages[0], 700, 300)
            enemy0.speed = 3
            enemies.add(enemy0)

            enemy1 = window.createSprite(enemyImages[1], 540, 230)
            enemy1.speed = 2
            enemies.add(enemy1)            
            
      elif level==2:
            enemy0 = window.createSprite(enemyImages[0], 700, 300)
            enemy0.speed = 3
            enemies.add(enemy0)            
            
            enemy1 = window.createSprite(enemyImages[1], 540, 230)
            enemy1.speed = 2
            enemies.add(enemy1)

            enemy2 = window.createSprite(enemyImages[2], 100, 350)
            enemy2.speed = 1
            enemies.add(enemy2)


def mainLoop():
      global lives
      global level
      
      lastTimeFired = time.time()
      lastPowerUp = time.time()
      
      quitGame = False
      while quitGame == False:

          # leggi la tastiera
          keyboard.readKeys()

          if keyboard.esc():
              quitGame = True

          if keyboard.left():
              ship.moveLeft(speed)

          if keyboard.right():
              ship.moveRight(speed)

          if keyboard.up():
              ship.moveUp(speed)

          if keyboard.down():
              ship.moveDown(speed)

          if keyboard.space():                
              currTime = time.time()
              elapsedTime = currTime - lastTimeFired
              if elapsedTime > minFireTime:                
                  x = ship.rect.centerx
                  y = ship.rect.centery
                  bullet = window.createSprite(bulletImage, x, y)
                  bullets.add(bullet)
                  lastTimeFired = currTime
                  sound.play('Fire')

          # muovi i proiettili
          for bullet in bullets:
              bullet.moveUp(bulletSpeed)
              if bullet.rect.bottom < 0:
                  bullet.kill()

          # px, py: coordinate dell'astronave del giocatore
          px = ship.rect.centerx
          py = ship.rect.centery
          
          # muovi i nemici
          for enemy in enemies:
              ex = enemy.rect.centerx
              if ex < px:
                    enemy.moveRight(enemy.speed)
              elif ex > px:
                    enemy.moveLeft(enemy.speed)
                    
              ey = enemy.rect.centery
              if ey < py:
                    enemy.moveDown(enemy.speed)
              elif ey > py:
                    enemy.moveUp(enemy.speed)

          # Power ups
          currTime = time.time()
          elapsedTime = currTime - lastPowerUp
          if elapsedTime > powerUpElapsedTime:                
                [x, y] = randomPosition(50)
                imageIndex = random.randint(0,5)
                powerUp = window.createSprite(powerUpsImages[imageIndex], x, y)
                powerUps.add(powerUp)
                lastPowerUp = currTime
      
          # controllo collisioni

          # collisione fra l'astronave del giocatore e quelle nemiche
          collisionGroup = pygame.sprite.spritecollide(ship, enemies, False, pygame.sprite.collide_circle_ratio(0.9))
          if len(collisionGroup)>0:
                lives = lives - 1
                print("vite:", lives)
                sound.play('Explosion')
                #ship.setImage(explosionImage)
                #px = ship.rect.centerx
                #py = ship.rect.centery
                #ship.setPosition(px, py)
                #window.draw()
                #pygame.time.wait(3000)
                #ship.setImage(shipImage)                               
                quitGame = True

          # collisione fra astronave e powerup
          collisionGroup3 = pygame.sprite.spritecollide(ship, powerUps, False, pygame.sprite.collide_circle_ratio(0.9))
          if len(collisionGroup3)>0:
                sound.play('PowerUp')
                for powerUp in collisionGroup3:
                      powerUp.kill()
                      # TO DO: aggiungere il bonus derivante dal power up

          # collisione fra le astronavi nemiche e i proiettili
          for enemy in enemies:
                collisionGroup2 = pygame.sprite.spritecollide(enemy, bullets, True, pygame.sprite.collide_circle_ratio(0.9))
                if len(collisionGroup2)>0:
                      enemy.kill()
                      sound.play('AsteroidBreak')

          # controllo se tutte le astronavi nemiche sono state distrutte passa al livello successivo
          if len(enemies)==0:
                level = level + 1 
                quitGame = True                
                    
          window.draw()
          
          # wait    
          clock.tick(60)



# inizio gioco
while lives>0 and level<3:
      print("Livello: ", level, " Vite: ", lives)
      initLevel(level)
      mainLoop()    

if lives<=0:
      splashScreen("Game Over!", 'GameOver')
elif level>=3:
      splashScreen("Victory!", 'Victory')


window.quit()

