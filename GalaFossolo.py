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

speed = 5
bulletSpeed = 10
minFireTime = 0.25

# creazione finestra di PyGame
window = Window(1024, 768, 'images/background2.png')
keyboard = Keyboard()

# Creazione sprite

# astronave giocatore (player ship)
shipImage = Image("images/playerShip2_blue.png")
ship = window.createSprite(shipImage, 512, 650)

# proiettile (bullet)
bulletImage = Image("images/laserRed01.png")
bullets = pygame.sprite.Group()

# nemici
numEnemy = 3
enemyImages = [Image("images/enemyBlue3.png"),
               Image("images/enemyBlack4.png"),
               Image("images/enemyGreen2.png")]

enemies = pygame.sprite.Group()

# creazione orologio
clock = Clock()


def initLevel(level):
      for enemy in enemies:
            enemy.kill()

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

          collisionGroup = pygame.sprite.spritecollide(ship, enemies, False, pygame.sprite.collide_circle_ratio(0.9))
          if len(collisionGroup)>0:
                lives = lives - 1
                print("vite:", lives)
                quitGame = True

          for enemy in enemies:
                collisionGroup2 = pygame.sprite.spritecollide(enemy, bullets, True, pygame.sprite.collide_circle_ratio(0.9))
                if len(collisionGroup2)>0:
                      enemy.kill()

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

window.quit()

