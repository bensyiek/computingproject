import pygame
import pickle
import random
import os
import copy

#Setup pygame settings, as well as screen dimensions
pygame.mixer.pre_init(22050, -16, 2, 2048)
pygame.mixer.init()
pygame.init()

gameWidth = 768
gameHeight = 624
offset = [0,0,0]

#Create the screen, as well as the clock object that is used to control framerate
screen = pygame.display.set_mode((gameWidth,gameHeight+144))
gameDisplay = pygame.Surface((gameWidth,gameHeight))

clock = pygame.time.Clock()

font=pygame.font.Font('PixelFont.ttf',24)
smallfont=pygame.font.Font('PixelFont.ttf',18)

#Utility function that allows images to be loaded from a file
def loadImage(name):
    image = pygame.image.load(os.path.join('Sprites',name))
    return image

#Utility function that allows sounds to be loaded from a file
def loadSound(name):
    sound = pygame.mixer.Sound(os.path.join('Sounds',name))
    return sound

#Set the icon of the window, as well as the window title
pygame.display.set_caption("Save the Princess!")
pygame.display.set_icon(loadImage("playerdown.png"))


class Player(pygame.sprite.Sprite):
    def __init__(self,x=200,y=200,hp=10,maxhp=10,gridX=0,gridY=0,keys=0,bombs=0,gold=0,inventory=[["Potion",3,"potionsquare.png",True]],weapons=[],sword=[["playerswordleft.png","sword1.png",0],5,12,"sword","Basic Blade",1],name=""):
        #Initialise pygame Sprite class, so that it can be used
        pygame.sprite.Sprite.__init__(self)

        self.image = loadImage("playerdown.png")

        #Setup the player's size and position attributes
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect.x = x
        self.rect.y = y
        self.gridX = gridX
        self.gridY = gridY
        self.facing = 0

        #Speed attributes
        self.velx = 0
        self.vely = 0        

        #Health attributes
        self.hp = hp
        self.maxhp = maxhp
        
        #Load the player's inventory
        self.inventory = inventory
        self.item = 0
        self.keys = keys
        self.bombs = bombs
        self.gold = gold

        #Load the player's weapons, including a specific case when the player is first created
        self.weapons = weapons
        if weapons == []:
            self.weapons = [sword]
        self.sword = sword

        #Various cooldowns for the player class to utilise
        self.attackcd = 0
        self.firecd = 0
        self.bombcd = 0
        self.invuln = 0
        self.knockbacktick = [0,0]

        #Tick attributes
        self.tick = 0
        self.animtick = 0
        self.imageindex = 0
        
        self.state = "normal"

        #Load all the images the player will need to use
            #Done here so that images aren't reloaded every time
        self.imgall = [[[loadImage("playerdown.png"),loadImage("playerdown2.png")],[loadImage("playerright.png"),loadImage("playerright2.png")],[loadImage("playerup.png"),loadImage("playerup2.png")],[loadImage("playerleft.png"),loadImage("playerleft2.png")]],[loadImage("playerattackdown.png"),loadImage("playerattackright.png"),loadImage("playerattackup.png"),loadImage("playerattackleft.png")]]
        self.images = self.imgall[0]

        self.name = name

    def isAvailable(self):
        #Returns true when the player is 'free', as in not doing any other major action
        if self.state != "dead" and self.state != "attacking" and self.state != "busy" and self.state != "shooting" and self.knockbacktick[0] == 0:
            return True
        else:
            return False

    def setPos(self,x,y,gridx,gridy):
        #Set a specific position for the player, including which room this is
        self.rect.x = x
        self.rect.y = y
        self.gridX = gridx
        self.gridY = gridy

    def shoot(self,image,direction,damage,speed=14,piercing=False,shottype="",special=""):
        #Method to create a projectile for the player
        proj = Bullet(self.rect.x+self.width/2,self.rect.y+self.height/2,self.facing,friendly=True,image=image,damage=damage,speed=speed,piercing=piercing,special=special)

        #If the shottype is a sword, then this is a projectile thrown from the player's weapon and so should be tracked separately
        if shottype == "sword":
            playerShotSprites.add(proj)
        bulletSprites.add(proj)

    def move(self,direction,speed):
        #Allows player to move in a direction, if they are available
        if self.isAvailable():
            #Handle the animation of walking
            if speed > 0:
                self.animtick += 1
            else:
                self.imageindex = 0
            if self.animtick == 7:
                self.imageindex += 1
            elif self.animtick == 14:
                self.imageindex -= 1
                self.animtick = 0

            #Change the direction they are facing, and change position based on direction
            self.facing = direction
            
            if direction == 1:
                self.rect.x += speed
            elif direction == 3:
                self.rect.x -= speed
            elif direction == 2:
                self.rect.y -= speed
            elif direction == 0:
                self.rect.y += speed

        #If the player collides with a wall, move them back outside of the wall
        if pygame.sprite.spritecollide(self,wallSprites,False) or pygame.sprite.spritecollide(self,invisWallSprites,False):
            if direction == 1:
                self.rect.x -= speed  
            elif direction == 3:
                self.rect.x += speed
            elif direction == 2:
                self.rect.y += speed
            elif direction == 0:
                self.rect.y -= speed

            #This is the 'auto-correct' feature of walking - if the player is just colliding with part of a wall, try to move them a little so they don't collide
            if direction == 1 or direction == 3:
                if self.rect.y % 48 > 24:
                    self.rect.y += 1
                elif self.rect.y % 24 < 24:
                    self.rect.y -= 1
            elif direction == 0 or direction == 2:
                if self.rect.x % 48 > 24:
                    self.rect.x += 1
                elif self.rect.x % 24 < 24:
                    self.rect.x -= 1

        #Check to see if the player has left the current room and if so load the room
        if self.rect.x > gameWidth- self.width/2:
            self.gridX += 1
            self.rect.x = 0
            loadRoom()
        elif self.rect.x < 0-self.width/2:
            self.gridX -= 1
            self.rect.x = gameWidth - self.width
            loadRoom()
        elif self.rect.y > gameHeight-self.height/2:
            self.gridY += 1
            self.rect.y = 0
            loadRoom()
        elif self.rect.y < 0-self.height/2:
            self.gridY -= 1
            self.rect.y = gameHeight - self.height
            loadRoom()

    def attack(self,direction):
        #Method to allow the player to use regular attacks
        if self.isAvailable() and self.attackcd <= 0:
            #Play a sound, change state, set correct cooldown and images
            loadSound("SwordSlash.wav").play()
            self.state = "attacking"
            self.attackcd = self.sword[2]+10
            self.images = self.imgall[1]
            self.image = self.images[self.facing]

            #Different size images need different offsets
            if self.sword[3] == "sword":
                soffset = 36
            elif self.sword[3] == "greatsword":
                soffset = 48
            elif self.sword[3] == "dagger":
                soffset = 24

            #Create a sword object based on which direction the player is facing in
            if self.facing == 0:
                playerBonusSprites.add(Sword(self.rect.x,self.rect.y+48,(pygame.transform.rotate(loadImage(self.sword[0][0]),90)),self.facing,self.sword[1],self.sword[2]))
            elif self.facing == 1:
                playerBonusSprites.add(Sword(self.rect.x+48,self.rect.y,(pygame.transform.flip(loadImage(self.sword[0][0]),True,False)),self.facing,self.sword[1],self.sword[2]))
            elif self.facing == 2:
                playerBonusSprites.add(Sword(self.rect.x,self.rect.y-soffset,(pygame.transform.rotate(loadImage(self.sword[0][0]),270)),self.facing,self.sword[1],self.sword[2]))
            elif self.facing == 3:
                playerBonusSprites.add(Sword(self.rect.x-soffset,self.rect.y,loadImage(self.sword[0][0]),self.facing,self.sword[1],self.sword[2]))

            #Check to see whether or not the player can throw the sword or dagger - if so, then create a projectile
            if self.sword[3] == "sword" and self.hp == self.maxhp and len(playerShotSprites) == 0:
                self.shoot(self.sword[0][1],self.facing,self.sword[1],speed=8,shottype="sword")
            elif self.sword[3] == "dagger" and (self.hp == self.maxhp or self.hp == 1) and len(playerShotSprites) < 2:
                self.shoot(self.sword[0][1],self.facing,self.sword[1],speed=8,shottype="sword")

    def bomb(self):
        #Method to allow the player to place bombs
        if self.bombcd <= 0 and self.isAvailable() and self.bombs > 0:
            #If the player has passed the check and can place a bomb, decrease bomb counter, increase cooldown
            self.bombs -= 1
            loadSound("BombDrop.wav").play()
            self.bombcd = 60

            #Depending on the direction you are facing, need a different offset for the bomb
            if self.facing == 0:
                bomboffset = [0,1]
            elif self.facing == 1:
                bomboffset = [1,0]
            elif self.facing == 2:
                bomboffset = [0,-1]
            elif self.facing == 3:
                bomboffset = [-1,0]

            #Create the bomb at the correct location
            itemSprites.add(Bomb(self.rect.centerx+bomboffset[0]*48,self.rect.centery+bomboffset[1]*48,"bomb.png",center=True))

    def dodamage(self,amount):
        #Method to handle the player taking damage
        #Add screenshake, play a hurt sound, decrease health, and set invulnerability period
        screenShake(amount*5)
        loadSound("PlayerHurt.wav").play()
        self.hp -= amount
        self.invuln = 40

        #If the player runs out of health, they die
        if self.hp <= 0:
            self.hp = 0
            self.die()

    def heal(self,amount):
        #Method to heal the player
        #Play heal sound, and increase health
        loadSound("Heart.wav").play()
        self.hp += amount

        #Make sure the player doesn't overheal
        if self.hp > self.maxhp:
            self.hp = self.maxhp

    def fire(self,direction):
        #Method for the player to use the candle and create a fire
        if self.firecd == 0:
            #If the player is able to create a fire, check which direction they are facing for the offset
            if direction == 0:
                fireoffset = [0,1]
            elif direction == 1:
                fireoffset = [1,0]
            elif direction == 2:
                fireoffset = [0,-1]
            elif direction == 3:
                fireoffset = [-1,0]

            #Set cooldown, and then create the fire 
            self.attackcd = 30
            self.firecd = 1
            effectSprites.add(Fire(self.rect.x+fireoffset[0]*48,self.rect.y+fireoffset[1]*48,[["fire.png",7],["fire2.png",7]],120,fireoffset[0]*2,fireoffset[1]*2,5))
            

    def die(self):
        self.state = "dead"

    def useItem(self):
        #Method to allow the player to use items
        #Need to check the player has items and can use them
        if self.isAvailable() and self.attackcd <= 0 and len(self.inventory) > 0:
            #Get the item name and do different things based on which item is used
            itemname = self.inventory[self.item][0]
            
            #Potion heals the player and has a cooldown
            if itemname == "Potion":
                self.heal(10)
                self.attackcd = 30

            #Fire tome creates a fire projectile
            elif itemname == "Tome: Fire":
                self.attackcd = 20
                loadSound("Fire.wav").play()
                self.shoot("fire.png",self.facing,10,15,special="fire")

            #Lightning tome deals damage to multiple enemies on screen
            elif itemname == "Tome: Lightning":
                loadSound("Lightning.wav").play()
                self.attackcd = 20

                #Lightning only guaranteed to deal damage to first three enemies on screen, then a decreasing chance for each other enemy
                enemyCount = 1
                if len(enemySprites) > 0:
                    for enemy in enemySprites:
                        if enemyCount < 3 or random.randint(1,enemyCount-2) == 1:
                            enemyCount += 1
                            effectSprites.add(Effect(enemy.rect.x,enemy.rect.y-436,[["shock1.png",3],["shock2.png",3]],6))
                            enemy.dodamage(random.randint(5,20))

                        #Else if there were no enemies, strike the player with lightning
                        else:
                            effectSprites.add(Effect(self.rect.x,self.rect.y-436,[["shock1.png",3],["shock2.png",3]],6))
                            self.dodamage(2)
                            self.invuln = 0
                            self.knockbacktick = [10,0]

            #Candle creates a fire in front of the player
            elif itemname == "Candle":
                self.fire(self.facing)

            #If the item is consumeable, subtract one from its count
            if self.inventory[self.item][3] == True:
                self.inventory[self.item][1] -= 1

                #Check to see if its count is 0, if so then remove it from the player's inventory
                if self.inventory[self.item][1] == 0:
                    self.inventory.remove(self.inventory[self.item])
                    self.item = 0

    def giveItem(self,newItem,picture,useup=False):
        #Method to add an item to the player's inventory
        #Check to see whether the player has at least one of this item or not - if so, add to its count
        new = True
        for item in self.inventory:
            if item[0] == newItem:
                item[1] += 1
                new = False
                break

        #Else, add the new item
        if new:
            self.inventory.insert(0,[newItem,1,picture,useup])

        #Sort the player's inventory
        self.inventory.sort(key=lambda x: x[0])

    def giveWeapon(self,newWeapon):
        #Add a new weapon to the weapon list then sort the list
        self.weapons.append(newWeapon)
        self.weapons.sort(key=lambda x: x[5])

    def update(self):
        #Change the player's image
        if self.isAvailable():
            self.image = self.images[self.facing][self.imageindex]

        #Decrease cooldowns
        if self.bombcd > 0:
            self.bombcd -= 1

        if self.attackcd > 0:
            self.attackcd -= 1
            if self.attackcd == 8:
                self.state = "normal"
                self.images = self.imgall[0]

        #If the player is being knocked back, change their position
        if self.knockbacktick[0] > 0:
            self.knockbacktick[0] -= 1
            if self.knockbacktick[1] == 1:
                self.velx = 12
                self.vely = 0
            elif self.knockbacktick[1] == 3:
                self.velx = -12
                self.vely = 0
            elif self.knockbacktick[1] == 0:
                self.vely = 12
                self.velx = 0
            elif self.knockbacktick[1] == 2:
                self.vely = -12
                self.velx = 0

            self.rect.x += self.velx
            self.rect.y += self.vely

            #If the player collides with a wall or goes out of bounds, revert the position change and set knockback duration to 0
            if pygame.sprite.spritecollide(self,wallSprites,False)or pygame.sprite.spritecollide(self,invisWallSprites,False) or self.rect.x+self.width > gameWidth or self.rect.x < 0 or self.rect.y+self.height > gameHeight or self.rect.y < 0:
                self.rect.x -= self.velx
                self.rect.y -= self.vely
                self.knockbacktick[0] = 0


        #If the player is invulnerable, reduce cooldown
        if self.invuln > 0:
            self.invuln -= 1

        #Else check for enemy collisions
        elif self.isAvailable():
              #If the player collides with an enemy, take damage and set knockback based on what direction the enemy is moving
              if pygame.sprite.spritecollide(self,enemySprites,False):
                for enemy in pygame.sprite.spritecollide(self,enemySprites,False):
                    
                     self.dodamage(enemy.damage)
                     self.knockbacktick[0] = 8

                     if enemy.velx > 0 and enemy.rect.x < self.rect.x:
                         self.knockbacktick[1] = 1
                     elif enemy.velx < 0 and enemy.rect.x > self.rect.x:
                         self.knockbacktick[1] = 3
                     elif enemy.vely > 0 and enemy.rect.y < self.rect.y:
                         self.knockbacktick[1] = 0
                     elif enemy.vely < 0 and enemy.rect.y > self.rect.y:
                         self.knockbacktick[1] = 2
                     elif self.facing == 0:
                         self.knockbacktick[1] = 2
                     elif self.facing == 1:
                         self.knockbacktick[1] = 3
                     elif self.facing == 2:
                         self.knockbacktick[1] = 0
                     else:
                         self.knockbacktick[1] = 1

              #Check if the player collides with a bullet
              for item in pygame.sprite.spritecollide(self,bulletSprites,False):
                    if item.friendly == False:
                        #If the bullet is an enemy bullet, check to see whether it is blocked
                        if self.state != "attacking" and (self.facing == 0 and item.direction == 2 or self.facing == 1 and item.direction == 3 or self.facing == 2 and item.direction == 0 or self.facing == 3 and item.direction == 1):
                            effectSprites.add(Effect(self.rect.x,self.rect.y,[["cloud1.png",6],["cloud2.png",6]],12))
                            item.die()
                        #Otherwise take damage
                        else:
                            self.dodamage(item.damage)
                            self.knockbacktick[1] = item.direction
                            self.knockbacktick[0] = 2
                            item.die()
                    

class Sword(pygame.sprite.Sprite):
    def __init__(self,x,y,image,facing,damage,maxtick):
        #Initiliase all attributes that are required by the sword object
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.facing = facing
        self.damage = damage
        self.tick = 0
        self.maxtick = maxtick
        
    def update(self):
        #Check to see whether the sword collides with an enemy, if so damage them
        for enemy in pygame.sprite.spritecollide(self,enemySprites,False):
                enemy.knockback(self.facing)
                enemy.dodamage(self.damage,direction=self.facing)

        #Increase tick count, once sword reaches maximum duration destroy it
        self.tick += 1
        if self.tick == self.maxtick:
            self.kill()
            del self

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction=0,friendly=False,special="",damage=1,image="",speed=5,piercing = False):
        #Setup initial bullet attributes
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        
        self.image = pygame.transform.rotate(loadImage(image),direction*90)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        
        self.damage = damage
        self.friendly = friendly
        self.special = special
        self.piercing = piercing

        #Based on which direction the bullet is facing, set x and y velocities
        if direction == 0:
            self.velx = 0
            self.vely = speed
        if direction == 1:
            self.velx = speed
            self.vely = 0
        elif direction == 2:
            self.velx = 0
            self.vely = -1*speed
        elif direction ==3:
            self.velx = -1*speed
            self.vely = 0
        
    def die(self):
        #Destroy the bullet
        self.kill()
        del self

    def update(self):
        #Change the bullet position
        self.rect.x += self.velx
        self.rect.y += self.vely
        #If the bullet collides or goes out of bounds, destroy it
        if self.piercing == False and pygame.sprite.spritecollide(self,wallSprites,False) or self.rect.x < -50 or self.rect.x > gameWidth + 50 or self.rect.y < -50 or self.rect.y > gameWidth + 50:
            self.die()

