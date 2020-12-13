from FGLib import *
import math

window = Window(1024, 768, "images/background2.png")
keyboard = Keyboard()

# Sprite creation
shipImage = Image("images/playerShip2_blue.png")
ship = window.createSprite(shipImage, 700 , 300)

bulletImage = Image("images/laserRed01.png")
bullets = pygame.sprite.Group()

#path
path = [[900,0], [450, 300], [1000, 450], [500, 600], [650, 700], [800, 600], [200, 450], [200, 0]]

# enemy creation
numEnemy = 3
enemyImageNames = ["images/enemyBlue3.png",
                   "images/enemyBlack4.png",
                   "images/enemyGreen2.png"]
enemyStartPos = [[500, 400], [300, 400], [100, 400]]
enemyTarget   = [[100, 600], [300, 600], [500, 600]]
enemySpeedData = [ 3, 2, 1]

enemies = pygame.sprite.Group()
for i in range(0, numEnemy):
    enemyImage = Image(enemyImageNames[i])
    enemy = window.createSprite(enemyImage, path[0][0], path[0][1])
    enemy.index = i
    enemy.targetIndex = 1
    enemies.add(enemy)

enemyBulletImage = Image("images/towerDefense_tile298.png")
enemyBullets = pygame.sprite.Group()

clock = Clock()

quitGame = False

#ship parameters
speed = 5
bulletSpeed = 7
lastTimeIFired = time.time()
minFireTime = 0.5

#enemy parameters
enemyHitPoints = 3
enemyBulletSpeed = 3
lastTimeEnemyFired = [time.time(), time.time(), time.time()]
minEnemyFireTime = 1.0
enemyFire = True


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
    if keyboard.space():
        currTime = time.time()
        elapsedTime = currTime - lastTimeIFired
        if elapsedTime > minFireTime:                       
            bullet = window.createSprite(bulletImage, ship.rect.centerx, ship.rect.centery - 70)
            bullets.add(bullet)
            lastTimeIFired = time.time()

    #bullets movement
    for bullet in bullets:
        bullet.moveUp(bulletSpeed)
        if bullet.rect.bottom < 0:
            bullet.kill()
    
    #enemy AI
    for enemy in enemies:        

        index       = enemy.index
        enemySpeed  = enemySpeedData[index]
        targetIndex = enemy.targetIndex;
        
        targetX    = path[targetIndex][0]
        targetY    = path[targetIndex][1]

        enemyX = enemy.rect.centerx
        enemyY = enemy.rect.centery
        #targetX = ship.rect.centerx
        #targetY = ship.rect.centery - 300

        isCloseToTargetX = False
        isCloseToTargetY = False        

        deltaX = enemy.rect.centerx - targetX
        deltaY = enemy.rect.centerx - targetY

        dist = math.sqrt(deltaX*deltaX + deltaY*deltaY)
        shiftX = 0.0
        shiftY = 0.0
        if dist>0.0:
            shiftX = deltaX * enemySpeed/dist
            shiftY = deltaY * enemySpeed/dist
        

        
        if (enemy.rect.centerx - targetX) < -enemySpeed:
            enemy.moveRight(shiftX)
        elif (enemy.rect.centerx - targetX) > enemySpeed:
            enemy.moveLeft(shiftX)
        else:
            isCloseToTargetX = True

        if (enemy.rect.centery - targetY) < -enemySpeed:
            enemy.moveDown(shiftY)
        elif (enemy.rect.centery - targetY) > enemySpeed:
            enemy.moveUp(shiftY)
        else:
            isCloseToTargetY = True

        if isCloseToTargetX and isCloseToTargetY:
            enemy.targetIndex += 1
            if enemy.targetIndex >= len(path):
                enemy.kill()            

        if enemyFire:
            currTime = time.time()
            elapsedTime = currTime - lastTimeEnemyFired[index]
            if elapsedTime > minEnemyFireTime:
                px = enemy.rect.centerx - 30#enemyBulletImage.rect.width
                py = enemy.rect.centery + 30
                enemyBullet = window.createSprite(enemyBulletImage, px, py)
                enemyBullets.add(enemyBullet)
                lastTimeEnemyFired[index] = time.time()
    
   #enemy bullets movement
    for enemyBullet in enemyBullets:
        enemyBullet.moveDown(enemyBulletSpeed)
        if enemyBullet.rect.top > 768:
            enemyBullet.kill()    

    # check collisions

    # enemy VS ship collision
    collisionGroup = pygame.sprite.spritecollide(ship, enemies, False, pygame.sprite.collide_circle_ratio(0.9))
    collision = len(collisionGroup)>0
    if collision:
        quitGame = True
        
    # bullet VS enemy
    collisionGroup2 = pygame.sprite.spritecollide(enemy, bullets, True, pygame.sprite.collide_circle_ratio(0.9))
    collision2 = len(collisionGroup2)>0
    if collision2:
        enemyHitPoints-=1
        if enemyHitPoints<=0:
            enemy.kill()

    # enemyBullets VS ship collision
    collisionGroup3 = pygame.sprite.spritecollide(ship, enemyBullets, False, pygame.sprite.collide_circle_ratio(0.9))
    collision3 = len(collisionGroup3)>0
    if collision3:
        quitGame = True            
    
    if keyboard.esc():
        quitGame = True

    window.draw()

    # wait    
    clock.tick(60)

window.quit()

