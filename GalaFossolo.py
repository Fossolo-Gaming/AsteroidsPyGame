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
speed = 5
bulletSpeed = 10
minFireTime = 0.25

# creazione finestra di PyGame
window = Window(1024, 768, 'images/background2.png')
keyboard = Keyboard()

# Creazione sprite

# astronave giocatore (player ship)
shipImage = Image("images/playerShip2_blue.png")
ship = window.createSprite(shipImage, 700, 300)

# proiettile (bullet)
bulletImage = Image("images/laserRed01.png")
bullets = pygame.sprite.Group()

# creazione orologio
clock = Clock()

# main loop

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

    # muovi gli sprite
    for bullet in bullets:
        bullet.moveUp(bulletSpeed)
        if bullet.rect.bottom < 0:
            bullet.kill()            
    
    window.draw()
    
    # wait    
    clock.tick(60)    

window.quit()