class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y,images, hp=5, damage=1, width=48,height=48):
        pygame.sprite.Sprite.__init__(self)

        #Initialise all images that the enemy uses
        self.images = []
        for item in images:
            self.images.append(loadImage(item))

        #Now setup all of the attributes they will use
        #Images
        self.imageindex = 0
        self.image = self.images[self.imageindex]
        self.rect = self.image.get_rect()
        
        #Size, positions
        self.width = width
        self.height = height
        self.rotation = 0
        self.direction = 0
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

        self.velx = 0
        self.vely = 0
        self.knockbacktick = [0,0]

        #Hp and tick
        self.hp = hp
        self.damage = damage
        self.invuln = 0
        self.tick = 0
        self.animtick = 0
        
    def collide(self,enemy=False):
        #Check for collisions - with walls or out of bounds
            #An argument is passed to see whether collisions with other enemies should be checked too
        if pygame.sprite.spritecollide(self,invisWallSprites,False) or pygame.sprite.spritecollide(self,wallSprites,False) or self.rect.x < 0 or self.rect.y < 0 or self.rect.x + self.width > gameWidth or self.rect.y + self.height > gameHeight or enemy == True and len(pygame.sprite.spritecollide(self,enemySprites,False)) > 1:
            return True

        #Option for collisions to be checked just with enemies of the same type
        elif enemy=="self":
            for collided in pygame.sprite.spritecollide(self,enemySprites,False):
                if type(collided) == type(self) and collided != self:
                    return True
          
    def knockback(self,direction,time=8):
        #Knockback
        self.knockbacktick[0] = time
        self.knockbacktick[1] = direction

    #Different damage types that are inherited and changed
    def firedamage(self,amount):
        self.dodamage(amount,direction=5)

    def rangeddamage(self,amount,direction):
        self.dodamage(amount,direction=direction)

    def bombDamage(self,amount,bypass=True,direction=5):
        self.dodamage(amount,bypass=bypass,direction=direction)

    def dodamage(self,amount,bypass=False,direction=5):
        #Method to deal damage to the enemy
        if self.invuln == 0 or bypass:
            #Play sound, deal damage
            loadSound("EnemyHurt.wav").play()
            for i in range(amount):
                effectSprites.add(Effect(self.rect.x,self.rect.y,[["hitmarker1.png",6],["hitmarker2.png",6]],12,velx=random.randint(-4,4),vely=random.randint(-4,4)))
                
            self.hp -= amount

            #Kill the enemy if hp is below or at 0
            if self.hp <= 0:
                self.die()
                
            #Otherwise give them invulnerability
            else:
                self.invuln = 15
                self.hit()

    def die(self):
        #Method to handle destruction of enemy
        loadSound("EnemyDie.wav").play()
        effectSprites.add(Effect(self.rect.x,self.rect.y,[["death1.png",7],["death2.png",7]],14))

        self.droploot()
        
        self.kill()
        del self

    def droploot(self):
        #Base loot drop with different chances for different loot
        chance = random.randint(1,25)
        if chance <= 5:
            itemSprites.add(Heart(self.rect.centerx,self.rect.centery))
        elif chance <= 8:
            itemSprites.add(BombPickup(self.rect.centerx,self.rect.centery))
        elif chance <= 14:
            itemSprites.add(Gold(self.rect.centerx,self.rect.centery))
        elif chance <= 18:
            itemSprites.add(Gold(self.rect.centerx,self.rect.centery,"gold2.png",5))
        elif chance <= 19:
            itemSprites.add(Gold(self.rect.centerx,self.rect.centery,"gold3.png",15))
        
    def update(self):
        #Decrease invulnerability cooldown
        if self.invuln > 0:
            self.invuln -= 1
            
        #Check for collisions with player projectiles
        for item in pygame.sprite.spritecollide(self,bulletSprites,False):
              if item.friendly == True:
                  if item.special == "fire":
                      self.firedamage(item.damage)
                  else:
                      self.rangeddamage(item.damage,direction=item.direction)
                  item.die()
        
        #If the enemy is being knocked back, change their position
        if self.knockbacktick[0] > 0:
            self.knockbacktick[0] -= 1
            if self.knockbacktick[1] == 1:
                self.knox = 12
                self.knoy = 0
            elif self.knockbacktick[1] == 3:
                self.knox = -12
                self.knoy = 0
            elif self.knockbacktick[1] == 0:
                self.knoy = 12
                self.knox = 0
            elif self.knockbacktick[1] == 2:
                self.knoy = -12
                self.knox = 0
            self.rect.x += self.knox
            self.rect.y += self.knoy
            #If the enemy collides, revert position change
            if self.collide(True):
                self.rect.x -= self.knox
                self.rect.y -= self.knoy

        #Otherwise do unique behaviour
        else:
            self.move()

    def move(self):
        pass

    def hit(self):
        pass

class Bug(Enemy):
    def __init__(self,x,y,images=["meany1.png","meany2.png"],hp=5,damage=1):
        super().__init__(x,y,images,hp,damage)
    
    def update(self):
        super().update()
        #Animation
        self.animtick += 1
        if self.animtick == 10:
            self.imageindex = 1
        elif self.animtick == 20:
            self.imageindex = 0
            self.animtick = 0
            
    def move(self):
        if self.tick == 24:
            #Pick a random direction to move in after a delay, or shoot a projectile
            self.tick = 0
            temp = random.randint(1,6)
            if temp == 1:
                self.direction = 1
                self.velx = 2
                self.vely = 0
            elif temp == 2:
                self.direction = 2
                self.velx = 0
                self.vely = -2
            elif temp == 3:
                self.direction = 3
                self.velx = -2
                self.vely = 0
            elif temp == 4:
                self.direction = 0
                self.velx = 0
                self.vely = 2
            elif temp == 5:
                self.velx = 0
                self.vely = 0
            elif temp == 6:
                self.velx = 0
                self.vely = 0
                bulletSprites.add(Bullet(self.rect.x+self.width/2,self.rect.y+self.height/2,direction=self.direction,friendly=False,image="rock.png",speed=10))

        #Change image rotation, update position
        self.image = pygame.transform.rotate(self.images[self.imageindex],self.direction * 90)
        self.rect.x += self.velx
        self.rect.y += self.vely
        if self.collide():
            self.rect.x -= self.velx
            self.rect.y -= self.vely
            self.tick = 23
        self.tick += 1

class BlueBug(Bug):
    def __init__(self,x,y):
        super().__init__(x,y,["meany3.png","meany4.png"],15,2)
        #More tough bug with same behaviour

class Orc(Enemy):
    def __init__(self,x,y,images=["rorcdown.png","rorcdown1.png","rorcright.png","rorcright1.png","rorcup.png","rorcup1.png","rorcleft.png","rorcleft1.png"],hp=15,damage=1,arrowimage="arrow2.png"):
        super().__init__(x,y,images,hp,damage=damage)
        #Another attribute for shot image
        self.arrowimage=arrowimage
            
    def move(self):
        #After a delay, choose a direction to move in or shoot
        if self.tick == 24:
            self.tick = 0
            temp = random.randint(1,5)
            if temp == 1:
                self.direction = 1

                self.velx = 2
                self.vely = 0
            elif temp == 2:
                self.direction = 2
                
                self.velx = 0
                self.vely = -2
            elif temp == 3:
                self.direction = 3

                self.velx = -2
                self.vely = 0
            elif temp == 4:
                self.direction = 0

                self.velx = 0
                self.vely = 2
            elif temp == 5:
                self.velx = 0
                self.vely = 0
                loadSound("Arrow.wav").play()
                bulletSprites.add(Bullet(self.rect.x+self.width/2,self.rect.y+self.height/2,self.direction,False,False,damage=self.damage,image=self.arrowimage,speed=6,piercing=True))

        #Update position
        self.rect.x += self.velx
        self.rect.y += self.vely
        if self.collide():
            self.rect.x -= self.velx
            self.rect.y -= self.vely
            self.tick = 23

        #Update tick count and image
        self.tick += 1
        if self.tick > 12:
            self.animtick = 1
        else:
            self.animtick = 0

        #Choose image
        self.image = self.images[2*self.direction+self.animtick]

class BlueOrc(Orc):
    def __init__(self,x,y,images=["orcdown.png","orcdown1.png","orcright.png","orcright1.png","orcup.png","orcup1.png","orcleft.png","orcleft1.png"],hp=25,damage=2,arrowimage="arrow3.png"):
        super().__init__(x,y,images,hp,damage=damage)
        #More tough orc with more health and damage

class Skeleton(Enemy):
    def __init__(self,x,y):
        super().__init__(x,y,images=["skeleton1.png","skeleton2.png"],hp=15,damage=1)
        
    def move(self):
        self.rect.x += self.velx
        self.rect.y += self.vely
        #Pick an initial direction to move in and then check for collisions
        if self.tick == 0 or self.collide("self"):
            #Upon collision, choose a new direction to move in
            self.rect.x -= self.velx
            self.rect.y -= self.vely
            temp = random.randint(1,4)
            if temp == 1:
                self.velx = 4
                self.vely = 0
            elif temp == 2:
                self.velx = 0
                self.vely = -4
            elif temp == 3:
                self.velx = -4
                self.vely = 0
            elif temp == 4:
                self.velx = 0
                self.vely = 4

        #Handle animation
        self.tick += 1
        if self.tick == 12:
            self.animtick = 1
        elif self.tick == 24:
            self.animtick = 0
            self.tick = 1
        self.image = self.images[self.animtick]

class Mummy(Enemy):
    def __init__(self,x,y):
        super().__init__(x,y,images=["mummy1.png","mummy2.png"],hp=25,damage=1)
        
    def move(self):
        self.rect.x += self.velx
        self.rect.y += self.vely
        #Choose a random direction to move in initially, upon collision, or at a random check
        if self.tick == 0 or self.collide(True) or random.randint(1,30) == 1:
            self.rect.x -= self.velx
            self.rect.y -= self.vely
            temp = random.randint(1,4)
            if temp == 1:
                self.velx = 2
                self.vely = 0
            elif temp == 2:
                self.velx = 0
                self.vely = -2
            elif temp == 3:
                self.velx = -2
                self.vely = 0
            elif temp == 4:
                self.velx = 0
                self.vely = 2

        #Change image
        self.tick += 1
        if self.tick == 12:
            self.image = self.images[1]
        elif self.tick == 24:
            self.image = self.images[0]
            self.tick = 1
        
    def die(self):
        #Upon death, create a skeleton
        enemySprites.add(Skeleton(self.rect.x,self.rect.y))
        self.kill()
        del self

class Snowman(Enemy):
    def __init__(self,x,y):
        super().__init__(x,y,images=["snowman1.png","snowman2.png"],hp=15)
        self.velx = 2
        self.vely = 2

    def firedamage(self,amount):
        #Triple fire damage
        self.dodamage(amount*3)
        
    def move(self):
        self.tick += 1
        #Animation
        if self.tick == 15:
            self.image = self.images[1]
        elif self.tick == 30:
            self.image = self.images[0]
            self.tick = 0

        #Check for collisions and then reverse velocity
        self.rect.x += self.velx
        if self.collide("self"):
            self.rect.x -= self.velx
            self.velx *= -1

        self.rect.y += self.vely
        if self.collide("self"):
            self.rect.y -= self.vely
            self.vely *= -1 

class Knight(Enemy):
    def __init__(self,x,y,images=["rknightdown.png","rknightdown1.png","rknightright.png","rknightright1.png","rknightup.png","rknightup1.png","rknightleft.png","rknightleft1.png"],hp=15,damage=1):
        super().__init__(x,y,images,hp,damage)
        
    def knockback(self,direction,amount=10):
        #Override so that the knight takes increased knockbackback from the front
        super().knockback(direction,amount)
        
    def dodamage(self,amount,direction=5,bypass=False):
      if self.invuln <= 0:
        #Block damage from the front of the knight
        if self.position == 0 and direction == 2 or self.position == 1 and direction == 3 or self.position == 2 and direction == 0 or self.position == 3 and direction == 1:
            loadSound("Shield.wav").play()
            self.invulnerable = 10
        else:
            super().dodamage(amount)
            #This is called so that the knight has reduced knockback from the sides and back
            if direction <= 3:
                self.knockback(direction,amount=6)

        
    def move(self):
        self.rect.x += self.velx
        self.rect.y += self.vely

        #Similar to skeleton, choose random direction to  move in until collision, then choose another
        if self.tick == 0 or self.collide("self"):
            self.rect.x -= self.velx
            self.rect.y -= self.vely
            temp = random.randint(1,4)
            if temp == 1:
                self.position = 1
                self.velx = 4
                self.vely = 0
            elif temp == 2:
                self.position = 2
                self.velx = 0
                self.vely = -4
            elif temp == 3:
                self.position = 3
                self.velx = -4
                self.vely = 0
            elif temp == 4:
                self.position = 0
                self.velx = 0
                self.vely = 4

        #Animation handling
        self.tick += 1
        if self.tick == 12:
            self.animtick = 1
        elif self.tick == 24:
            self.animtick = 0
            self.tick = 1
        
        self.image = self.images[self.position*2+self.animtick]

class BlueKnight(Knight):
    def __init__(self,x,y):
        super().__init__(x,y,images=["knightdown.png","knightdown1.png","knightright.png","knightright1.png","knightup.png","knightup1.png","knightleft.png","knightleft1.png"],hp=25,damage=2)
        #Tougher version of knight with more health and damage

class Dragon(Enemy):
    def __init__(self,x,y,images=["dragon1.png","dragon2.png","dragon3.png","dragon4.png"],width=72,height=96,hp=150):
        super().__init__(x,y,images,hp=hp,width=width,height=height,damage=3)
        #Setup additional attributes that are used in the class methods
        self.fireup = 1
        self.velx = 1
        self.damage = 3
        self.type = "boss"

        self.position = 0

    def firedamage(self,amount):
        #Reduced fire damage
        self.dodamage(int(amount/5))

    def bulletDamage(self,amount,direction=5):
        #Reduced bullet damage
        self.dodamage(int(amount/4))

    def bombDamage(self,amount,bypass):
        #Reduced bomb damage
        self.dodamage(int(amount/3),direction=5,bypass=True)

    def knockback(self,direction):
        #No knockback
        pass
        
    def update(self):
        super().update()
    
        self.tick += 1
        self.animtick += 1

        #Deal with animation
        if self.animtick == 10:
            self.position +=1
        elif self.animtick == 20:
            self.position -=1
            self.animtick = -1
            #Reverse velx so that dragon moves back and forth
            self.velx *= -1

        self.rect.x += self.velx
        self.image = self.images[self.position]

        #Prevent the player form moving right of the dragon
        while player.rect.x+36 > self.rect.x:
            player.rect.x -= 3

        #Start attack sequence, warn of attack
        if self.tick == 120:
            loadSound("Dragon.wav").play()
            self.position += 2

        #Check that starts the actual attack, time delay between two decreases as dragon is injured more
        elif self.tick > 140+self.hp/5:
            temp = random.randint(1,2)
            #Create fires that go to random locations on screen
            if temp == 1:
              for i in range(6):
                effectSprites.add(Fire(self.rect.x,self.rect.y,[["fire.png",5],["fire2.png",5]],120,random.randint(-10,-4),random.randint(0,4)*self.fireup,1,friendly=False))
                self.fireup *= -1
            #Or fire two fire 'bullets' in front
            else:
                bulletSprites.add(Bullet(self.rect.x,self.rect.y+24,3,False,"fire",image="fire.png",speed=10))
                bulletSprites.add(Bullet(self.rect.x,self.rect.y+72,3,False,"fire",image="fire.png",speed=10))
            loadSound("Fire.wav").play()
           
            self.tick = 0
            self.position -= 2

    def droploot(self):
        itemSprites.add(Gold(self.rect.centerx,self.rect.centery,"gold4.png",50))
        itemSprites.add(Gold(self.rect.centerx+32,self.rect.centery+48,"gold3.png",15))
        itemSprites.add(Gold(self.rect.centerx-32,self.rect.centery+48,"gold3.png",15))
        itemSprites.add(Gold(self.rect.centerx+32,self.rect.centery-48,"gold3.png",15))
        itemSprites.add(Gold(self.rect.centerx-32,self.rect.centery-48,"gold3.png",15))

    def die(self):
        loadSound("DragonDeath.wav").play()
        super().die()

class Effect(pygame.sprite.Sprite):
    def __init__(self,x,y,images,duration,velx=0,vely=0):
        pygame.sprite.Sprite.__init__(self)

        #Image attributes
        self.images = images
        self.image = loadImage(self.images[0][0])
        self.imageindex = 0

        #Timing attributes
        self.tick = 0
        self.totaltick = 0
        self.duration = duration

        #Position attributes
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velx = velx
        self.vely = vely
        

    def update(self):
        #Increase tick count, when it goes over current timer, try to swap to next image, and repeat
        if self.tick > self.images[self.imageindex][1]:
            self.imageindex += 1
            #If the index goes beyond maximum length, go back to start of list
            if self.imageindex == len(self.images):
                self.imageindex = 0
            self.image = loadImage(self.images[self.imageindex][0])
            self.tick = -1

        #Update ticks and position
        self.tick += 1
        self.totaltick += 1
        self.rect.x += self.velx
        self.rect.y += self.vely

        self.effect()

        #If the effect has been alive for its duration, destroy it
        if self.totaltick > self.duration:
            self.kill()
            del self

    def effect(self):
        pass

class Fire(Effect):
    def __init__(self,x,y,images,duration,velx,vely,strength,friendly=True):
        super().__init__(x,y,images,duration,velx,vely)
        self.strength = strength
        self.friendly = friendly
        
    def effect(self):
        #Deal damage to all enemies in fire, if fire belongs to player
        for enemy in pygame.sprite.spritecollide(self,enemySprites,False):
            if self.friendly:
                enemy.firedamage(self.strength)

        #Deal damage to the player if they are in the fire
        for player in pygame.sprite.spritecollide(self,playerSprites,False):
            if player.invuln <= 0:
                player.dodamage(1)

        #Stop the fire from moving after a set period
        if self.totaltick == 24 and self.friendly == True:
            self.velx = 0
            self.vely = 0
        
        elif self.totaltick == 48 and self.friendly == False:
            self.velx = 0
            self.vely = 0

