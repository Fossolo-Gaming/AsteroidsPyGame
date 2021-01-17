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
enemyHP       =  [ 1, 2, 3]
enemySpeedData = [ 3, 2, 1]

enemies = pygame.sprite.Group()
for i in range(0, numEnemy):
    enemyImage = Image(enemyImageNames[i])
    enemy = window.createSprite(enemyImage, path[0][0], path[0][1])
    enemy.index = i
    enemy.targetIndex = 1
    enemy.hitPoints = enemyHP[i]
    enemies.add(enemy)

enemyBulletImage = Image("images/towerDefense_tile298.png")
enemyBullets = pygame.sprite.Group()

clock = Clock()

quitGame = False

#ship parameters
speed = 5.
bulletSpeed = 7
lastTimeIFired = time.time()
minFireTime = 0.5

#enemy parameters
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
        enemySpeed  = float(enemySpeedData[index])
        targetIndex = enemy.targetIndex;
        
        targetX    = float(path[targetIndex][0])
        targetY    = float(path[targetIndex][1])

        enemyX = enemy.fpos[0]
        enemyY = enemy.fpos[1]
        #targetX = ship.rect.centerx
        #targetY = ship.rect.centery - 300
   

        deltaX = float(targetX - enemyX)
        deltaY = float(targetY - enemyY)
        dist = math.sqrt(deltaX*deltaX + deltaY*deltaY)
        
        if dist>enemySpeed: 
            deltaX *= enemySpeed/dist
            deltaY *= enemySpeed/dist

            #enemy ship is initially rotated facing down. Angle 0 is considered facing right, so we need to add 90 deg
            eAngle = VectorToAngle((deltaX, deltaY))            
            enemy.setAngle(eAngle)            
        
            enemy.moveRight(deltaX)
            enemy.moveDown(deltaY)
        else:
            print("enemy ", index, " target ", enemy.targetIndex, " reached")
            enemy.targetIndex += 1
            if enemy.targetIndex >= len(path):
                enemy.kill()            

        if False and enemyFire:
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
    for enemy in enemies:
        collisionGroup2 = pygame.sprite.spritecollide(enemy, bullets, True, pygame.sprite.collide_circle_ratio(0.9))
        collision2 = len(collisionGroup2)>0
        if collision2:        
            enemy.hitPoints-=1
            if enemy.hitPoints<=0:
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

