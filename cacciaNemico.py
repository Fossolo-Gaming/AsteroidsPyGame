from FGLib import *

window = Window(1024, 768, "images/background2.png")
keyboard = Keyboard()

# Sprite creation
shipImage = Image("images/playerShip2_blue.png")
ship = window.createSprite(shipImage, 700 , 300)

enemyImage = Image("images/enemyBlue3.png")
enemy = window.createSprite(enemyImage, 500, 400)

enemies = pygame.sprite.GroupSingle(enemy)

clock = Clock()

quitGame = False
speed = 5
enemySpeed = 2

while quitGame == False:
    # keyboard control
    keyboard.readKeys()
    
    if keyboard.left():
        ship.moveLeft(speed)
    if keyboard.right():
        ship.moveRight(speed)        
    if keyboard.up():
        ship.moveUp(speed)
    if keyboard.down():
        ship.moveDown(speed)

    enemyX = enemy.rect.centerx
    enemyY = enemy.rect.centery
    shipX = ship.rect.centerx
    shipY = ship.rect.centery

    if (enemy.rect.centerx - ship.rect.centerx) < -enemySpeed:
         enemy.moveRight(enemySpeed)
    elif (enemy.rect.centerx - ship.rect.centerx) > enemySpeed:
        enemy.moveLeft(enemySpeed)

    if (enemy.rect.centery - ship.rect.centery) < -enemySpeed:
         enemy.moveDown(enemySpeed)
    elif (enemy.rect.centery - ship.rect.centery) > enemySpeed:
        enemy.moveUp(enemySpeed)

    
    collisionGroup = pygame.sprite.spritecollide(ship, enemies, False, pygame.sprite.collide_circle_ratio(0.9))
    collision = len(collisionGroup)>0

    if collision:
        quitGame = True
    
    if keyboard.esc():
        quitGame = True

    window.draw()

    # wait    
    clock.tick(60)

#window.quit()