class Item(pygame.sprite.Sprite):
    def __init__(self,x,y,image,attackinteract=False,center=False):
        pygame.sprite.Sprite.__init__(self)
        #Image
        self.image = loadImage(image)

        #Position
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        if center:
            self.rect.centerx = x
            self.rect.centery = y 
        else:
            self.rect.x = x*48
            self.rect.y = y*48

        #Other
        self.tick = 0
        self.interacted = False
        self.attackinteract = attackinteract

    def removeSelf(self):
        #Method to remove the item from the item database
        try:
            for item in itemDatabase[player.gridX, player.gridY]:
                if item[1][0] == self.x and item[1][1] == self.y:
                    itemDatabase[player.gridX, player.gridY].remove(item)
        except KeyError:
            pass
 
    def update(self):
        if self.tick < 10:
            self.tick += 1

        #If the player collides with the item for the first time, calls its interact method
        if pygame.sprite.spritecollide(self,playerSprites,False) and self.tick == 10  or pygame.sprite.spritecollide(self,playerBonusSprites,False) and self.attackinteract:
            if self.interacted == False:
                self.interacted = True
                self.interact()

    def interact(self):
        pass


class Princess(Item):
    def __init__(self,x,y):
        super().__init__(x,y,"princess.png",center=False)
        
    def interact(self):
        global state
        #Change the global state so that the player wins the game
        state = "victory"


class Pickup(Item):
    def __init__(self,x,y,image,utype,useUp=True):
        super().__init__(x,y,image,True)
        #Information needed to create an item for the player's inventory
        self.imageName = image
        self.utype = utype
        self.useUp = useUp
        self.timer = 10
        
    def interact(self):
        loadSound("Fanfare.wav").play()
        #If the utype is a str, then this is a useable item, in which case add it to the player's inventory
        if type(self.utype) == str:
            player.giveItem(self.utype,self.imageName,self.useUp)

        #Otherwise this is a weapon pickup, and so add that to the player's weapon list
        else:
            player.giveWeapon(self.utype)
            
        self.removeSelf()
        self.kill()


class ShopItem(Item):
    def __init__(self,x,y,image,cost,item,center=False,renewable=False):
        super().__init__(x,y,image,center=center)
        #Attributes needed for the shopItem to work
        self.cost = cost
        self.item = item
        self.renewable = renewable
        
    def update(self):
        global textSprites
        #Display the cost
        textSprites.append([str(self.cost),self.rect.x,self.rect.y+48])

        #Try to buy the item upon collision
        if pygame.sprite.spritecollide(self,playerSprites,False) and player.gold >= self.cost:
            player.gold -= self.cost

            #Create the item in the game world
            itemSprites.add(eval(self.item[0])(*self.item[1]))
            if self.renewable == False:
                self.removeSelf()
            self.kill()


class Key(Item):
    def __init__(self,x,y):
        super().__init__(x,y,"keysquare.png",center=False)
        
    def interact(self):
        #Add to the player's key count upon pickup
        loadSound("GetItem.wav").play()
        player.keys += 1
        self.removeSelf()
        self.kill()



class BombPickup(Item):
    def __init__(self,x,y):
        super().__init__(x,y,"bombsquare.png",center=True)
            
    def interact(self):
        #Add to the player's bomb count upon pickup
        loadSound("GetItem.wav").play()
        player.bombs += 2
        self.kill()

class Bomb(Item):
    def update(self):
        self.tick += 1
        #After a delay, detonate the bomb and create explosion effect in a pattern around the bomb
        if self.tick == 60:
            loadSound("BombBlow.wav").play()
            effectSprites.add(Explosion(self.rect.x,self.rect.y,[["cloud1.png",7],["cloud2.png",7]],14))
            effectSprites.add(Explosion(self.rect.x+46,self.rect.y,[["cloud1.png",7],["cloud2.png",7]],14))
            effectSprites.add(Explosion(self.rect.x-46,self.rect.y,[["cloud1.png",7],["cloud2.png",7]],14))
            effectSprites.add(Explosion(self.rect.x+32,self.rect.y+46,[["cloud1.png",7],["cloud2.png",7]],14))
            effectSprites.add(Explosion(self.rect.x+32,self.rect.y-46,[["cloud1.png",7],["cloud2.png",7]],14))
            effectSprites.add(Explosion(self.rect.x-32,self.rect.y+46,[["cloud1.png",7],["cloud2.png",7]],14))
            effectSprites.add(Explosion(self.rect.x-32,self.rect.y-46,[["cloud1.png",7],["cloud2.png",7]],14))
            self.kill()

class Explosion(Effect):
    def effect(self):
        #Deal damage to all enemies caught in the blast
        if self.totaltick < 6:
            for enemy in pygame.sprite.spritecollide(self,enemySprites,False):
                enemy.bombDamage(2,bypass=True)


class Gold(Item):
    def __init__(self,x,y,image="gold1.png",value=1):
        super().__init__(x,y,image,center=True)
        self.value = value
        
    def interact(self):
        #Upon collision, add to the player's gold count
        loadSound("Rupee.wav").play()
        player.gold += self.value
        self.removeSelf()
        self.kill()
        del self

class Heart(Item):
    def __init__(self,x,y):
        super().__init__(x,y,"heart.png",center=True)
                                  
    def interact(self):
        #Upon collision, heal the player
        player.heal(2)
        self.kill()

class TeleDoor(Item):
    def __init__(self,x,y,image,newx,newy,newgridx,newgridy):
        super().__init__(x,y,image)
        
        #Attributes to store the position the player should be moved to
        self.newx = newx
        self.newy = newy
        self.newgridx = newgridx
        self.newgridy = newgridy

    def interact(self):
        #Upon collision, set the player's position
        player.setPos(self.newx*48,self.newy*48,self.newgridx,self.newgridy)
        loadRoom()


class Door(Item):
    def __init__(self,x,y,image):
        super().__init__(x,y,image,attackinteract=True)
        wallSprites.add(self)

    def interact(self):
        #Door that requires the player to attack it with a key in their inventory
        self.interacted = False

        #If this is true, then destroy the door and remove a key from the player
        if player.keys > 0:
            loadSound("DoorUnlock.wav").play()
            player.keys -= 1
            self.removeSelf()
            self.kill()
            del self


class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y,width=48,height=48,colour=(0,0,0)):
        #Basic class to handle walls in the game world
        pygame.sprite.Sprite.__init__(self)

        #Invisible wall
        if colour=="none":
            self.rect = ((x,y),(width,height))

        #Wall using a sprite
        elif type(colour) == str:
            self.image = loadImage(colour)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

        #Otherwise this is a background block colour
        else:
            self.image = pygame.Surface( (width,height) )
            self.image.fill(colour)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y


def loadRoom(enemies=True):
    #Clear these sprite groups upon loading a new room
    deleteGroups = [wallSprites,invisWallSprites,backgroundBlockSprites,backgroundSprites,enemySprites,bulletSprites,effectSprites,itemSprites]
    for group in deleteGroups:
        for item in group:
            item.kill()
            del item
            
    #Allow the player to use the candle again
    player.firecd = 0

    #Create the background
    backgroundBlockSprites.add(Wall(0,0,800,800,backgroundDatabase[(player.gridX,player.gridY)]))

    #Go through each row in the current room's database, and check each set of two characters
    tempy = -1
    for item in objectDatabase[(player.gridX,player.gridY)]:
        tempy += 1
        tempx = -1
        for character in [item[i:i+2] for i in range(0, len(item)-1, 2)]:
            tempx += 1

            #If the character corresponds to a tile that is in the background, add it to backgroundSprites group
            if character in ["PP","LL","W5","W6","W7","W8"]:
                backgroundSprites.add(Wall(tempx*48,tempy*48,colour=(character+".png")))

            #If the tile is water, add it to backgroundSprites, then create an invisible wall (so that projectiles travel over the water)
            elif character[0] == "W":
                backgroundSprites.add(Wall(tempx*48,tempy*48,colour=(character+".png")))
                invisWallSprites.add(Wall(tempx*48,tempy*48))

            #Otherwise if the tile is a regular wall, add it to wall sprite list
            elif character != "..":
                wallSprites.add(Wall(tempx*48,tempy*48,colour=(character+".png")))
            
    #If the room is being loaded via playing moving to it i.e. not loading a saved game, load enemies
    if enemies:
      try:
        #For each enemy, check if their spawn is far enough away from the player - if so, create the enemy, otherwise don't
        for item in enemyDatabase[(player.gridX,player.gridY)]:
            if item[0]*48 < player.rect.x+192 and item[0]*48 > player.rect.x-192 and item[1]*48< player.rect.y + 192 and item[1]*48 > player.rect.y - 192:
                pass
            else:
                enemySprites.add(eval(item[2])(item[0]*48,item[1]*48))
      except KeyError:
        pass

    #See if items exist in this room, if so load them in
    try:
        for item in itemDatabase[(player.gridX,player.gridY)]:
            itemSprites.add(eval(item[0])(*item[1]))
    except KeyError:
        pass
        
        
def drawUI():
    #Procedure to draw the display at the bottom of the screen
    #Draw the footer image, then render each of the basic texts 
    screen.blit(loadImage("footer.png"),(0,624))
    texts = [[font.render("HP: "+str(player.hp)+"/"+str(player.maxhp), 1,(0,0,0)),24,646],[font.render("GOLD: "+str(player.gold), 1, (0,0,0)),24,694],[font.render("BOMBS: "+str(player.bombs), 1,(0,0,0)),280,646],[font.render("KEYS: "+str(player.keys), 1,(0,0,0)),280,694],[smallfont.render("WEAPON ", 1,(0,0,0)),550,640],[smallfont.render("ITEM ", 1,(0,0,0)),675,640]]
    for text in texts:
        screen.blit(text[0],(text[1],text[2]))

    #Draw the player's current weapon sprites in position
    screen.blit(loadImage(player.sword[0][1]),(580,680))

    #If the player has items in their inventory, draw the equipped item in the item slot
    if len(player.inventory) > 0:
        screen.blit(loadImage(player.inventory[player.item][2]),(680,680))

        #If the item is consumeable, render text to display the item count
        if player.inventory[player.item][3] == True:
            text = smallfont.render("X "+str(player.inventory[player.item][1]), 1, (0,0,0))
        else:
            text = smallfont.render("X ∞", 1, (0,0,0))
        screen.blit(text, (680,730))
        


def menuDisplay(text,selection,x,y,ychange):
    #Procedure to draw basic menus, along with which item in the menu is currently displayed
    for i in range(len(text)):
        if i == selection-1:
            tempText = "> "
        else:
            tempText = ""
        textSprites.append([tempText+str(text[i]),x,y+i*ychange])


def saveGame():
    global player
    global itemDatabase
    
    #Only allow the game to save if there are no enemies on screen
    if len(enemySprites) == 0:
        
        #Add each attribute that needs saving to a single list, then save this to a file along with the item database
        attributes = [player.rect.x,player.rect.y,player.hp,player.maxhp,player.gridX,player.gridY,player.keys,player.bombs,player.gold,player.inventory,player.weapons,player.sword,player.name]
        with open("save.pickle","wb") as f:
            pickle.dump(attributes, f)
            pickle.dump(itemDatabase, f)
        return True

    #If there are enemies alive, play an error sound and don't save
    else:
        loadSound("playerHurt.wav").play()
        return False

def loadGame(fromSave=True):
    global player
    global itemDatabase

    #If the game is being loaded from a save (rather than from scratch):
    if fromSave:
        try:
            #Open the save file, and load the attributes list and item database
            with open("save.pickle","rb") as f:
                attributes = pickle.load(f)
                itemDatabase = pickle.load(f)

                #Create a new player object using the attributes in the list, then load the room
                player.kill()
                del player
                player = Player(*attributes)
                playerSprites.add(player)
                loadRoom(enemies=False)
                return True

        #If the player is trying to load without saving first, don't allow this - play an error sound
        except FileNotFoundError:
            loadSound("playerHurt.wav").play()
            return False

    #If this is a new game, create a new player and item database, then load the first room
    else:
        itemDatabase = copy.deepcopy(itemTemplateDatabase)
        player.kill()
        del player
        player = Player()
        playerSprites.add(player)
        loadRoom(enemies=False)


def screenShake(amount=0):
    global offset
    #If amount is > 0, then screenshake is being added
    if amount > 0:
        offset[2] = 5+amount

    #Randomise the amount the screen is offset by
    offset[0] = random.randint(-2*offset[2],2*offset[2])
    offset[1] = random.randint(-2*offset[2],2*offset[2])

    #If the timer runs out, set offset back to 0
    offset[2] -= 1
    if offset[2] == 0:
        offset[0], offset[1] = 0, 0
    

#Default state
state = "mainmenu"
def gameloop():
    global textSprites
    global offset
    global state
    running = True

    #Set the music
    pygame.mixer.music.load(os.path.join('Sounds',"Overworld.mp3"))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)

    selection = 1
    #Main menu state
    while running:
      if state == "mainmenu":

        #Set the text to be displayed and clear the screen, then draw text
        textSprites = []
        textSprites.append(["Save the Princess!",30,50])
        
        menuDisplay(["NEW GAME","LOAD GAME","QUIT"],selection,30,200,60)
        
        gameDisplay.fill((255,255,255))
        screen.fill((255,255,255))
        
        for item in textSprites:
            text=font.render(item[0], 1,(0,0,0))
            gameDisplay.blit(text, (item[1], item[2]))        

        #Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_RETURN:
                    loadSound("menuselect.wav").play()
                    if selection == 1:
                        loadGame(False)
                        state = "naming"
                        errors = []
                    elif selection == 2:
                        if loadGame():
                            state = "game"
                    elif selection == 3:
                        running = False
                        
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    loadSound("menumove.wav").play()
                    selection += 1
                    if selection > 3:
                        selection = 1
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    loadSound("menumove.wav").play()
                    selection -= 1
                    if selection < 1:
                        selection = 3

        #Update screen, and control framerate
        screen.blit(gameDisplay,(0,0))

        pygame.display.update()

        clock.tick(60)

      #State for entering name
      elif state == "naming":
        textSprites = []
        smallTextSprites = []
        #Add text for a few things
        textSprites.append(["Enter your name:",30,50])
        textSprites.append(["> Confirm",30,550])
        textSprites.append([str(player.name),30,100])

        #Add text for each error on a new line
        for i in range(len(errors)):
            smallTextSprites.append([str(errors[i]),30,200+i*30])

        gameDisplay.fill((255,255,255))
        screen.fill((255,255,255))
        
        for item in textSprites:
            text=font.render(item[0], 1,(0,0,0))
            gameDisplay.blit(text, (item[1], item[2]))

        for item in smallTextSprites:
            text=smallfont.render(item[0], 1,(0,0,0))
            gameDisplay.blit(text, (item[1], item[2]))

        #Draw the 'text entry' line
        pygame.draw.rect(gameDisplay,(0,0,0),((30+font.size(player.name)[0],100),(10,30)))

        #Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    loadSound("menuback.wav").play()
                    state = "mainmenu"
                #Attempt to enter the name
                elif event.key == pygame.K_RETURN:
                    loadSound("menuselect.wav").play()
                    errors = []
                    #Name must be between 3 and 15 characters, and only contain letters
                    if len(player.name) == 0:
                        errors.append("Please enter a name")
                    elif len(player.name) < 3:
                        errors.append("Name must be at least 3 characters long")
                    elif len(player.name) > 15:
                        errors.append("Name must be at most 15 characters long")

                    for character in player.name:
                        if ord(character) < 65 or ord(character) > 122 or ord(character) > 90 and ord(character) < 97:
                            errors.append("Name must be only letters.")
                            break

                    #If no errors have been detected in the name, then go to the main game state
                    if len(errors) == 0:
                        state = "game"

                elif event.key == pygame.K_BACKSPACE:
                    player.name = player.name[:-1]

                else:
                    if len(player.name) < 25:
                        player.name += event.unicode

        #Update screen, and control framerate
        screen.blit(gameDisplay,(0,0))

        pygame.display.update()

        clock.tick(60)

      #Pause State
      if state == "pause":

        #Clear screen, set text to be displayed, draw text
        textSprites = []
        textSprites.append(["PAUSED",30,50])
        
        menuDisplay(["SAVE GAME","LOAD GAME","MAIN MENU","QUIT"],selection,30,200,60)
        
        gameDisplay.fill((255,255,255))
        screen.fill((255,255,255))
        
        for item in textSprites:
            text=font.render(item[0], 1,(0,0,0))
            gameDisplay.blit(text, (item[1], item[2]))

        #Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    loadSound("menuback.wav").play()
                    state = "game"
                elif event.key == pygame.K_RETURN:
                    loadSound("menuselect.wav").play()
                    if selection == 1:
                        if saveGame():
                            state = "game"
                    elif selection == 2:
                        if loadGame():
                            state = "game"
                    elif selection == 3:
                        state = "mainmenu"
                    elif selection == 4:
                        running = False
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    loadSound("menumove.wav").play()
                    selection += 1
                    if selection > 4:
                        selection = 1
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    loadSound("menumove.wav").play()
                    selection -= 1
                    if selection < 1:
                        selection = 4

        #Update screen, and control framerate
        screen.blit(gameDisplay,(0,0))

        pygame.display.update()

        clock.tick(60)

      #Inventory state      
      if state == "inventory":
          #Clear the screen, set text to be displayed, then draw text
          textSprites = []
          gameDisplay.fill((255,255,255))
          screen.fill((255,255,255))
          textSprites.append(["INVENTORY",30,50])          

          menuDisplay(["Weapons","Items"],selection,30,200,60)

          for item in textSprites:
            text=font.render(item[0], 1,(0,0,0))
            gameDisplay.blit(text, (item[1], item[2]))

          #Handle events
          events = pygame.event.get()
          for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                    state = "game"
                    loadSound("menuback.wav").play()
                    
                elif event.key == pygame.K_RETURN:
                    loadSound("menuselect.wav").play()
                    if selection == 1:
                        state = "weapons"
                    elif selection == 2:
                        state = "items"
                        selection = 1
                    
                elif event.key == pygame.K_UP:
                    selection -= 1
                    loadSound("menumove.wav").play()
                    if selection < 1:
                        selection = 2
                        
                elif event.key == pygame.K_DOWN:
                    selection += 1
                    loadSound("menumove.wav").play()
                    if selection > 2:
                        selection = 1
        
          
          #Update screen, then control framerate
          screen.blit(gameDisplay,(0,0))

          pygame.display.update()

          clock.tick(60)

      #Item menu state
      if state == "items":
        #Set text to be displayed, clear screen
        textSprites = []
        gameDisplay.fill((255,255,255))
        newLocation = 0

        textSprites.append(["ITEMS",30,50])

        #For each item in the player's inventory, set its y position as well as which is selected, which is equipped, and the quantity of each one
        yoffset = 0
        for i in range(len(player.inventory)):
            yoffset += 1
            if i == selection-1:
                itemName = "> "
                newLocation = i
            else:
                itemName = ""

            itemName += player.inventory[i][0]
            textSprites.append([itemName,30,80+yoffset*40])
            
            itemCount = "X" + str(player.inventory[i][1])
            textSprites.append([itemCount,650,80+yoffset*40])

            #If index is equal to player's item attribute, this is the equipped item
            if i == player.item:
                textSprites.append(["Equipped",400,80+yoffset*40])    

        #Handle events
        events = pygame.event.get()  
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                    state = "inventory"
                    selection = 1
                    loadSound("menuback.wav").play()
                elif event.key == pygame.K_RETURN:
                    loadSound("menuselect.wav").play()
                    player.item = newLocation
                    
                elif event.key == pygame.K_UP:
                    selection -= 1
                    loadSound("menumove.wav").play()
                    if selection < 1:
                        selection = len(player.inventory)
                        
                elif event.key == pygame.K_DOWN:
                    selection += 1
                    loadSound("menumove.wav").play()
                    if selection >len(player.inventory):
                        selection = 1

        #Draw the UI at the bottom of the screen, as well as text
        drawUI()
        for item in textSprites:
            text=font.render(item[0], 1,(0,0,0))
            gameDisplay.blit(text, (item[1], item[2]))

        #Update the screen, and control framerate
        screen.blit(gameDisplay,(0,0))

        pygame.display.update()

        clock.tick(60)

      #Weapon menu state
      if state == "weapons":
          #Clear screen, set text to be display
          textSprites = []
          gameDisplay.fill((255,255,255))
          textSprites.append(["WEAPONS",30,50])
          newLocation = 0

          yoffset = 0
          #For each weapon, display at correct height, display damage, speed, as well as which weapon is selected and which is equipped
          for i in range(len(player.weapons)):
              yoffset += 1
              if selection == i+1:
                  weaponName = "> "+ player.weapons[i][4]
                  newLocation = i
              else:
                  weaponName = player.weapons[i][4]
                  
              textSprites.append([weaponName,30,80+yoffset*40])
              gameDisplay.blit(smallfont.render("DMG:" + str(player.weapons[i][1]),1,(0,0,0)),(550,80+yoffset*40))
              gameDisplay.blit(smallfont.render("SPD:" + str(22-player.weapons[i][2]),1,(0,0,0)),(670,80+yoffset*40))
              if player.weapons[i] == player.sword:
                  gameDisplay.blit(smallfont.render("Equipped",1,(0,0,0)),(390,80+yoffset*40))

          #Handle events
          events = pygame.event.get()
          for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                    state = "inventory"
                    selection = 1
                    loadSound("menuback.wav").play()
                elif event.key == pygame.K_RETURN:
                    loadSound("menuselect.wav").play()
                    player.sword = player.weapons[newLocation]
                elif event.key == pygame.K_UP:
                    selection -= 1
                    loadSound("menumove.wav").play()
                    if selection < 1:
                        selection = len(player.weapons)
                        
                elif event.key == pygame.K_DOWN:
                    selection += 1
                    loadSound("menumove.wav").play()
                    if selection >len(player.weapons):
                        selection = 1

          #Draw UI, as well as text
          drawUI()
          for item in textSprites:
            text=font.render(item[0], 1,(0,0,0))
            gameDisplay.blit(text, (item[1], item[2]))

          #Update the screen, and control framerate
          screen.blit(gameDisplay,(0,0))

          pygame.display.update()

          clock.tick(60)

      #Main game state
      if state == "game":
        #Clear screen
        gameDisplay.fill((255,255,255))
        screen.fill((255,255,255))

        #Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    loadSound("menuselect.wav").play()
                    state = "pause"
                    selection = 1
                    
                #Allow the player to attack, use a bomb, use an item, or go to their inventory
                elif event.key == pygame.K_SPACE:
                    player.attack(player.facing)
                elif event.key == pygame.K_b:
                    player.bomb()
                elif event.key == pygame.K_e:
                    player.useItem()
                elif event.key == pygame.K_i:
                    state = "inventory"
                    selection = 1

        #See which keys are held down - use these to move the player around
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            player.move(1,4)
        elif keys[pygame.K_a]:
            player.move(3,4)
        elif keys[pygame.K_s]:
            player.move(0,4)
        elif keys[pygame.K_w]:
            player.move(2,4)

        #Now draw all the sprite groups in the correct order, so that the correct sprites are on top
            #Also update all objects of certain classes here
        backgroundBlockSprites.draw(gameDisplay)

        backgroundSprites.draw(gameDisplay)

        wallSprites.draw(gameDisplay)

        itemSprites.update()
        itemSprites.draw(gameDisplay)

        enemySprites.update()
        enemySprites.draw(gameDisplay)

        playerSprites.update()
        playerSprites.draw(gameDisplay)

        bulletSprites.update()
        bulletSprites.draw(gameDisplay)

        playerBonusSprites.update()
        playerBonusSprites.draw(gameDisplay)

        effectSprites.update()
        effectSprites.draw(gameDisplay)

        #Check here to see the player's health
        if player.hp <= 0:
            state = "gameover"
            offset = [0,0,0]
        #Handle screenshake
        elif offset[2] > 0:
            screenShake()

        #Draw text, then the UI
        for item in textSprites:
            text=font.render(item[0], 1,(0,0,0))
            gameDisplay.blit(text, (item[1], item[2]))
        textSprites = []
        
        screen.blit(gameDisplay,(offset[0],offset[1]))

        drawUI()

        #Update the screen, control framerate

        pygame.display.update()

        clock.tick(60)

      #Gameover state
      if state == "gameover":

        #Only event that needs to be checked is the window being closed
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        #Count up, and fade the screen to red
        selection += 1
        gameDisplay.blit(loadImage("red.png"),(0,0))
        if selection > 180:
            state = "mainmenu"
            selection = 1

        #After a delay, draw text to screen
        elif selection > 50:
            gameDisplay.blit(font.render("Game Over.",1,(255,255,255)),(300,200))

        #Update screen, control framerate
        screen.blit(gameDisplay,(0,0))

        pygame.display.update()

        clock.tick(60)

      #Victory state
      if state == "victory":

        #Check for window being closed, or the player returning to the main menu
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and selection >= 180:
                    state = "mainmenu"
                    selection = 0

        #Fade to black
        selection += 1
        gameDisplay.blit(loadImage("black.png"),(0,0))
        screen.blit(loadImage("black.png"),(0,200))
        
        #Draw text to screen
        if selection > 50:
            gameDisplay.blit(font.render("Victory!",1,(255,255,255)),(50,50))
            gameDisplay.blit(smallfont.render("You saved the princess and won the game!",1,(255,255,255)),(50,100))
            gameDisplay.blit(smallfont.render("Peace returns to the land. Well done.",1,(255,255,255)),(50,140))
            gameDisplay.blit(smallfont.render("Thank you for playing, "+str(player.name)+".",1,(255,255,255)),(50,180))

        #Add option for the player to return to the main menu
        if selection >= 180:
            gameDisplay.blit(font.render("> Main Menu",1,(255,255,255)),(20,350))
        
        #Update screen, control framerate
        screen.blit(gameDisplay,(0,0))

        pygame.display.update()

        clock.tick(60)

#Initialise all of the sprite groups that will be used, as well as textSprites list
backgroundSprites = pygame.sprite.Group()
backgroundBlockSprites = pygame.sprite.Group()
wallSprites = pygame.sprite.Group()
invisWallSprites = pygame.sprite.Group()
bulletSprites = pygame.sprite.Group()
enemySprites = pygame.sprite.Group()
summonedEnemySprites = pygame.sprite.Group()
itemSprites = pygame.sprite.Group()
effectSprites = pygame.sprite.Group()
playerSprites = pygame.sprite.Group()
playerBonusSprites = pygame.sprite.Group()
playerShotSprites = pygame.sprite.Group()

#Create a base player object
player = Player(200,200,10,10)
playerSprites.add(player)

#Stores background colour for each room
backgroundDatabase = {
    (-4,-1):(200,255,200),
    (-4,0):(247, 239, 133),
    (-4,1):(247, 239, 133),
    (-4,2):(247, 239, 133),
    (-3,-2):(200,255,200),
    (-3,-1):(200,255,200),
    (-3,0):(247, 239, 133),
    (-3,1):(247, 239, 133),
    (-3,2):(247, 239, 133),
    (-2,-3):(200,255,200),
    (-2,-2):(200,255,200),
    (-2,-1):(200,255,200),
    (-2,0):(247, 239, 133),
    (-2,1):(247, 239, 133),
    (-2,2):(247, 239, 133),
    (-1,-6):(201, 216, 239),
    (-1,-5):(201, 216, 239),
    (-1,-4):(201, 216, 239),
    (-1,-3):(200,255,200),
    (-1,-2):(200,255,200),
    (-1,-1):(200,255,200),
    (-1,0):(200,255,200),
    (-1,3):(152, 209, 173),
    (-1,4):(152, 209, 173),
    (-1,5):(152, 209, 173),
    (0,-6):(201, 216, 239),
    (0,-5):(201, 216, 239),
    (0,-4):(201, 216, 239),
    (0,-3):(201, 216, 239),
    (0,-2):(200,255,200),
    (0,-1):(200,255,200),
    (0,0):(200,255,200),
    (0,2):(152, 209, 173),
    (0,3):(152, 209, 173),
    (0,4):(152, 209, 173),
    (0,5):(152, 209, 173),
    (1,-5):(201, 216, 239),
    (1,-4):(201, 216, 239),
    (1,-3):(201, 216, 239),
    (1,-2):(200,255,200),
    (1,-1):(200,255,200),
    (1,0):(200,255,200),
    (1,1):(200,255,200),
    (1,2):(152, 209, 173),
    (1,3):(152, 209, 173),
    (1,4):(152, 209, 173),
    (1,5):(152, 209, 173),
    (2,-5):(201, 216, 239),
    (2,-4):(201, 216, 239),
    (2,-3):(201, 216, 239),
    (2,-2):(200,255,200),
    (2,-1):(200,255,200),
    (2,0):(200,255,200),
    (2,1):(200,255,200),
    (2,2):(152, 209, 173),
    (2,5):(152, 209, 173),
    (3,-4):(201, 216, 239),
    (3,-3):(201, 216, 239),
    (3,-2):(200,255,200),
    (3,-1):(200,255,200),
    (3,0):(200,255,200),
    (3,1):(200,255,200),
    (3,2):(200,255,200),
    (4,-1):(200,255,200),
    (4,0):(200,255,200),
    (4,1):(200,255,200),
    (5,0):(200,255,200),
    (5,1):(200,255,200),

    (200,250):(249, 193, 110),
    (201,250):(249, 193, 110),
    (202,250):(249, 193, 110),
    (203,250):(249, 193, 110),
    (204,250):(249, 193, 110),
    (205,250):(150, 191, 255),
    (206,250):(150, 191, 255),
    (207,250):(249, 193, 110),
    (208,250):(249, 193, 110),
    (209,250):(249, 193, 110),
    
    (239,250):(150, 191, 255),
    (240,250):(150, 191, 255),

    (250,250):(249, 193, 110),
    
    (299,301):(249, 193, 110),
    (299,300):(249, 193, 110),
    (300,300):(249, 193, 110),

    (208,202):(249, 193, 110),
    (209,202):(249, 193, 110),
    (210,202):(249, 193, 110),
    (210,201):(249, 193, 110),
    (210,200):(249, 193, 110),
    (211,200):(255, 213, 150),
    }

#Stores which enemies are in what room at what tile position (x,y)
enemyDatabase = {
    
    (-4,0):[[5,4,"BlueOrc"],[15,5,"BlueOrc"],[14,5,"BlueOrc"],[6,10,"Mummy"]],
    (-4,1):[[2,3,"Skeleton"],[4,3,"Skeleton"],[3,4,"Skeleton"],[9,6,"Mummy"],[9,5,"Mummy"]],
    (-4,2):[[4,5,"Mummy"],[8,7,"Mummy"],[7,5,"Skeleton"],[4,9,"Skeleton"],[9,5,"Bug"]],


    (-3,-2):[[12,9,"Bug"],[12,7,"Bug"],[5,4,"BlueOrc"],[9,4,"Bug"]],
    (-3,-1):[[2,2,"Bug"],[11,10,"Bug"]],
    (-3,0):[[0,5,"Skeleton"],[7,12,"Skeleton"]],
    (-3,1):[[7,0,"Mummy"],[9,2,"Mummy"],[0,11,"Mummy"],[9,10,"Skeleton"],[15,7,"Mummy"]],
    (-3,2):[[0,5,"Mummy"],[15,9,"Mummy"],[8,7,"Mummy"],[7,5,"Skeleton"],[4,9,"Skeleton"],[9,5,"Bug"]],

    (-2,-7):[[1,5,"Snowman"]],
    (-2,-6):[[1,0,"Skeleton"],[2,0,"Skeleton"],[15,5,"Skeleton"],[15,6,"Skeleton"]],
    (-2,-3):[[5,5,"BlueOrc"],[10,6,"BlueOrc"],[14,8,"Orc"],[1,8,"Orc"]],
    (-2,-2):[[5,7,"Bug"],[8,10,"BlueBug"]],
    (-2,-1):[[3,4,"Orc"],[7,9,"BlueOrc"]],
    (-2,0):[[5,10,"Skeleton"]],
    (-2,1):[[3,8,"Skeleton"],[5,6,"Skeleton"],[5,2,"Mummy"],[12,6,"Skeleton"]],
    (-2,2):[[9,9,"Skeleton"],[10,8,"Mummy"]],

    (-1,-6):[[2,3,"Snowman"],[6,3,"Snowman"],[9,4,"Snowman"],[9,8,"Snowman"],[15,6,"BlueOrc"],[11,12,"BlueOrc"]],
    (-1,-5):[[7,7,"Snowman"],[9,6,"Snowman"],[3,0,"Skeleton"],[12,0,"Skeleton"],[7,12,"Skeleton"]],
    (-1,-4):[[5,10,"Snowman"],[2,3,"Snowman"],[4,5,"Skeleton"],[7,1,"Mummy"],[8,1,"Skeleton"],[15,7,"Mummy"]],
    (-1,-3):[[4,6,"Bug"],[6,6,"Bug"],[5,10,"BlueBug"],[14,7,"BlueBug"],[9,2,"BlueOrc"]],
    (-1,-2):[[10,3,"Bug"],[6,8,"Bug"],[8,4,"Bug"]],
    (-1,-1):[[5,2,"Orc"],[6,9,"Orc"],[0,8,"Bug"],[14,8,"Orc"],[15,5,"BlueBug"]],
    (-1,0):[[3,4,"Bug"],[14,9,"Orc"],[14,8,"Orc"],[13,8,"BlueOrc"]],
    (-1,3):[[1,6,"Knight"],[15,6,"Knight"],[6,1,"BlueKnight"],[9,1,"BlueKnight"]],
    (-1,4):[[2,5,"BlueKnight"],[12,5,"Knight"],[8,12,"Knight"]],
    (-1,5):[[1,6,"Knight"],[1,7,"BlueKnight"],[8,11,"Bug"],[10,11,"Bug"]],
    
    (0,-6):[[3,10,"Orc"],[9,2,"Orc"],[12,3,"Orc"],[13,6,"Orc"]],
    (0,-5):[[3,12,"Skeleton"],[2,5,"Snowman"],[12,1,"Snowman"],[15,5,"Orc"]],
    (0,-4):[[4,12,"Orc"],[6,12,"Orc"],[2,7.5,"Snowman"],[3,0,"Skeleton"],[9,1,"Skeleton"],[15,7,"Orc"]],
    (0,-3):[[1,7,"Orc"],[5,0,"Orc"],[15,6,"Orc"],[12,9,"Snowman"],[7,7,"Snowman"]],
    (0,-1):[[9,4,"Orc"],[12,9,"BlueOrc"],[1,9,"Bug"],[1,5,"Bug"]],
    (0,0):[],
    (0,2):[[11,10,"Knight"],[13,10,"BlueKnight"],[15,2,"Knight"],[5,12,"Orc"],[3,6,"BlueKnight"],[7,7,"Knight"],[12,10,"Orc"]],
    (0,3):[[10,4,"Skeleton"],[9,2,"BlueKnight"],[7,6,"Knight"]],
    (0,4):[[5,6,"Knight"],[7,6,"BlueBug"],[8,4,"Skeleton"],[9,4,"Skeleton"]],
    (0,5):[[4,3,"Knight"],[4,10,"Knight"],[12,2,"Bug"],[14,2,"Bug"],[13,1,"BlueBug"]],
    

    (1,-5):[[11,5,"Orc"],[6,12,"Orc"],[0,5,"Orc"],[10,2,"Snowman"],[13,8,"Snowman"]],
    (1,-4):[[10,6,"Orc"],[1,7,"Skeleton"],[13,2,"Snowman"],[14,6,"Snowman"],[6,0,"Orc"]],
    (1,-3):[[1.5,9,"Snowman"],[8,3,"Snowman"],[10,3,"BlueOrc"],[9,11,"Orc"]],    
    (1,-2):[[3,5,"Orc"],[15,1,"BlueBug"],[15,2,"Bug"],[7,6,"BlueBug"],[3,10,"Bug"]],
    (1,-1):[[3,4,"Orc"],[10,5,"BlueBug"],[14,6,"BlueBug"],[6,7,"Bug"]],
    (1,0):[[10,4,"Bug"],[12,8,"Bug"],[1,5,"Bug"]],
    (1,1):[[7,9,"Bug"],[15,9,"Orc"],[15,8,"Orc"]],
    (1,2):[[0,2,"Knight"],[3,12,"Knight"],[15,4,"Knight"],[15,9,"Knight"],[12,11,"Bug"]],
    (1,3):[[5,11,"Knight"],[2,0,"Knight"],[9,0,"Knight"],[10,8,"Orc"],[13,2,"BlueBug"]],
    (1,4):[[13,6,"Skeleton"],[13,8,"Skeleton"],[10,3,"Skeleton"]],
    (1,5):[[7,5,"Skeleton"],[7,7,"Skeleton"],[13,6,"Knight"]],

    (2,-4):[[4,11,"Snowman"],[1,4,"Snowman"],[5,1,"Snowman"],[14,4,"Snowman"]],
    (2,-3):[[11,11,"BlueBug"],[0,5,"Skeleton"],[7,6,"Skeleton"]],
    (2,-2):[[0,1,"BlueBug"],[0,2,"Orc"],[10,7,"Orc"],[7,11,"Bug"]],
    (2,-1):[[5,7,"Bug"],[14,9,"Bug"]],
    (2,0):[[1,5,"Bug"],[7,1,"Bug"],[14,4,"Bug"],[10,5,"Bug"]],
    (2,1):[[13,8,"BlueBug"],[4,7,"Orc"],[8,7,"Orc"],[14,9,"Bug"],[5,10,"Bug"]],
    (2,2):[[7,3,"Bug"],[13,6,"Knight"],[6,11,"Knight"]],

    (3,-4):[[1,3,"Snowman"],[12,1,"Snowman"],[8,12,"Skeleton"],[4,6,"Skeleton"],[11,5,"Skeleton"],[0,8,"BlueOrc"],[0,9,"Orc"],[4,4,"Orc"],[10,12,"Orc"]],
    (3,-3):[[3,4,"Snowman"],[7,1,"Snowman"],[13,1,"Snowman"],[11,4,"Orc"],[11,11,"Skeleton"]],
    (3,-2):[[12,11,"BlueBug"],[10,11,"Bug"],[1,9,"BlueBug"],[1,8,"Bug"],[10,4,"Bug"],[7,4,"Orc"],[4,4,"Bug"]],
    (3,-1):[[10,0,"BlueBug"],[12,0,"Bug"],[14,0,"BlueBug"],[12,6,"Orc"],[0,7,"Bug"],[0,8,"BlueBug"],[4,11,"Bug"]],
    (3,0):[[3,8,"BlueBug"],[10,10,"Bug"],[11,3,"Bug"]],
    (3,1):[[0,7,"BlueBug"],[5,4,"Bug"],[5,12,"BlueOrc"],[15,5,"Orc"]],

    (4,0):[[7,8,"Bug"],[15,5,"BlueOrc"]],
    (4,1):[[0,6,"BlueOrc"],[0,7,"Orc"],[2,6,"Bug"],[2,7,"Bug"],[15,6,"BlueOrc"],[15,7,"Orc"],[13,6,"Bug"],[13,7,"Bug"]],

    (5,0):[[4,7,"BlueBug"],[8,6,"BlueBug"],[6,4,"Bug"],[9,11,"Bug"]],
    (5,1):[[0,6,"Bug"],[9,0,"BlueBug"],[10,0,"Bug"],[7,4,"BlueBug"],[6,9,"Orc"],[5,8,"BlueOrc"],[4,9,"Orc"]],

    (204,250):[[4,2,"Orc"],[8,1,"Orc"],[13,1,"Orc"],[5,10,"BlueOrc"],[10,11,"BlueOrc"],[13,10,"Bug"],[3,11,"Bug"],[4,1,"Bug"]],

    (209,202):[[7,4,"Mummy"],[0,7,"Mummy"],[12,10,"Mummy"]],
    (208,202):[[2,5,"Mummy"],[3,5,"Mummy"],[1,5,"Skeleton"],[4,5,"Skeleton"]],
    (210,202):[[1,9.5,"Skeleton"],[7.5,1,"Skeleton"],[12,9,"Skeleton"],[6,5,"Mummy"],[9,5,"Mummy"]],
    (210,201):[[3,4,"Mummy"],[12,8,"Mummy"],[3,8,"Skeleton"],[12,4,"Skeleton"]],
    (210,200):[[11.5,5.5,"Dragon"]],
    }

#The itemDatabase is a copy of the template database - allows changes to be made that aren't permanent between playthroughs
itemDatabase = {}

#Stores what items are in what rooms, as well as the unique information that each item requires 
itemTemplateDatabase = {
    (-4,-1):[["Gold",[3.5*48,10*48,"gold2.png",5]],["Gold",[5.5*48,10*48,"gold2.png",5]],["Pickup",[4,9.5,"potionsquare.png","Potion"]]],
    (-4,0):[["TeleDoor",[1,4,"blackdoor.png",15,6,204,250]]],
    (-4,1):[["TeleDoor",[3,2,"blackdoor.png",4.5,11,209,202]]],
    (-4,2):[["TeleDoor",[4,7,"rstairs.png",7.5,10.5,209,250]]],

    (-3,-2):[["Gold",[4.5*48,4*48,"gold3.png",15]]],

    (-2,0):[["Door",[7,6,"door.png"]]],
    
    (-1,-6):[["TeleDoor",[4,1,"blackdoor.png",7.5,11,206,250]]],
    (-1,-2):[["TeleDoor",[12,1,"blackdoor.png",12,11,300,300]],["Door",[15,6,"door.png"]]],
    (-1,0):[["TeleDoor",[3,1,"blackdoor.png",7.5,11,250,250]]],
    (-1,5):[["TeleDoor",[3,3,"blackdoor.png",7.5,9.5,208,250]]],
    
    (0,-5):[["TeleDoor",[10,7,"blackdoor.png",7.5,12,240,250]]],
    (0,-2):[["Gold",[10*48,7*48,"gold3.png",15]],["Gold",[6*48,7*48,"gold3.png",15]],["Pickup",[7.9,7,"dagger1.png",[["playerbdaggerleft.png","dagger1.png"],8,4,"dagger","Rogue's Dagger",40]]]],
    (0,0):[["TeleDoor",[13,2,"blackdoor.png",7.5,12,200,250]]],
    (0,2):[["Door",[5,11,"door.png"]]],

    (1,-2):[["TeleDoor",[3,1,"blackdoor.png",7.5,11,203,250]]],
    (1,1):[["TeleDoor",[7,6,"blackdoor.png",7.5,11,201,250]]],

    (2,-5):[["TeleDoor",[8,6,"blackdoor.png",7.5,11,205,250]]],
    (2,5):[["Gold",[8*48,7*48,"gold4.png",50]],["Key",[7.5,5]]],

    (3,2):[["TeleDoor",[2,4,"blackdoor.png",7.5,11,202,250]]],
    
    (4,0):[["TeleDoor",[7,6,"blackfull.png",7.5,11,207,250]]],


    (200,250):[["Pickup",[7.5,6,"potionsquare.png","Potion"],True],["Gold",[10*48,7*48,"gold2.png",5]],["Gold",[6*48,7*48,"gold2.png",5]],["TeleDoor",[7.5,13,"blackdoor.png",13,3,0,0]]],
    (201,250):[["Gold",[10*48,7*48,"gold1.png",1]],["Gold",[6*48,7*48,"gold1.png",1]],["Key",[7.5,6]],["TeleDoor",[7.5,13,"blackdoor.png",7,7,1,1]]],
    (202,250):[["Gold",[10*48,7*48,"gold2.png",5]],["Gold",[6*48,7*48,"gold2.png",5]],["TeleDoor",[7.5,13,"blackdoor.png",2,5,3,2]],["ShopItem",[8*48,5*48,"sword2.png",15,["Pickup",[8,5,"sword2.png",[["playerwswordleft.png","sword2.png"],8,12,"sword","Blue Sword",10]]],True]] ],
    (203,250):[["TeleDoor",[7.5,13,"blackdoor.png",3,2,1,-2]]],
    (204,250):[["TeleDoor",[16,6,"blackdoor.png",2,4,-4,0]],["Pickup",[11,1.5,"tomeyellowsquare.png","Tome: Lightning"],True],["Pickup",[11,10.5,"tomeyellowsquare.png","Tome: Lightning"],True],["Pickup",[3,6,"tomeredsquare.png","Tome: Fire"],True]],
    (205,250):[["ShopItem",[8*48,5*48,"sword4.png",125,["Pickup",[8,5,"sword4.png",[["playergswordleft.png","sword4.png"],12,20,"greatsword","Greatsword",30]]],True]], ["Gold",[10*48,7*48,"gold1.png",1]],["Gold",[6*48,7*48,"gold1.png",1]],["TeleDoor",[7.5,13,"blackdoor.png",7,7,2,-5]]],
    
    (206,250):[["ShopItem",[9,7,"bombsquare.png",15,["BombPickup",[9.5*48,7.5*48]],False,True]],["ShopItem",[6,7,"heartsquare.png",15,["Heart",[6.5*48,7.5*48]],False,True]],["ShopItem",[8,7,"dagger3.png",60,["Pickup",[8,8,"dagger3.png","dagger3"]],True,False],["TeleDoor",[7.5,13,"blackdoor.png",4,2,-1,-6]]]],
    (207,250):[["Gold",[10*48,7*48,"gold2.png",5]],["Gold",[6*48,7*48,"gold2.png",5]],["ShopItem",[7.5,6,"potionsquare.png",10,["Pickup",[7.5,6,"potionsquare.png","Potion"],True]]],["TeleDoor",[7.5,13,"blackdoor.png",7,7,4,0]]],

    (208,250):[["ShopItem",[9,7,"bombsquare.png",15,["BombPickup",[9.5*48,7.5*48]],False,True]],["ShopItem",[6,7,"heartsquare.png",15,["Heart",[6.5*48,7.5*48]],False,True]],["ShopItem",[8*48,5*48,"sword3.png",100,["Pickup",[8,5,"sword3.png",[["playerrswordleft.png","sword3.png"],10,10,"sword","Regal Sword",20]]],True]],["TeleDoor",[7.5,13,"blackdoor.png",3,4,-1,5]]],
    (209,250):[["TeleDoor",[7.5,13,"blackdoor.png",4,8,-4,2]], ["ShopItem",[8*48,5*48,"dagger2.png",125,["Pickup",[8,5,"dagger2.png",[["playerrdaggerleft.png","dagger2.png"],15,7,"dagger","Assassin's Dagger",150]]],True]]],

    (239,250):[["ShopItem",[4,8,"candle.png",50,["Pickup",[4,8,"candlesquare.png","Candle",False]],False]],["ShopItem",[6,8,"heartsquare.png",10,["Heart",[6*48,8*48]],False,True]],["ShopItem",[10,8,"keysquare.png",25,["Key",[10,8]],False]],["ShopItem",[8,8,"bombsquare.png",15,["BombPickup",[8*48,8*48]],False,True]],],
    (240,250):[["TeleDoor",[7.5,13,"blackdoor.png",10,8,0,-5]]],

    (250,250):[["Pickup",[7.5,6,"tomeyellowsquare.png","Tome: Lightning",True]],["TeleDoor",[7.5,13,"blackdoor.png",3,2,-1,0]]],

    
    (299,300):[["Key",[2.5,3]]],
    (300,300):[["TeleDoor",[12,13,"blackdoor.png",12,2,-1,-2]]],

    (208,202):[["Key",[7,2]]],
    (209,202):[["TeleDoor",[4.5,13,"blackdoor.png",3,3,-4,-1]],["Door",[13,10,"door.png"]]],
    (210,201):[["TeleDoor",[7.5,1,"rstairs.png",3.5,11,210,200]]],
    (211,200):[["Princess",[7.5,3]]],
    }

#Stores the tiles in each rooms - system uses two characters to one tile, so rooms dimensions are 16x13
objectDatabase = {
    (-4,-1):['WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWR',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWR',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWR',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWR',
            'WWWWWWWWWWWWWWWWWWWWWWWWWDWDWDW1',
            'WWWWWWWWWWWWWWWWWWWWWWW5......FT',
            'WWWWWWWWWWWWWWWWWWWWWR..........',
            'WWWWWWWWPPWWWWWWWWWWWR........FT',
            'WDWDWDWDPPWDWDWDWDWDW1........FT',
            'F3............................FT',
            'FGF6F3......................FTFB',
            'FGFGFGF3..F4F3..............FTFT',
            'FGFGFGFGF6FGFGF6F3F4F6F3FTFBFTFT',],
    
    (-4,0):['RGRGRGRGRGRGRGRGRGRGRGRGRGR2RGRG',
            'RGRGRGRGRGRGRGRGRGRGRGRGR1..R2RG',
            'RGRGR1FB..FT..FBR2RGRGR1......RG',
            'RGRG..............RGRG........R2',
            'RG................RGRG..........',
            'RGRG..............RGRG..........',
            'RGRGR3..........R4RGR1..........',
            'RGRGRGR6R6LLR6R6RGRG............',
            'RGRGRGRGRGLLRGRGRGRG..........R4',
            'RGRGR1..R2LLRGRGRGR1..........RG',
            'RG..........................R4RG',
            'RGR3......................R4RGRG',
            'RGRGR3R4R6R6R6R6R6R6R6R6R6RGRGRG',],
    
    (-4,1):['RGRGRGRGRGRGRGRGRGRGRGRGRGRGRGRG',
            'RGRGRGRGRGRGR1..............R2RG',
            'RGR2RG..RGR1..................RG',
            'RGRT......RT..........R3......RG',
            'RGRT......RT..........RG......R2',
            'RGRT......RT........R4RG......R4',
            'RGRT......RT........RGRGR3....RG',
            'RG........RT........RGRGRG....RG',
            'RG....R4R6R3........RGRGRG....R2',
            'RG....R2RGRGR6R6R3..RGRGRG......',
            'RG........R2RGRGR1..R2RGR1......',
            'RGR6R3..........................',
            'RGRGRGR6R6R6R6R6R6R6R6RGR6R6R6R6',],

    (-4,2):['RGRGRGRGRGRGRGRGRGRGRGRGRGRGRGRG',
            'RGRGRGRGRGRGRGRGRGRGRGR1R2RGRGRG',
            'RGRGRGRGRGRGR1R2RGR1........R2RG',
            'RGRGRGR1......................R2',
            'RGRG............................',
            'RGR1............................',
            'RG..............................',
            'RG..RT......RT..................',
            'RG......................R4R6R6R6',
            'RG..............R4R3R4R6RGRGRGRG',
            'RGR3........R4R6RGRGRGRGRGRGRGRG',
            'RGRGR6R6R6R6RGRGRGRGRGRGRGRGRGRG',
            'RGRGRGRGRGRGRGRGRGRGRGRGRGRGRGRG',],

    (-3,-2):['WWWWWRF2FGFGFGFGFGFGFGFGFGFGFGFG',
            'WWWWWR....F2FGFGFGFGFGFGFGFGFGFG',
            'WWWWWR..................F2FGFGFG',
            'WWPPPP....................F2FGFG',
            'WWWWWR......................FGFG',
            'WWWWWWW7....................F2FG',
            'WWWWWWWWWUPPWUW3..............FG',
            'WWWWWWWWWWPPWWWR..............FG',
            'WWWDWDWDWDPPWDW1..............FG',
            'W5............................FG',
            'FT............................FG',
            'FT....................F4F6F6F6FG',
            'FTFT......FTFTF4F6F6F6FGFGFGFGFG',],

    (-3,-1):['FTFB......FTFTF2FGFGFGFGFGFGFGFG',
            'FTFT......FTFT..........F2FGFGFG',
            'FB........FTFB................F2',
            'FB..........FT....FT....FB......',
            'FT................FT..........F4',
            'FT................FT..........FG',
            '............FTFTFTFTFTFTFTFTFTFG',
            'FT............................F2',
            'FT..............................',
            'FT....FB....FTFTFTFT....FB......',
            'F3..........FTFBFTFT..........F4',
            'FGF3........FTFTFTFB..........FG',
            'FGFGF6F6F6F6F6F6F6F6F6F6F6F6F6FG',],

    (-3,0):['RGRGRGRGRGRGRGRGRGRGRGRGRGRGRGRG',
            'RGRGRGRGRGRGR1..........R2RGRGRG',
            'RGRGRGRGR1..................R2RG',
            'R2RGR1........................RG',
            '..............RTRTFT..........RG',
            '..........RTFTFTFTFTFT........RG',
            '........RTRTFTFT..FTRTFT......RG',
            '......FTFTFT......FTFT........RG',
            'R6R3RTRTRT....................RG',
            'RGRGR3RT....................R4RG',
            'RGRGRG....................R4RGRG',
            'RGRGRGR6R3............R4R6RGRGRG',
            'RGRGRGRGRGR3........R4RGRGRGRGRG',],

   (-3,1):[ 'RGRGRGRGRGR1........R2RGRGRGRGRG',
            'RGRGR1................R2RGRGRGRG',
            'RGRGFT......................R2RG',
            'RGRG..........................RG',
            'RGRG..........................R2',
            'RGR1........R4R6R4R3............',
            'RGR3........RGRGRGRG............',
            'RGRGR3......R2RGRGR1............',
            'R1R2R1........W6W5............R4',
            '..............................RG',
            '............................R4RG',
            '..........R4R6R3..........FBRGRG',
            'R6R6R3R4R6RGRGRGR6R3R4R6R6R6RGRG',],

    (-3,2):['RGRGRGRGRGRGRGRGR1R2RGRGRGRGRGRG',
            'RGRGRGRGR1......FTFT..R2RGRGRGRG',
            'RGR1......................RGRGRG',
            'R1........................RGRGRG',
            '..........................R2RGRG',
            '........FT..................RGRG',
            '........RT..................R2RG',
            '..............................R2',
            'R6R3....................RT......',
            'RGRGR3..................FT......',
            'RGRGRG........................R4',
            'RGRGRGR3........FTFT........R4RG',
            'RGRGRGRGR6R6R6R6R6R6R6R6R6R6RGRG',],

    (-2,-3):['FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGF1..........F2FGFGFGFGFGFGFG',
            'FGF1......................F2FGFG',
            'FG............................F2',
            'FG..............................',
            'FG..............................',
            'FGFT............................',
            'FGFTFT........................F4',
            'FGFTFTFT............F4F6F6F6F6FG',
            'FGF6F6F6F6F3....F4F6FGFGFGFGFGFG',],

    (-2,-2):['FGFGF2FGFGF1....F2FGFGFGFGFGFGFG',
            'FGFG..F2F1............F2FGFGFGFG',
            'FGF1........................F2FG',
            'FG..RT..RT..RT................F2',
            'FG....................RT........',
            'F1..RT......RT..................',
            'F3....................RT........',
            'FG............................F4',
            'FG..........F4F3..............FG',
            'FG....RT....FGFG....F4F3......FG',
            'FGF3........FGFG....FGFGF3....F2',
            'FGFG......F4FGFG....FGFGFG....F4',
            'FGFGF3F4F6FGFGFG....FGFGFG....FG',],

    (-2,-1):['FGFGF1F2FGF1F2F1....F2FGFG....FG',
            'FG....................FBFT....FG',
            'F1..RT..RT..RT........FTFT....F2',
            '..............................F4',
            'F3..RT..RT..RT........FTFT....FG',
            'FG....................FTFT....F2',
            'FGFTFTFTFTFBFTFTFTFTFTFTFT......',
            'F1FTFTFTFTFTFTFTFTFBFTFTFT......',
            '......................FTFT......',
            '......................FTFBFT..F4',
            'F6F6F3F4F6F6F3..........FTFT..FG',
            'FGFGFGFGFGFGFGF3........FTFTF4FG',
            'FGFGFGFGFGFGFGFGF3....F4F6F6FGFG',],

    (-2,0):['RGRGRGRGRGR1R2RGR1....R2RGRGRGRG',
            'RGR1........................FTR2',
            'RG............................R4',
            'RG......FT....................RG',
            'RGR3......................RTR4RG',
            'RGRGR6R3................R4R6RGRG',
            'RGRGRGRGR6R6FB..FBR6R4R6RGRGRGRG',
            'RGRGRGRGRGR1......R2RGR1R2RGRGRG',
            'RGRGRGR1................FT..R2RG',
            'RGRGFT........................R2',
            'RGRGR3........................RT',
            'RGRGRG....R4R3................RT',
            'RGRGRGR6R6RGRGR3RTRTRT......R4R6',],

     (-2,1):['RGRGRGRGRGR1R2RGRGRGRG......RGRG',
            'RGRGR1..........R2RGR1......R2RG',
            'RGFT..........................RG',
            'RGR6..........................RG',
            'RGRGR3............R4R6R3......RG',
            '..R2RGR6R3....R4R6RGRGRG......RG',
            '....R2RGR1....R2RGRGRGR1......RG',
            '..................R2R1........RG',
            'R3............................R2',
            'RG............................R4',
            'RGR3..........................RG',
            'RGRG........................R4RG',
            'RGRGR6R6R3R4R3......R4R6R6R6RGRG',],

    (-2,2):['RGRGRGRGRGRGR1......R2RGRGRGRGRG',
            'RGRGRGR1FT................R2RGRG',
            'RGRGR1......................R2RG',
            'RGRGWUW3......................R2',
            'RGRGWWWR......................R4',
            'RGRGWDW1............R4R3....RTR2',
            'RGR1................R2R1......RT',
            'R1............W4WUW3........RTR4',
            '..............WLWWW1..........R2',
            '..............W2W1..........FTR4',
            'R6R6R3..................FTR4R6RG',
            'RGRGRGR3FT..............R4RGRGRG',
            'RGRGRGRGR6R6R3R4R6R6R4R6RGRGRGRG',],

    (-1,-6):['SGSGSGSGSGSGSGSGSGSGSGS1S2SGSGSG',
            'SGSGSGSG..SGSGSGSGSGS1ST..S2SGSG',
            'SGSGS1......S2SGSGSGST......S2SG',
            'SGSG..........SGSGS1..........S2',
            'SGS1..........SGSG..............',
            'SG............SGSG..............',
            'SG............SGSG..............',
            'S3ST..........SGSG..............',
            'SGS3..........SGSG..............',
            'SGSG..........SGSGS3..........S4',
            'SGSG........STSGSGSG..........SG',
            'SGSG........STSGSGSG..........SG',
            'SGSGS3....S4SGSGSGSGS3....S4SGSG',],

    (-1,-5):['SGSGS1....SGSGSGSGSGSG....S2SGSG',
            'SGST......S2SGSGSGSGS1........SG',
            'SGST........SGSGSGSG..........SG',
            'SG..........SGSGSGSG..........SG',
            'SG..........S2SGSGS1..........SG',
            'SG............STST..........S4SG',
            'SG............STSB..........SGSG',
            'SG..............STST........SGSG',
            'SGST............STSB........SGSG',
            'SGS3ST......................SGSG',
            'SGSGS3ST..................S4SGSG',
            'SGSGSGS6S6S3........S4S6S6SGSGSG',
            'SGSGSGSGSGSG........SGSGSGSGSGSG',],

    (-1,-4): ['SGSGSGSGSGSG........SGSGSGSGSGSG',
            'SGSGSGSGSGS1........S2SGSGSGSGSG',
            'SGS1......................FTS2SG',
            'SBST........................STSG',
            'STSTST........................SG',
            'STSBST........................S2',
            'STFTFT..........................',
            'SBFT............................',
            'SGS3............................',
            'SGSGS6S3......................S4',
            'SGSGSGSGS3..................STSG',
            'SGSGSGSGSGS6S3............STS4SG',
            'SGSGSGSGSGSGSGS6S3....S4S6S6SGSG',],

    (-1,-3):['FGFGFGFGFGFGFGSGSGLLLLSGSGFGFGFG',
            'FGFGFGFGFGFGFGFGSGLLLLSGFGFGFGFG',
            'FGFGFGFGFGFGFGFGFG....FGFGFGFGFG',
            'FGFGFGFGFGFGFGFGF1....F2FGFGFGFG',
            'FGF1......................F2FGFG',
            'FG....FT..FT..FT..............FG',
            'F1............................FG',
            '........................FT....FG',
            '..............................FG',
            '......FT..FT..FT............F4FG',
            'F3......................F4F6FGFG',
            'FGF6F6F6F6F6F6F6F6F6F6F6FGFGFGFG',
            'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',],

    (-1,-2):['FGFGFGFGFGFGFGF1F2FGFGFGFGFGFGFG',
            'FGFGFGFGFGF1FT....F2FGFG..FGFGFG',
            'FGF1..................FT..FTF2FG',
            'F1............................FG',
            '......T4T3....................F2',
            '......T2T1....................FT',
            '................................',
            'F3............................FT',
            'FG..T4T3........FTFT..........F4',
            'FG..T2T1......................FG',
            'FG..........................F4FG',
            'FGF3......................F4FGFG',
            'FGFGF6F6F6F6F3........F4F6FGFGFG',],

    (-1,-1):[ 'FGFGFGFGFGFGF1........F2FGFGFGFG',
            'FGFGF1F2F1............FTFGFGFGFG',
            'FGF1FT..................F2F1F2FG',
            'FGF3............................',
            'FGF1........F4F3................',
            'F1..........F2F1................',
            '................................',
            '....................F4F3........',
            '........F4F3........F2F1........',
            'F3......F2F1....................',
            'FGF3........................F4F6',
            'FGFGF3..............F4F6F3F4FGFG',
            'FGFGFGFTFTFTFT......FGFGFGFGFGFG',],

    (-1,0):[ 'FGFGFGFGFGFGF1......F2FGFGFGFGFG',
            'FGFGFG..FGF1............F2FGFGFG',
            'FGFGFT..FT................F2FGFG',
            'FGF1........................F2FG',
            'FG............................F2',
            'FG............W4WUW3..........F4',
            'F1....RT......WLWWWR..........FG',
            'F3............WLWWWR....FB....F2',
            'FG............PPPPPP............',
            'FG....FB......WLWWWR....FT......',
            'FG............WLWWWR..........F4',
            'FGF3..........WLWWWR..........FG',
            'FGFGF6F3F4F6F3WLWWWRF4F6F6F6F6FG',],

    (-1,3):['FTFTFTFTFTFTF2FGFGF1FTFTFTFTFTFB',
            'FTFTFTFB......F2F1....FTFBFTFTFT',
            'FTFTFTFT..................FBFTFT',
            'FTFT..........................FT',
            'FBFT..........................FT',
            'FT..............................',
            'FT..............................',
            'FT..............................',
            'FTFT........................FTFT',
            'FTFT..........FT..........FBFTFT',
            'FTFBFTFB......FTFB........FBFBFT',
            'FTFTFBFTFT....FTFT......FTFTFTFT',
            'FTFTFTFTFT....FTFT....FTFTFTFTFT',],

    (-1,4):['FTFTFTFBFT....FTFT....FTFBFTFTFT',
            'FBFTFT........FBFT......FTFTFTFB',
            'FTFT..........FTFT............FT',
            'FTFT........FTFTFT..............',
            'FTFB........FTFTFT..............',
            'FT..........FBFTFTFTFBFT..FTFTFT',
            'FB..FT..........FTFTFTFTFTFTFTFT',
            'FT....................FTFTFTFTFB',
            'FT....F4F3......................',
            'FB....F2F1......................',
            'F6F3........FT................F4',
            'FGFGF3....................F4F6FG',
            'FGFGFGF6F6F3F4F3..F4F6F6F6FGFGFG',],

    (-1,5):['FGFGFGFGFGFGFGF1..F2FGFGFGFGFGFG',
            'FGFGFGFGFGFGFG......FGFGFGFGFGFG',
            'FGFGFGFGFGFGFG......F2FGFGFGFGFG',
            'FGFGFG..FGFGF1..........F2FGFGFG',
            'FGF1......FTFT..................',
            'FG..............................',
            'FG..FB..........................',
            'FG..FB............FTFT........F4',
            'FG..............W4WUW3........FG',
            'FGF3..........FTW2WDW1......FTFG',
            'FGFGF3FT....................F4FG',
            'FGFGFGF3FTFT..............F4FGFG',
            'FGFGFGFGFTFTFBFTFTFTFBFTFTFGFGFG',],

    (0,-6):['SGSGSGSGSGSGSGS1S2SGSGSGSGSGSGSG',
            'SGSGSGSGSGS1STSBSTS2SGSGSGSGSGSG',
            'SGSGS1........STST....S2SGSGSGSG',
            'S1........................S2SGSG',
            '........................STSTSBS2',
            '......................STSBSTSTS4',
            '......................STST..S4SG',
            '............................SGSG',
            '............................SGSG',
            'S3ST......................S4SGSG',
            'SGS3ST....................SGSGSG',
            'SGSGS6S3ST..............S4SGSGSG',
            'SGSGSGSGS6S6S3......S4S6SGSGSGSG',],

    (0,-5):['SGSGSGSGSGSGS1......S2S1S2SGSGSG',
            'SGSGSGSGS1ST..............S2SGSG',
            'SGSGSGS1....................SGSG',
            'SGSGSG......................S2SG',
            'SGSGS1..........................',
            'SGS1..............S4S6S3........',
            'SGS3............S4SGSGSGS3......',
            'SGSG..........S4SGSG..SGSGS3S4S6',
            'SGS1..........SGSGS1..S2SGSGSGSG',
            'SGST........S4SGS1......S2S1STS2',
            'SG..........SGSGST............S4',
            'SGS3........SGSG............STSG',
            'SGSG......S4SGSGS3....S4S6S3S4SG',],

   (0,-4): ['SGSG......S2SGSGS1....S2SGSGSGSG',
            'SGSG......STSGSG........S2SGSGSG',
            'SGSG......S4SGSG..........S2SGSG',
            'SGSG......SGSGS1..........STS2SG',
            'SGS1......SGSGST............S4SG',
            'S1........SGSGS3............S2SG',
            '....SB....S2SGSG................',
            '............SGSGS3..............',
            '............S2SGSG..............',
            'S3..SB........SGSGS3............',
            'SG............S2SGSGS3ST......S4',
            'SGS3..........STS2SGSGS6S6S3S4SG',
            'SGSGS6S3........S4SGSGSGSGSGSGSG',],

    (0,-3):['SGSGSGS1........S2SGSGSGSGSGSGSG',
            'SGSGS1................S2SGSGSGSG',
            'SGSG......................STS2SG',
            'SGSG................S4S3......SG',
            'SGS1......S4S6S3....S2S1......S2',
            'SGST......SGSGSGS3..............',
            'SG........S2SGSGS1..............',
            'SG............................S4',
            'SG......................SB....SG',
            'SGS3..........................SG',
            'SGSG..........S4S6S6S3......S4SG',
            'SGSGS3ST..S4S6SGSGSGSGS3....SGSG',
            'SGSGSGS6S6SGSGSGSGSGSGSGS6S6SGSG',],

    (0,-2):['FGFGFGFGF1F2FGFGFGFGFGFGFGFGFGFG',
            'FGF1................F2FGFGF1F2FG',
            'FG............................FG',
            'FG............................F2',
            'F1............................F4',
            'FT............................FG',
            '..............................FG',
            'FT............................FG',
            'F6F3........................F4FG',
            'FGFGW4WUWUWUWUPPPPWUWUWUWUW3FGFG',
            'FGFGWLWWWWWWWWPPPPWWWWWWWWWRFGFG',
            'FGF1WLWWWWWWWWWWWWWWWWWWWWWRFGFG',
            'FGF3WLWWWWWWWWWWWWWWWWWWWWWRF2FG',],

    (0,-1):['FGFGFGFGFGFGFGFGFGWLWWWWWWWRFGFG',
            'FGFGFGFGFGFGFGFGF1WLWWWWWWWRF2FG',
            'F1F2FGFGFGFGFGF1FTWLWWWWWWWRFTFG',
            '....F2FGFGFGF1....W2WDWDWDW1..FG',
            '......F2FGFGF3................F2',
            '......F4FGFGF1................FT',
            '......F2FGF1......F4F6F6......FT',
            '..................F2FGF1......FT',
            '..............................FT',
            '..............................F4',
            'F6F3........................F4FG',
            'FGFGF3......................FGFG',
            'FGFGFGF3F4F6F3........F4F6F6FGFG',],

    (0,0):[ 'FGFGFGFGFGFGF1........FGFGFGFGFG',
            'FGFGFGFGFGF1..........FGFGFGFGFG',
            'FGFGFGFGF1............F2FG..FGFG',
            'FGFGFGFG................FT..FTFG',
            'FGFGFGFG......................F2',
            'FGFGFGF1........................',
            'FGFGFG..........................',
            'FGFGF1..........................',
            '................................',
            '................................',
            'F6F3F4F6F3..............F4F3F4F6',
            'FGFGFGFGFGF6F3......F4F6FGFGFGFG',
            'FGFGFGFGFGFGFGFTFTFTFGFGFGFGFGFG',],

    (0,2):[ 'FTFTFBFBFTFTFTFTFTFTFTFTFTFTFTFT',
            'FTFTFTFTFTFT....................',
            'FTFTFT..........................',
            'FTFT......................FTFTFT',
            'FBFT..FB......FB....FTFTFTFTFTFT',
            'FTFT..............FTFTFT........',
            'FTFT..............FTFT..........',
            'FTFT..............FTFB........FB',
            'FBFT..............FTFT......FTFT',
            'FTFT..FB......FB..FTFT......FTFT',
            'FTFT..............FTFT......FBFT',
            'FTFTFTFTFB..FBFBFTFBFTFTFTFTFTFT',
            'FTFTFBFT......FTFTFBFTFTFTFTFTFT',],

    (0,3):[ 'FTFTFTFT......FTFTFBFTFTFTFTFTFT',
            'FTFTFTFB......FTFTFTFTFTFTFBFTFT',
            'FTFT....................FTFTFTFT',
            'FTFT..............FB........FTFT',
            'FT..........................FTFB',
            '..........FTFT........FB....FTFT',
            '........FTFBFT..............FTFT',
            '........FTFTFTFT............FBFT',
            'FT........FTFTFTFBFT..........FT',
            'FBFT............................',
            'FTFTFT..........................',
            'FTFBFTFT..................F4F6F6',
            'FTFTFTFTFTF4F6F6F6F6F6F6F6FGFGFG',],

    (0,4):[ 'FGFGFGFGFGFGFGFTFBFTFTFTFBFBFGFG',
            'FGFGFGFGFGFGF1..............F2FG',
            'F1............................F2',
            '................................',
            '..........FTFTFT....FTFT........',
            'FTFTFTFBFTFTFTFTFTFTFTFTFTFBFTFT',
            'FTFTFTFBFT......FTFTFBFTFTFTFTFT',
            'FT............................FT',
            '..........FB........FB..........',
            '................................',
            'F3........FB........FB........F4',
            'FGF6F3......................FTFG',
            'FGFGFGF6F6F3........F4F6F6F6F6FG',],

    (0,5):[ 'FGFGFGFGFGF1........F4FGFTFBFTFT',
            'FGFGF1..............FGFGFT..FTFT',
            'FGF1....FB..........F2F1......FB',
            'F1..................FT........F4',
            '........FB....................FG',
            '............F4F3FT............F2',
            '....F4F6F6F6FGFG................',
            'F6F6FGFGFGFGFGF1................',
            'FGFGFGFGFGF1..................F4',
            'FGFGF1........................FG',
            'FTFT..FB..FB................F4FG',
            'FTFB..............F4F3....F4FGFG',
            'FTFTFTFBFTFTFTFTF4FGFGF3F4FGFGFG',],

    (1,-5):['SGSGSGSGSGSGS1S2SGSGSGSGSGSGSGSG',
            'SGSGSGS1STSTST....S2SGS1..S2SGSG',
            'SGS1..STSTST................S2SG',
            'S1............................SG',
            '..............................SG',
            '................SBSB..........SG',
            '..............STSTST..........SG',
            'S3............SBSB..........STSG',
            'S1..........................STSG',
            'S3ST......................STSTSG',
            'SGSTST..................STSTSTSG',
            'SGS6S3..................STSTS4SG',
            'SGSGSGS6S3......S4S6S6S6S3S4SGSG',],

   (1,-4):['SGSGSGSGS1......S2SGSGSGS1S2SGSG',
            'SGSGSGS1..........STSTSTST..SGSG',
            'SGS1STST............STST....S2SG',
            'SGSTSTSTST....................SG',
            'SGSTSTSTSTST..................S2',
            'S1....STSTSTST................S4',
            '........STSTST....SB..........SG',
            '........STST........SB....STS4SG',
            '......S4S6S6S3............S4SGSG',
            '......S2SGSGSGS3..........SGSGSG',
            'S3........S2SGSG........S4SGSGSG',
            'SG..........SGSG........SGSGSGSG',
            'SGS6S3....S4SGSG......S4SGSGSGSG',],

    (1,-3):['SGSGS1....S2SGS1......S2SGSGSGSG',
            'SGS1......................S2SGSG',
            'SG..........................S2SG',
            'SG................ST..ST......S2',
            'S1....ST........ST......ST......',
            '................................',
            '................................',
            'S3......S4S3..................S4',
            'SG....S4SGSG........ST........SG',
            'SG....S2SGSG..ST..........ST..SG',
            'SGS3..........................SG',
            'SGSGS3......................S4SG',
            'SGSGSGS3S4S6S3S4S6S6SBS4S6S6SGSG',],

   (1,-2):["FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG",
           "FGFGFG..FGFGFGFGF1..............",
           "FGF1......F2FGFG................",
           "FG..........FGFG........W4WUWUWU",
           "FG....FT....FGF1........WLWWWWWW",
           "FG..........FG....FT....WLWWWWWW",
           "FG..........FG....FT....WLWWWWWW",
           "FG....FT....FGF3........WLWWWWWW",
           "FG..........FGFG........WLWWWWWW",
           "FGF3......F4FGFG........WLWWWWWW",
           "FGFGF3..F4FGFGFG........WLWWWWWW",
           "FGFGFGLLFGFGFGFGF3......WLWWWWWW",
           "FGFGFGLLFGFGFGFGFG......WLWWWWWW"],
    

    (1,-1):["FGFGFGLLFGFGFGFGFG......WLWWWWWW",
           "FGFGFGLLFGFGFGFGF1......WLWWWWWW",
           "FGFGFG..F2FGFGF1........WLWWWWWW",
           "FGFGF1....F2F1..........WLWWWWWW",
           "FGFG....................W2WDWDWD",
           "FGFG............................",
           "FGFGF3......RT....RT............",
           "FGFGFG..................FB....F4",
           "FGFGF1........................FG",
           "FGFGF3......FT....FT....FT....FG",
           "FGFGFG........................FG",
           "FGFGFG........................FG",
           "FGFGFGF6F6F6F3......F4F6F6F6F6FG"],
        
    (1,0):[ 'FGFGFGFGF1F2F1......F2FGFGF1FBF2',
            'FGFGFGF1..............FTFTFT....',
            'FGFGFG..........................',
            'FGFGF1..................FB......',
            'FGF1....FT..FT..................',
            '........................FB......',
            '........FT..FT..................',
            '........................FB......',
            '........FT..FT..................',
            '............................F4F6',
            'F6F3..FTFTFTFTFT........F4F6FGFG',
            'FGFGF3FTFTFTFTFTF4F6F3F4FGFGFGFG',
            'FGFGFGFTFTFTFTFTFGFGFGFGFGFGFGFG',],

    (1,1):[ 'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGFGF1F2FGFGF1F2FGFGF1F2FGFGFG',
            'FGFGF1............F2F1....F2FGFG',
            'FTFT......................F4FGFG',
            'FTFT........R4R6R3........FGFGFG',
            'F6F3......R4RGRGRGR3......FGFGFG',
            'FGF1......R2RG..RGR1......F2FGFG',
            'FGF3........RT..RT..........FTFT',
            'FGFG............................',
            'FGF1............................',
            'FGF3F4F3....................FTFT',
            'FGFGFGFGF6F3..............F4F6F6',
            'FGFGFGFGFGFGF6F3FTFTFTF4F6FGFGFG',],

    (1,2):[ 'FGFGFGFGFGF1F2FGFGFGF1F2FGFGFGFG',
            '..............F2FGF1......F2FGFG',
            '..............................F2',
            'FBFB............................',
            'FTFTFTFTFT......................',
            '............................FBFT',
            '................FTFBFTFTFTFTFTFT',
            'FT............FTFTFTFTFTFTFTFTFT',
            'FBFT........FTFTFT..............',
            'FTFT........FBFT................',
            'F3FB........FTFT................',
            'FGF3......F4F3FT............F4F6',
            'FGFG....F4FGFGF3....F4F6F6F6FGFG',],

    (1,3):[ 'FGFG....F2FGFGF1....F2FGFGFGFGFG',
            'FGF1......F2F1........FGFGF1F2FG',
            'FG....................F2F1....F2',
            'FG............................FT',
            'FG..........................FTFT',
            'F1........FBFBFTFTFTFT......FTFT',
            'FTFBFBFTFTFTFTFTFTFTFBFTFTFTFBFT',
            'FTFTFTFTFTFB..........FBFBFTFTFT',
            'FTFT......................FTFTFT',
            '..........................FTFTFT',
            '........................FTFTFTFT',
            'F6F3............F4F6F3FTFTFTFTFB',
            'FGFGF6F6F3....F4FGFGFGF3FTFTFTFT',],

    (1,4):[ 'FGFGFGFGF1....F2FGFGFGF1FTFTFTFB',
            'FGF1....................FBFTFTFB',
            'F1..................FB....FTFBFT',
            '..........................FBFTFT',
            '......FTFTFT........FB....FTFTFT',
            'FTFTFTFTFTFBFTFT............FTFT',
            'FTFTFT....FTFTFTFT............FT',
            'FT..........FTFTFT........FT..FB',
            '..............FTFT............FT',
            '..............FT............FTFT',
            'F3........................FTFTFT',
            'FGF3..................FTFTFBFTFT',
            'FGFGF6F6F6F3......FTFTFTFBFTFTFT',],

    (1,5):[ 'FGFGFGFGFGF1......FBFTFTFTFBFTFT',
            'FGFGFGFGF1..............FTFTFTFT',
            'FGFGF1....................FTFTFB',
            'FGF1........................FTFT',
            'FG........FT..FT..FT........FTFT',
            'F1..........................FBFB',
            '............FB..FB..............',
            '............................FBFB',
            'F3........FT..FT..FT........FTFT',
            'FG........................FTFBFT',
            'FGF3....................FTFTFTFT',
            'FGFGF3FTFB............FTFTFBFTFT',
            'FGFGFGFTFTFTFTF4F6F3FTFTFTFTFTFT',],

        (2,-5):['STSTSTSTSTFTSTSTSTSTSBSBSTSTSTST',
            'STSTSTSBSB......FTSTSTSTSTSTSBST',
            'STFT........................STST',
            'S3..........S4S6S3..........STST',
            'SG........S4SGSGSGS3..........ST',
            'SG........S2SGSGSGSG......ST..S4',
            'S1............S2..S1..........SG',
            'ST..........................S4SG',
            'ST....SBSTST..........FT....SGSG',
            'S3..........................SGSG',
            'SGS3......................S4SGSG',
            'SGSGS3................S4S6SGSGSG',
            'SGSGSGS6S6S3....S4S6S6SGSGSGSGSG',],

   (2,-4):['SGSGSGSGSGS1....S2SGSGSGSGSGSGSG',
            'SGSGSGSGS1........S2S1S2SGSGSGSG',
            'SGSGS1ST................S2SGSGSG',
            'SGS1......................STS2SG',
            'SG............................SG',
            'SG................ST..........SG',
            'S1..............STSTST........S2',
            'S3....W4WUWUWUWUW3STST..........',
            'SG....WLWWWWWWWWWWW3............',
            'SG....W2WDWWWWWWWWWR............',
            'SGS3......W6WWWWWWWRSTST........',
            'SGSGS3....STWLWWWWWRSTSTST....S4',
            'SGSGSGS6S6S3WLWWWWWRS4S3S4S6S4SG',],

      (2,-3):['SGSGSGSGSGSGWLWWWWWRSGSGSGSGSGSG',
            'SGSGSGSGS1STWLWWWWWRS2S1S2SGSGSG',
            'SGSGS1STSTSTWLWWWWWRSTSTSTSGSGSG',
            'SGS1....STSTWLWWWWWRSTST..SGSGSG',
            '............W2WDWDW1......S2SGSG',
            '..............STSTSTST......S2SG',
            '................STST..........SG',
            'S6S3..........................S2',
            'SGSGST..........................',
            'SGSGS6S3........................',
            'SGSGSGSGS6S3..................S4',
            'SGSGSGSGSGSGS6S6S3F4F3....F4F3SG',
            'SGSGSGSGSGSGSGSGSGFGFGLLLLFGFGSG',],

    (2,-2):['FGFGF1F2FGFGFGFGFGFGFGLLLLFGFGFG',
            '..................F2F1....F2FGFG',
            '............................FGFG',
            'WUWUWUWUWUWUW3..............F2FG',
            'WWWWWWWWWWWWWR................FG',
            'WWWWWWWWWWWWWR..............F4FG',
            'WWWWWWWWWWWWWR..............FGFG',
            'WWWWWWWWWWWWWR..FT......FT..F2F1',
            'WWWWWWWWWWWWWR..................',
            'WWWWWWWWWWWWWR..................',
            'WWWWWWWWWWWWWR..............F4F6',
            'WWWWWWWWWWWWWWW7....F4F6F6F6FGFG',
            'WWWWWWWWWWWWWWWWWUWUWUWUWUWUWUWU',],

    (2,-1):["WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
           "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
           "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
           "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
           "WDWDWDWDWDWDWDWDWDWDWDWWWWWWWWWW",
           "......................W6WWWWWWWW",
           "......FT....FT..........W2WDWDWD",
           "F3..............................",
           "FG..............................",
           "FGF3..FT....FT....FT....FT....F4",
           "FGFG..........................FG",
           "FGFGF3......................F4FG",
           "FGFGFGF6F6F6F3....F4F6F6F6F6FGFG"],

    (2,0):[ 'FGF1F2FGFGFGF1....F2FGF1F2FGFGFG',
            '........F2F1..............F2FGFG',
            '............................FGFG',
            '......FTFTFTFT....FTFTFT....F2FG',
            '......................FTFT......',
            '........................FT......',
            '......FT......FTFTFT....FTFTFTF4',
            '......FT....FTFT..............FG',
            '......FT....FT................FG',
            'F6F3..FT....FT....FTFTFTFT..F4FG',
            'FGFGF6F3....................FGFG',
            'FGFGFGFG..................F4FGFG',
            'FGFGFGFGF6F3........F4F6F6FGFGFG',],

    (2 ,1):['FGFGFGFGFGF1........F2FGFGFGFGFG',
            'FGFGFGF1..............F2FGFGFGFG',
            'FGFGFG..................F2F1FGFG',
            'FGFGF1......................F2FG',
            'FGFGF3........................F2',
            'FGFGFG....FBFBFB....F4F3......FT',
            'FGFGF1..............FGFG........',
            'FTFT................FGFGF3......',
            '....................F2FGFG......',
            '....................F4FGFGF3..FT',
            'FTFT................FGFGFGFGF6F6',
            'F6F6F3..........F4F6FGFGFGFGFGFG',
            'FGFGFGF3....F4F6FGFGFGFGFGFGFGFG',],

    (2, 2):['FGFGFGF1....F2FGFGFGFGF1F2FGFGFG',
            'FGF1................FTFB..F2FGFG',
            'F1..................FTFT....FGFG',
            '................FTFTFTFT....FGFG',
            '..............FTFBFTFTFT....F2FG',
            'FTFBFB......FTFTFT............F2',
            'FTFTFTFTFTFTFTFT................',
            'FTFTFTFTFTFTFB..................',
            '..................W4WUWUWUWUWUWU',
            '..................WLWWWWWWWWWWWW',
            '..................WLWWWWWWWWWWWW',
            'F6F6F6F3..........WLWWWWWWWWWWWW',
            'FGFGFGFGF6F6F6F6F3WLWWWWWWWWWWWW',],

    (2, 5):['FTFTFTFBFBFTFTFTFTFTFTFTFTFTFTFT',
            'FTFBFTFT..............FTFTFBFBFT',
            'FTFT..........................FT',
            'FT............................FT',
            'FT............................FT',
            'FT..........................FTFT',
            '..............................FT',
            'FT..........................FTFT',
            'FT..........................FTFT',
            'FTFT........................FTFT',
            'FBFTFT....................FTFTFB',
            'FBFBFTFTFTFT..FTFBFTFT....FTFTFT',
            'FTFTFTFTFTFBFTFTFTFTFTFTFTFBFTFT',],

    (3,-4):['SGSGSTSTSTSTSTSTSTSTSTSTS2SGSGSG',
            'SGSGSTSTSTSTSTSTSTST......S2SGSG',
            'SGS1..STSTSTST..............S2SG',
            'SG..........................SBSG',
            'SG..........................STS2',
            'SG............S4S3..........SBS4',
            'S1..........S4SGSG..........S4SG',
            '............SGSGSG..SB..SB..SGSG',
            '..........S4SGSGS1..........SGSG',
            '..........SGSGSG............SGSG',
            '........S4SGSGS1..........S4SGSG',
            'S3S6S3S4SGSGSGS3..........SGSGSG',
            'SGSGSGSGSGSGSGSG......S4S6SGSGSG',],

   (3,-3):['SGSGSGSGSGSGSGS1......S2S1S2SGSG',
            'SGSGSGS1S2SGS1..............S2SG',
            'SGS1STST......................SG',
            'SGWUWUW3..............ST......S2',
            'SGWWWDW5................ST....S4',
            'SGW5..........S4S3............SG',
            'SG..........S4SGSG............SG',
            'S1..........S2SGS1....S4S3..S4SG',
            '......................S2S1..SGSG',
            '............................S2SG',
            'S3..SB......................STS2',
            'SG..............S4S6S3....STSTS4',
            'SGS6S6S4S6S4S3S4SGSGSGS6S4S3S6SG',],

    (3,-2):['FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGFGFGFGFGFGF1FTFTFTFTF2FGFGFG',
            'FGFGF1FTFTFT..............F2FGFG',
            'FGF1........................FGFG',
            'FG..........................FGFG',
            'FG..........................FGFG',
            'FG......RT....RT....RT......F2FG',
            'F1..........................FTFG',
            '............................F4FG',
            '............................FGFG',
            'F3..........................F2FG',
            'FGF6F6W8WUWUWUWUW3............FG',
            'WUWUWUWWWWWWWWWWWR............FG',],

    (3,-1):['WWWWWWWWWWWWWWWWWR............FG',
            'WWWWWWWWWWWWWWWWWR............FG',
            'WWWWWWWWWWWWWWWWWR............FG',
            'WWWWWWWWWWWWWWWWWR............F2',
            'WWWWWWWWWWWWWWWWWR..FT..FB......',
            'WWWWWWWWWWWWWWWWWR............F4',
            'WDWDWDWDWDWDWDWDW1............FG',
            '..............................FG',
            '..............................FG',
            'F3........................FTFTFG',
            'FG..................FTFTF4F6F6FG',
            'FGF3..........FTFTF4F6F6FGFGFGFG',
            'FGFGF3......F4F6F6FGFGFGFGFGFGFG',],

    (3,0):[ 'FGFGF1......F2FGFGF1F2FGFGFGFGFG',
            'FGFG..........F2F1..RTF2FGFGFGFG',
            'FGF1FTRT..................F2FGFG',
            'F1FTFTFTFT..................F2FG',
            '......FTFTFTFT..............FTFG',
            '........FTFTFTFTFT............FG',
            'F3..........FTRTFTFTFT........FG',
            'FG..............FTFTF4F6F3....FG',
            'FG..................F2FGF1..F4FG',
            'FGF3........................FGFG',
            'FGFGF6F6F3................F4FGFG',
            'FGFGFGFGFGF6F3FT........F4FGFGFG',
            'FGFGFGFGFGFGFGF6F6F6F6F6FGFGFGFG',],

    (3,1): ['FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGFGFGF1..F2FGFGFGFGF1F2FGFGFG',
            'F1F2F1........F2FGFGF1....F2FGF1',
            'FT..............F2F1............',
            '................................',
            '................................',
            '..............W4WUWUWUWUWUWUWUWU',
            'FT............WLWWWWWWWWWWWWWWWW',
            'F3............WLWWWWWWWWWWWWWWWW',
            'FGF6F3........WLWWWWWWWWWWWWWWWW',
            'FGFGFGF3......WLWWWWWWWWWWWWWWWW',],

    (3,2):[ 'FGFGFGF1......WLWWWWWWWWWWWWWWWW',
            'FGFGFGF3......WLWWWWWWWWWWWWWWWW',
            'FGFGFGFG......WLWWWWWWWWWWWWWWWW',
            'FGFGFGFGFT..FTWLWWWWWWWWWWWWWWWW',
            'FGFG..F1......WLWWWWWWWWWWWWWWWW',
            'F1FT..FT......WLWWWWWWWWWWWWWWWW',
            '..............WLWWWWWWWWWWWWWWWW',
            '............W8WWWWWWWWWWWWWWWWWW',
            'WUWUWUWUWUWUWWWWWWWWWWWWWWWWWWWW',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',],

    (4,-1):['FGFGFGFGFGFGF1F2FGFGFGFGFGFGFGFG',
            'FGF1......................F2FGFG',
            'FG..........................F2FG',
            'F1..........................FTFT',
            '..........................FTFTFT',
            'F3........................FTFTFT',
            'FG..........................FTFT',
            'FG........................FTFTFT',
            'FG..........................FTFT',
            'FGF3......................F4F6F6',
            'FGFGF3......FT....FT..F4F6FGFGFG',
            'FGFGFGF6F6F3F4F6F6F3F4FGFGFGFGFG',
            'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',],

    (4,0):[ 'FGFGFGFGFGFGF1F2FGFGFGFGFGFGFGFG',
            'FGFGFGF2FGF1..........FTF2FGFGFG',
            'FGFGFGFT....................F2FG',
            'FGFGF1........................F2',
            'FGF1............................',
            'FG..........T4TTT3..............',
            'F1........FTT2..T1FT............',
            'F3............................F4',
            'FG........................F4F6FG',
            'FGF3................F4F3F4FGFGFG',
            'FGFGF3............F4FGFGFGFGFGFG',
            'FGFGFGF3F4F6F3F4F6FGFGFGFGFGFGFG',
            'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',],

    (4,1):[ 'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGFGFGFGFGFGFGFGFGFGFGFGFGFGFG',
            'FGFGF2FGFGFGFGFGFGFGFGF1FTF2FGFG',
            'FGF1..F2FGFGFGFGF1F2F1......F2F1',
            '........F2F1F2F1................',
            '................................',
            '................................',
            'WUWUWUWUWUWUWUWUWUWUWUWUWUWUWUWU',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',],

    (5,0):[ 'FGFGFGFGFGFGFGWLWWWWWWWWWWWWWWWW',
            'FGFGFGFGFGFGFGWLWWWWWWWWWWWWWWWW',
            'FGFGF1F2FGFGF1W2WDWDWDWWWWWWWWWW',
            '......FTF2F1FT........W6WWWWWWWW',
            '........................WLWWWWWW',
            '........................WLWWWWWW',
            '........................WLWWWWWW',
            'F3......................WLWWWWWW',
            'FGF6F6F3FT..............WLWWWWWW',
            'FGFGFGFGF3FT............WLWWWWWW',
            'FGFGFGFGFGF6F3..........WLWWWWWW',
            'FGFGFGFGFGFGFG..........WLWWWWWW',
            'FGFGFGFGFGFGFGF3........WLWWWWWW',],

    (5,1):[ 'FGFGFGFGFGFGFGFG........WLWWWWWW',
            'FGFGFGFGFGFGFGFG........WLWWWWWW',
            'FGFGFGFGFGFGFGF1........WLWWWWWW',
            'FGFGFGFGFGFGF1FT........WLWWWWWW',
            'FGF1F2FGFGF1FT..........WLWWWWWW',
            '........................WLWWWWWW',
            '........................WLWWWWWW',
            '......................W8WWWWWWWW',
            'WUWUWUWUPPPPPPWUWUWUWUWWWWWWWWWW',
            'WWWWWWWWPPPPPPWWWWWWWWWWWWWWWWWW',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',],

    (200,250):['RGRGR1R2RGRGRGR1R2RGRGRGRGRGRGRG',
            'RGR1........................R2RG',
            'RG............................R2',
            'RG............................R4',
            'R1............................RG',
            'R3............................RG',
            'RG............................RG',
            'RGR3........................R4RG',
            'RGRG..FT................FT..RGRG',
            'RGRG....FT............FT....RGRG',
            'RGRGR6R3................R4R6RGRG',
            'RGRGRGRGR6R6R3....R4R6R6RGRGRGRG',
            'RGRGRGRGRGRGRG....RGRGRGRGRGRGRG',],

    (201,250):['RGRGR1R2RGRGRGR1R2RGRGRGRGRGRGRG',
            'RGR1........................R2RG',
            'RG..FT....................FT..R2',
            'RG....FT................FT....R4',
            'R1............................RG',
            'R3............................RG',
            'RG............................RG',
            'RGR3........................R4RG',
            'RGRG........................RGRG',
            'RGRG........................RGRG',
            'RGRGR6R3..R4R3....R4R3..R4R6RGRG',
            'RGRGRGRGR6RGRG....RGRGR6RGRGRGRG',
            'RGRGRGRGRGRGRG....RGRGRGRGRGRGRG',],

    (202,250):['FGFGF1F2FGFGFGF1F2FGFGFGFGFGFGFG',
            'FGF1........................F2FG',
            'FG..FT....................FT..F2',
            'FG....FT................FT....F4',
            'F1............................FG',
            'F3............................FG',
            'FG............................FG',
            'FGF3........................F4FG',
            'FGFG........................FGFG',
            'FGFG........................FGFG',
            'FGFGF6F3..F4F3....F4F3..F4F6FGFG',
            'FGFGFGFGF6FGFG....FGFGF6FGFGFGFG',
            'FGFGFGFGFGFGFG....FGFGFGFGFGFGFG',],

    (203,250):['RGRGR1R2RGRGRGR1R2RGRGRGRGRGRGRG',
            'RGR1........................R2RG',
            'RG..FT....................FT..R2',
            'RG....FT................FT....R4',
            'R1............................RG',
            'R3............................RG',
            'RG............................RG',
            'RGR3........................R4RG',
            'RGRG........................RGRG',
            'RGRG........................RGRG',
            'RGRGR6R3..R4R3....R4R3..R4R6RGRG',
            'RGRGRGRGR6RGRG....RGRGR6RGRGRGRG',
            'RGRGRGRGRGRGRG....RGRGRGRGRGRGRG',],

    (204,250):['RGRGRGRGRGRGRGRGRGRGRGRGRGRGRGRG',
            'RGRGR1......................R2RG',
            'RGR1..........................RG',
            'RGWUWUPPWUWUWUWUWUWUWUWUWUWUWURG',
            'RGWDWDPPWDWDWDWDWDWDWDWDWDWDWDRG',
            'RG............................R2',
            'RG..............................',
            'RG............................R4',
            'RGWUWUPPWUWUWUWUWUWUWUWUWUWUWURG',
            'RGWDWDPPWDWDWDWDWDWDWDWDWDWDWDRG',
            'RGR3........................R4RG',
            'RGRGR3....................R4RGRG',
            'RGRGRGR6R6R6R6R6R6R6R6R6R6RGRGRG',],

    (205,250):['SGSGS1S2SGSGSGS1S2SGSGSGSGSGSGSG',
            'SGS1........................S2SG',
            'SG..FT....................FT..S2',
            'SG....FT................FT....S4',
            'S1............................SG',
            'S3............................SG',
            'SG............................SG',
            'SGS3........................S4SG',
            'SGSG........................SGSG',
            'SGSG........................SGSG',
            'SGSGS6S3..S4S3....S4S3..S4S6SGSG',
            'SGSGSGSGS6SGSG....SGSGS6SGSGSGSG',
            'SGSGSGSGSGSGSG....SGSGSGSGSGSGSG',],

    (206,250):['SGSGS1S2SGSGSGS1S2SGSGSGSGSGSGSG',
            'SGS1........................S2SG',
            'SG............................S2',
            'SG............................S4',
            'S1............................SG',
            'S3............................SG',
            'SG............................SG',
            'SGS3........................S4SG',
            'SGSG..ST................ST..SGSG',
            'SGSG....ST............ST....SGSG',
            'SGSGS6S3................S4S6SGSG',
            'SGSGSGSGS6S6S3....S4S6S6SGSGSGSG',
            'SGSGSGSGSGSGSG....SGSGSGSGSGSGSG',],

    (207,250):['RGRGR1R2RGRGRGR1R2RGRGRGRGRGRGRG',
            'RGR1........................R2RG',
            'RG............................R2',
            'RG............................R4',
            'R1............................RG',
            'R3............................RG',
            'RG............................RG',
            'RGR3........................R4RG',
            'RGRG..FT................FT..RGRG',
            'RGRG....FT............FT....RGRG',
            'RGRGR6R3................R4R6RGRG',
            'RGRGRGRGR6R6R3....R4R6R6RGRGRGRG',
            'RGRGRGRGRGRGRG....RGRGRGRGRGRGRG',],

    (208,250):['RGRGR1R2RGRGRGR1R2RGRGRGRGRGRGRG',
            'RGR1........................R2RG',
            'RG............................R2',
            'RG............................R4',
            'R1............................RG',
            'R3............................RG',
            'RG............................RG',
            'RGR3........................R4RG',
            'RGRG..FT................FT..RGRG',
            'RGRG....FT............FT....RGRG',
            'RGRGR6R3................R4R6RGRG',
            'RGRGRGRGR6R6R3....R4R6R6RGRGRGRG',
            'RGRGRGRGRGRGRG....RGRGRGRGRGRGRG',],

    (209,250):['RGRGR1R2RGRGRGR1R2RGRGRGRGRGRGRG',
            'RGR1........................R2RG',
            'RG............................R2',
            'RG............................R4',
            'R1............................RG',
            'R3............................RG',
            'RG............................RG',
            'RGR3........................R4RG',
            'RGRG..FT................FT..RGRG',
            'RGRG....FT............FT....RGRG',
            'RGRGR6R3................R4R6RGRG',
            'RGRGRGRGR6R6R3....R4R6R6RGRGRGRG',
            'RGRGRGRGRGRGRG....RGRGRGRGRGRGRG',],

    (239,250):['SGSGSGSGS1S2SGSGSGS1S2SGSGSGSGSG',
            'SGSGS1....................S2SGSG',
            'SGS1........................S2SG',
            'SG............................SG',
            'SG..........................STS2',
            'SGS3....................W4WUWUWU',
            'SGSG....................WLWWWWWW',
            'SGS1....................PPPPPPPP',
            'SG......................WLWWWWWW',
            'SGST....................WLWWWWWW',
            'SGS6S3ST................W2WWWWW5',
            'SGSGSGS3S4S6S6S3........STST..S4',
            'SGSGSGSGSGSGSGSGS6S6S3S4S6S6S4S6',],

 (240,250):['SGSGSGSGSGS1S2SGSGSGSGSGSGSGSGSG',
            'SGSGS1..............S2SGSGSGSGSG',
            'SGS1......................S2SGSG',
            'SG..........................S2SG',
            'S1..ST..ST....................SG',
            'WUWUWUPPWUWUWUWUWUWUW3........S2',
            'WWWWWWPPWWWWWWWWWDWDW1........S4',
            'PPPPPPPPWWWWWWW5..............SG',
            'WWWWWWWWWWWWWR................SG',
            'WDWDWDWDWDWDW1..............S4SG',
            'SGS3........................SGSG',
            'SGSGS6S3..................S4SGSG',
            'SGSGSGSGS6S6S3....S4S6S3S4SGSGSG',],

    (250,250):['RGRGR1R2RGRGRGR1R2RGRGRGRGRGRGRG',
            'RGR1........................R2RG',
            'RG....FB................FB....R2',
            'RG............................R4',
            'R1............................RG',
            'R3............................RG',
            'RG............................RG',
            'RGR3........................R4RG',
            'RGRG..FB................FB..RGRG',
            'RGRG........................RGRG',
            'RGRGR6R3................R4R6RGRG',
            'RGRGRGRGR6R6R3....R4R6R6RGRGRGRG',
            'RGRGRGRGRGRGRG....RGRGRGRGRGRGRG',],

    

    (299,300):["RGRGRGRGRGRGRGRGRGRGRGRGRGRGRGRG",
           "RG........W8WUWUWWW3........R2RG",
           "R1........W4WWWWWWWR............",
           "RB........WLWWWWWWWR........R4R6",
           "R3........PPPPWWWWWR........RGRG",
           "RG........WLWWWWWWWR........R2RG",
           "RG........W6WWWWWWWR..........RG",
           "RG..........WLWWWWWR..........RG",
           "RG..........W2WDWDW1..........RG",
           "RG........R4R6R6R6............RG",
           "RGR3......RGRGRGRG........FB..RG",
           "RGRG......RGRGRGRG............RG",
           "RGRG....R4RGRGRGRGR3....R4R6R6RG"],

    (299,301):["RGR1....RGRGRGRGRGRG....R2RGRGRG",
           "RG......RGRGRGRGRGRG........R2RG",
           "RG......RGRG..RGRGRG..........RG",
           "RG....R4RGRG..R2RGRGR3........RG",
           "RG....RGRGRG....RGRGRGR3......RG",
           "RG....RGRGRG....RGRGRGRG......RG",
           "RG....RGRGRG....RGRGRGR1......RG",
           "RGR3..R2RGRG....RGRGR1........RG",
           "RGRG....R2R1....RGRG..........RG",
           "RGRG............R2R1..........RG",
           "RGRG......................R6R6RG",
           "RGRGR3..................R4RGRGRG",
           "RGRGRGW4WUWUWUWUWUWUWUW3RGRGRGRG"],

    (300,300):["RGRGRGRGRGRGRGRGRGRGRGRGRGRGRGRG",
           "RGRGRGR1....................R2RG",
           "..................RB..RB......RG",
           "R6R3....................RBRB..RG",
           "RGR1......R4R6R3..............RG",
           "RG......R4RGRGRGR3............RG",
           "RG......RGRGRGR1..............RG",
           "RG....R4RGRGR1................RG",
           "RG....R2RGR1..................RG",
           "RG....................R6..R6..RG",
           "RG..................R4RG..RGR6RG",
           "RGRT......R4R3....R4RGRG..RGRGRG",
           "RGR6R6R6R6RGRGR6R6RGRGRG..RGRGRG"],

(208,202):[ 'RGRGRGR2RGRGR1R2RGRGRGRGRGRGRGRG',
            'RGRGR1FBR2R1........R2RGRGRGRGRG',
            'RGRG................R4RGRGRGRGRG',
            'RGR1..............R4RGRGRGRGRGRG',
            'RG........R4R6R6R6RGRGRGRGRGRGRG',
            'RG........R2RGRGRGRGR1R2RGRGRGRG',
            'RG..........R2RGRGR1....R2R1....',
            'RG............R2R1..............',
            'RG..............................',
            'RG............................R4',
            'RG..........................FBRG',
            'RGR6R6R3....................R4RG',
            'RGRGRGRGR6R3R4R6R6R6R6R6R6R6RGRG',],

(209,202):[ 'RGRGRGRGRGRGRGRGRGRGRGRGRGRGRGRG',
            'RGRGRGRGRGRGRGRGRGRGRGRGRGRGRGRG',
            'RGRGRGRGRGRGRGRGRGRGRGRGRGRGRGRG',
            'RGRGRGRGR1R2RGRGRGRGRGRGRGRGRGRG',
            'RGRGRGR1........R2RGRGRGRGRGRGRG',
            'RGR1..................R2RGRGRGRG',
            '........................RGRGRGRG',
            '........................RGRGRGRG',
            '........................R2RGRGRG',
            'R3........................R2R1..',
            'RG..............................',
            'RGR3..FT....FT..........R4R6R6R6',
            'RGRGR6R3....R4R6R6R6R6R6RGRGRGRG',],

(210,202):[ 'RGRGRGRGRGRGR1....R2RGRGRGRGRGRG',
            'RGRGR1....FT........FT....R2RGRG',
            'RGR1......FB........FB......R2RG',
            'RG........FT........FT........RG',
            'RG............................RG',
            'RG............................RG',
            'RG............................RG',
            'RG..........FTR4R3FT..........RG',
            'R1............RGRG............RG',
            '............FTR2R1FT..........RG',
            '............................R4RG',
            'R3........................R4RGRG',
            'RGR6R6R6R6R6R6R6R6R6R6R6R6RGRGRG',],

(210,201):[ 'RGRGRGRGRGRGRGR1R2RGRGRGRGRGRGRG',
            'RGR1......RGRG....RGRG......R2RG',
            'RG....FT..RGRG....RGRG..FT....RG',
            'RG........R2R1....R2R1........RG',
            'RG............................RG',
            'RG............................RG',
            'RG....FT................FT....RG',
            'RG............................RG',
            'RG............................RG',
            'RG............................RG',
            'RG....FT..R4R3....R4R3..FT....RG',
            'RGR3......RGRG....RGRG......R4RG',
            'RGRGR6R6R6RGRG....RGRGR6R6R6RGRG',],

(210,200):[ 'RGRGRGRGR1R2RGRGRGRGRGRGRGRGRGRG',
            'RGRGR1..........R2RGRGRGRGRGRGRG',
            'RGRG..............R2RGRGRGRGRGRG',
            'RGR1................R2RGRGRGRGRG',
            'RG....................R2RGRGRGRG',
            'RG..............................',
            'R1..............................',
            'R3..............................',
            'RG....................R4R6R6R6R6',
            'RG..................R4RGRGRGRGRG',
            'RG................R4RGRGRGRGRGRG',
            'RGR3............R4RGRGRGRGRGRGRG',
            'RGRGR3..R4R6R6R6RGRGRGRGRGRGRGRG',
            "RGRGRGRGRGRGRGRGRGRGRGRGRGRGRGRG"],

(211,200):[ 'RGFGFGF1F2FGFGFGFGFGFGFGFGFGRGFG',
            'RGRGF1....................F2FGRG',
            'RGR1FT....................FTF2FG',
            'RG....FB................FB....FG',
            'R1......RT............RT......RG',
            '..........RB........FB........RG',
            '............FT....RT..........RG',
            '..............................R2',
            'R3............................R4',
            'RG............................RG',
            'RG............................RG',
            'RGR3........................F4RG',
            'RGRGR3R4R6F6F6F3R4R6F6F6R6R6FGRG',],

    }

#Load the first room, and then start the gameloop 

loadRoom()

gameloop()

#Once the gameloop is exited, quit pygame and then the main file

pygame.quit()
quit()
