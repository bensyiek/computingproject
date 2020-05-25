from tkinter import *
from PIL import Image, ImageTk, ImageEnhance
from tkinter import font
import time
import math, threading, random

master = Tk()
master.geometry('500x700')
master.title('Pokemon Draft')

backgrounds = {
    'route' : {'filePath' : 'assets/routeBackground.png', 'bgColor' : 'green'},
    'indoor' : {'filePath' : 'assets/indoorBackground.png','bgColor' : 'grey'}
    }

assets = {
    'triangle' : 'assets/trianglePointer.jpg',
    'fightButton' : 'assets/fightButton.png',
    'grass' : 'assets/Basic_Grass.png',
    'indoor-enemy' : 'assets/indoor-enemy-platform.png',
    'indoor-user' : 'assets/indoor-user-platform.png'
    }

trainerSprites = {'Blue' : 'assets/trainers/Blue.gif','Ben':'assets/trainers/Ben.png','Dalton':'assets/trainers/Dalton.png','Pedro':'assets/trainers/Pedro.png','Yuriy':'assets/trainers/Yuriy.png'}
trainerBackSprites = {'Ethan' : 'assets/trainers/BACK-Ethan.gif'}
pokeballs = {'Masterball' : 'assets/pokeballs/masterball.gif','Pokeball' : 'assets/pokeballs/pokeball.gif'}
throwpokeballs = {'Pokeball' : 'assets/pokeballs/throw-pokeball.gif'}
toBe = '''To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles And by opposing end them. To die—to sleep, No more; and by a sleep to say we end The heart-ache and the thousand natural shocks That flesh is heir to: 'tis a consummation Devoutly to be wish'd. To die, to sleep; To sleep, perchance to dream—ay, there's the rub: For in that sleep of death what dreams may come, When we have shuffled off this mortal coil, Must give us pause—there's the respect That makes calamity of so long life. For who would bear the whips and scorns of time, Th'oppressor's wrong, the proud man's contumely, The pangs of dispriz'd love, the law's delay, The insolence of office, and the spurns That patient merit of th'unworthy takes, When he himself might his quietus make With a bare bodkin? Who would fardels bear, To grunt and sweat under a weary life, But that the dread of something after death, The undiscovere'd country, from whose bourn No traveller returns, puzzles the will, And makes us rather bear those ills we have Than fly to others that we know not of? Thus conscience does make cowards of us all, And thus the native hue of resolution Is sicklied o'er with the pale cast of thought, And enterprises of great pitch and moment With this regard their currents turn awry And lose the name of action.'''
pokemon = {'Charizard' : 'assets/pokemon/charizard.gif'}
pokemonBackSprites = {'Charizard' : 'assets/pokemon/charizard-back.png'}
attacks = {'fightP' : 'assets/attacks/fp/fightingPhysical.png'}

def genFunc(f, *args):
    return lambda *args2: f(*args)

class app:
    def __init__(self,master):
        self.serviceQueue = 0
        self.serving = 0
        self.waiting = False
        global backgrounds
        global assets
        self.master = master
        self.animRunning = False
        
        self.battleFrame = Frame(master,relief=SUNKEN,borderwidth=5,height=350,width=500,bg=backgrounds['indoor']['bgColor'])
        self.battleFrame.grid(row=0,column=0,sticky=W+E+N+S,columnspan=2)
        self.battleCanvas = Canvas(self.battleFrame,width=480,height=350)
        self.battleCanvas.pack()
        self.backgroundPilImage = Image.open(backgrounds['indoor']['filePath'])
        self.backgroundPilImage = self.backgroundPilImage.resize((500,355))
        self.background = ImageTk.PhotoImage(self.backgroundPilImage)
        self.backgroundImage = self.battleCanvas.create_image(0,0,image=self.background,anchor=NW,tags=('background-indoor','background','indoor'))    
        
        self.DPPtFont = font.Font(family='Pokemon DPPt',size=26)
        self.battleFont = font.Font(family='Pokemon DPPt',size=26,weight="bold")
        self.textFrame = Frame(master,relief=RAISED,borderwidth=5,height=150,width=500,bg='white')
        self.textFrame.grid(row=1,column=0,sticky=W+E+N+S)

        self.textBox0 = Label(self.textFrame,text="What will you do?",font=self.DPPtFont,bg='white',anchor='center')
        self.textBox0.place(x=10,y=32,anchor='w')
        self.textBox1 = Label(self.textFrame,text="Your options are: Fight, Switch",font=self.DPPtFont,bg='white',anchor='center')
        self.textBox1.place(x=10,y=67,anchor='w')
        self.textBox2 = Label(self.textFrame,text="",font=self.DPPtFont,bg='white',anchor='center')
        self.textBox2.place(x=10,y=102,anchor='w')
        self.triangleImageFile = Image.open(assets['triangle'])
        self.triangleImageFile = ImageTk.PhotoImage(self.triangleImageFile)
        self.triangle = Label(master=self.textFrame,image=self.triangleImageFile,bg='white')

        self.buttonFrame = Frame(master,height=200,width=500,bg='white',relief=RAISED,bd=5)
        self.buttonFrame.grid(row=2,column=0,sticky=W+E+N+S)

        global toBe
        self.fightButton = Button(self.buttonFrame,text='FIGHT',font=self.DPPtFont,border=0,relief=FLAT)
        self.fightButton.grid(row=0,column=0,sticky="wens")
        self.switchButton = Button(self.buttonFrame,bg='blue',fg='white',text='SWITCH',font=self.DPPtFont,relief=FLAT,border=0,command = lambda: self.runText(toBe))
        self.switchButton.grid(row=1,column=0,sticky="wens")

        self.tBoxPointer = 0
        self.tBox = {
            '0' : self.textBox0,
            '1' : self.textBox1,
            '2' : self.textBox2
            }
        self.initResources()

#------------------------------------------------------------------------------------------------------------------------------#
# The following are functions pertaining to the initialize of battles

    def initResources(self):
        self.scrollPlatforms(1)

    ## FLOW FOR OPENING:
    ## Platforms scroll on screen. When finished, scrollPlatforms calls checker
    ## the firstSendOutChecker will make sure the trainer anim has finished before playing the anim for the first pokemon
    ## then play anim for user

    def scrollPlatforms(self,init=1,userIm=False,trainerIm=False):
        if init:
            ##First initialize the sprites for the trainers and the platforms.
            ##Trainers initialized after platforms so that they show up on top.
            ##Sprites are resized so that they appear better
            
            self.enemyPlatformImageFile = Image.open(assets['indoor-enemy'])
            self.enemyPlatformImageFile = self.enemyPlatformImageFile.resize((225,75))
            self.enemyPlatformImageFile = ImageTk.PhotoImage(self.enemyPlatformImageFile)
            self.enemyPlatform = self.battleCanvas.create_image(650,175,image=self.enemyPlatformImageFile,tags=('platform','enemy-platform'))
            
            self.enemyTrainerSpriteFile = Image.open(trainerSprites['Yuriy']) ##inits the gif file we will use later
            self.enemyTrainerSprite = ImageTk.PhotoImage(self.enemyTrainerSpriteFile.resize((141,141)))
            self.enemyTrainer = self.battleCanvas.create_image(650,175,image=self.enemyTrainerSprite,anchor=S,tags=("enemy-trainer"))

            self.userPlatformImageFile = Image.open(assets['indoor-user'])
            self.userPlatformImageFile = self.userPlatformImageFile.resize((325,40))
            self.userPlatformImageFile = ImageTk.PhotoImage(self.userPlatformImageFile)
            self.userPlatform = self.battleCanvas.create_image(-300,360,image=self.userPlatformImageFile,anchor=SW,tags=('platform','user-platform'))

            self.userTrainerSpriteFile = Image.open(trainerBackSprites['Ethan'])
            self.userTrainerSprite = ImageTk.PhotoImage(self.userTrainerSpriteFile.resize((180,180)))
            self.userTrainer = self.battleCanvas.create_image(-300,360,image=self.userTrainerSprite,anchor=SW,tags=('user-trainer'))

            self.blackFile = Image.open('assets/black/black250.png')
            self.blackFile = self.blackFile.resize((500,355))
            self.blackFileTk = ImageTk.PhotoImage(self.blackFile)
            self.black = self.battleCanvas.create_image(0,0,image=self.blackFileTk,anchor=NW,tags=('black'))
            self.blackAlpha = 250
        else:
            ##then iterate until the platforms are in place.
            if self.battleCanvas.coords('enemy-platform')[0] == 350:
                self.runGif(self.enemyTrainerSpriteFile,'enemy-trainer')
                self.runText('You have been challenged by Guitarist Yuriy!')
                self.sendOutFirstPokemonChecker()
                return
            else:
                if self.blackAlpha > 0:
                    self.blackFile.putalpha(self.blackAlpha)
                    #self.blackFile.convert('RGBA').save('assets/black/black' + str(self.blackAlpha) + '.png')
                    self.blackFileTk = ImageTk.PhotoImage(self.blackFile)
                    self.battleCanvas.delete('black')
                    self.black = self.battleCanvas.create_image(0,0,image=self.blackFileTk,anchor=NW,tags=('black'))
                    self.blackAlpha -= 5
                self.battleCanvas.move('enemy-platform',-6,0)
                self.battleCanvas.move('user-platform',6,0)
                self.battleCanvas.move('enemy-trainer',-6,0)
                self.battleCanvas.move('user-trainer',6,0)
                self.master.update()
        k = genFunc(self.scrollPlatforms,0)
        self.master.after(15,k)

    def sendOutFirstPokemonChecker(self):
        if self.animRunning == 'enemy-trainer':
            master.after(50,self.sendOutFirstPokemonChecker)
            return
        else:
            self.runText('Pokemon Trainer Blue sent out Charizard!')
            master.after(250,self.moveTrainerOffscreen)
            master.after(350,self.enemyPokemonSendOut)
    def moveTrainerOffscreen(self,count=0): ##recurs until trainer offstage, then recurs until animation finished, then recurs until pokemon in play, then recurs until pokemon anim finished
        ##each of count and ready are ways to play animations with defined frame lengths/anim lengths
        ##i've split into count and ready to make it easier to understand
        ##count: refers to the movement of enemy trainer and pokeball opening
        ##ready: refers to the pokemon's size and 'readiness' to come out
        if count < 50:
            self.battleCanvas.move('enemy-trainer',5,0)
            k = genFunc(self.moveTrainerOffscreen,count+1)
            master.after(15,k)
            return
        elif count == 50:
            self.battleCanvas.move('enemy-trainer',5,0)
            self.battleCanvas.delete('enemy-trainer')
            return

    def enemyPokemonSendOut(self,count=0,ready=0):
        ##this function first activates the pokeball anim
        ##then deals with the enlargening and gif anim of the pokemon sent out
        if count == 0 and not ready:
            self.EpokeballImageFile = Image.open(pokeballs['Pokeball'])
            self.EpokeballImageFile.seek(0)
            self.EpokeballImage = ImageTk.PhotoImage(self.EpokeballImageFile.resize((24,35)))
            k = genFunc(self.enemyPokemonSendOut,count+1)
            master.after(250,k)
            self.Epokeball = self.battleCanvas.create_image(350,175,image=self.EpokeballImage,anchor=S,tags=('enemy-pokeball'))
        elif count < 3 and not ready:
            self.EpokeballImageFile.seek(count)
            self.EpokeballImage = ImageTk.PhotoImage(self.EpokeballImageFile.resize((24,35)))
            self.battleCanvas.delete('enemy-pokeball')
            self.battleCanvas.create_image(350,175,image=self.EpokeballImage,anchor=S,tags=('enemy-pokeball'))
            if count == 2:
                k = genFunc(self.enemyPokemonSendOut,count,1)
            else:
                k = genFunc(self.enemyPokemonSendOut,count+1)
            master.after(250,k)
        elif ready == 1:
            self.EpokemonImageFile = Image.open(pokemon['Charizard'])
            self.EpokemonImage = ImageTk.PhotoImage(self.EpokemonImageFile.resize((1,1)))
            self.Epokemon = self.battleCanvas.create_image(350,75,image=self.EpokemonImage,tags=('enemy-pokemon'))
            k = genFunc(self.enemyPokemonSendOut,count,5)
            master.after(50,k)
        elif ready <= 100 and ready > 1: ##ready used as a size modifier
            self.EpokeballImageFile = self.EpokeballImageFile.resize((int(24*(100-ready)/100+1),int(35*(100-ready)/100+1)))
            self.EpokeballImage = ImageTk.PhotoImage(self.EpokeballImageFile)
            self.battleCanvas.delete('enemy-pokeball')
            self.battleCanvas.create_image(350,175,anchor=S,image=self.EpokeballImage,tags=('enemy-pokeball'))

            self.EpokemonImage = ImageTk.PhotoImage(self.EpokemonImageFile.resize(((int(math.log(ready)/math.log(100)*141)),int(math.log(ready)/math.log(100)*141))))
            self.battleCanvas.delete('enemy-pokemon')
            self.battleCanvas.create_image(350,180,anchor=S,image=self.EpokemonImage,tags=('enemy-pokemon'))
            
            k = genFunc(self.enemyPokemonSendOut,count,ready+5)
            master.after(20,k)
        elif ready == 105: ##ready used as a position modifier
            self.battleCanvas.delete('enemy-pokeball')
            k = genFunc(self.enemyPokemonSendOut,count,140)
            master.after(100,k)
        elif ready >= 140: ##loads the next gif in the pokemon's entry anim until an end of file... at which point it just leaves it
            try:
                self.battleCanvas.delete('enemy-pokemon')
                self.EpokemonImageFile.seek(ready-140)
                self.EpokemonImage = ImageTk.PhotoImage(self.EpokemonImageFile.resize((141,141)))
                self.battleCanvas.create_image(350,180,anchor=S,image=self.EpokemonImage,tags=('enemy-pokemon'))
                k = genFunc(self.enemyPokemonSendOut,count,ready+1)
                master.after(50,k)
            except EOFError:
                self.EpokemonImageFile.seek(ready-140-2)
                self.EpokemonImage = ImageTk.PhotoImage(self.EpokemonImageFile.resize((141,141)))
                self.battleCanvas.create_image(350,180,anchor=S,image=self.EpokemonImage,tags=('enemy-pokemon'))
                master.after(250,self.moveUserTrainerOffscreen) ##starts the launching of the user trainer
                return

    def moveUserTrainerOffscreen(self,count=1):
        if count == 1:
            self.runText('Go! %s!' % 'Charizard')
        if count % 5 == 0: ##this is to allow there to be some movement in between the movement of the trainer and the sprite updates
            try:
                self.userTrainerSpriteFile.seek(int(count/5))
                coords = self.battleCanvas.coords('user-trainer')
                self.battleCanvas.delete('user-trainer')
                self.userTrainerSprite = ImageTk.PhotoImage(self.userTrainerSpriteFile.resize((180,180)))
                self.battleCanvas.create_image(coords[0],coords[1],image=self.userTrainerSprite,anchor=SW,tags=('user-trainer'))
                if count == 15:
                    self.throwStartPokeball('Charizard')
            except EOFError:
                pass
        self.battleCanvas.move('user-trainer',-2,0)
        k = genFunc(self.moveUserTrainerOffscreen,count+1)
        master.after(20, k)

    def throwStartPokeball(self,pokemon,count=0):
        if count == 0:
            self.userPokeballImageFile = Image.open(throwpokeballs['Pokeball'])
            self.userPokeballImage = ImageTk.PhotoImage(self.userPokeballImageFile.resize((25,25)))
            self.battleCanvas.create_image(147,258,image=self.userPokeballImage,tags=('user-pokeball'))
            k = genFunc(self.throwStartPokeball,pokemon,count+1)
            master.after(100,k)
        elif count > 0 and count < 16:
            if count % 2 == 0:
                try:
                    self.userPokeballImageFile.seek(int(count/2))
                    coordsPokeball = self.battleCanvas.coords('user-pokeball')
                    self.userPokeballImage = ImageTk.PhotoImage(self.userPokeballImageFile.resize((25,25)))
                    self.battleCanvas.create_image(coordsPokeball[0],coordsPokeball[1],image=self.userPokeballImage,tags=('user-pokeball'))
                except EOFError:
                    pass
            self.battleCanvas.move('user-pokeball',int(count/7),int((count ** 2)/7))
            k = genFunc(self.throwStartPokeball,pokemon,count+1)
            master.after(50,k)
        elif count == 16:
            self.battleCanvas.delete('user-pokeball')
            self.userPokemonAnim(pokemon)
            return

    def userPokemonAnim(self,pokemon,count=0):
        if count == 0:
            self.userPokemonSpriteFile = Image.open(pokemonBackSprites[pokemon])
            self.userPokemonSprite = ImageTk.PhotoImage(self.userPokemonSpriteFile.resize((1,1)))
            self.battleCanvas.create_image(140,360,image=self.userPokemonSprite,anchor=S,tags=('user-pokemon'))
            k = genFunc(self.userPokemonAnim,pokemon,count+1)
            master.after(10,k)
        elif count > 0 and count <= 100:
            self.userPokemonSprite = ImageTk.PhotoImage(self.userPokemonSpriteFile.resize((int(math.log(count)/math.log(100)*179+1),int(math.log(count)/math.log(100)*179+1))))
            self.battleCanvas.delete('user-pokemon')
            self.battleCanvas.create_image(140,360,image=self.userPokemonSprite,anchor=S,tags=('user-pokemon'))
            k = genFunc(self.userPokemonAnim,pokemon,count+1)
            master.after(8,k)
        elif count > 100 and count <= 130:
            self.battleCanvas.move('user-pokemon',(-1) ** count * 15,0)
            k = genFunc(self.userPokemonAnim,pokemon,count+1)
            master.after(int(125*math.log(count-100)/math.log(30)),k)
        elif count == 131:
            self.fightingPhysical('enemy')
        
            
        ##REFERENCE: finish userPlatform at (0,360) and enemyPlatform at (350,175)

#------------------------------------------------------------------------------------------------------------------------------#
##Modifications on the pokemon in play
##ex. fainting

    def userPokemonFaint(self,count=0):
        if count == 0:
            self.runText('Charizard fainted!')
            k = genFunc(self.userPokemonFaint,count+1)
            master.after(1,k)
        elif count > 0 and count <=45:
            self.battleCanvas.move('user-pokemon',0,4)
            k = genFunc(self.userPokemonFaint,count+1)
            master.after(5,k)
        elif count == 46:
            self.battleCanvas.delete('user-pokemon')

    def enemyPokemonFaint(self,count=0):
        if count == 0:
            self.runText("Blue's Charizard fainted!")
            k = genFunc(self.enemyPokemonFaint,count+1)
            self.EpokemonImageFile = self.EpokemonImageFile.resize((141,141))
            self.EpokemonImageFile = self.EpokemonImageFile.convert('RGBA')
            master.after(1,k)
        if count > 0 and count <= 150:
            size = self.EpokemonImageFile.size
            print(size)
            self.EpokemonImageFile = self.EpokemonImageFile.crop((0,0,size[0],size[1]-4))
            self.EpokemonImage = ImageTk.PhotoImage(self.EpokemonImageFile)
            self.battleCanvas.delete('enemy-pokemon')
            self.battleCanvas.create_image(350,180,image=self.EpokemonImage,anchor=S,tags=('enemy-pokemon'))
            k = genFunc(self.enemyPokemonFaint,count+1)
            master.after(5,k)

#------------------------------------------------------------------------------------------------------------------------------#
##MOVE ANIMATIONS

    def fightingPhysical(self,targLoc=False,count=0): ##targLoc = target and/or target location
        ##idea: thread a bunch of randomly generated fists.
        ##these fists increase decreasingly in size (math.log?) and then stay at the peak for a split second then disappear
        ##if started at different times, could work well?
        ##coords of fist centers could vary but might work well methinks
        if count == 0:
            if targLoc == 'user':
                targLoc = (0,360)
            else:
                targLoc = (350,175)
            k = genFunc(self.fightingPhysical,targLoc,1)
            master.after(45,k)
        elif count <= 8:
            j = genFunc(self.randomFists,(targLoc[0]+random.randint(-50,50),targLoc[1]+random.randint(-50,50)),count)
            t = threading.Thread(target=j)
            t.start()
            k = genFunc(self.fightingPhysical,targLoc,count+1)
            master.after(50,k)

    def randomFists(self,location,identifier,count=0):
        for count in range(0,100):
            if count == 0:
                self.fpFile = Image.open(attacks['fightP'])
                time.sleep(0.1)
            elif count >= 1 and count <= 50:
                newSize = (int(math.log(count)/math.log(50)*46+1),int(math.log(count)/math.log(50)*46+1))
                self.fpImage = ImageTk.PhotoImage(self.fpFile.resize(newSize))
                self.battleCanvas.delete('attack'+str(identifier))
                self.battleCanvas.create_image(location[0],location[1],image=self.fpImage,tags=('attack'+str(identifier)))
                time.sleep(0.1)
            

    def old(self,targLoc,count):
        if count == 0:
            if targLoc == 'user':
                targLoc = (0,360)
            else:
                targLoc = (350,175)
            try:
                self.fpFile
            except:
                self.fpFile = Image.open(attacks['fightP'])
        if count > 0 and count <= 20:
            self.fpImage = ImageTk.PhotoImage(self.fpFile.resize((int(count/50*46+1),int(count/50*37+1))))
            self.battleCanvas.create_image(targLoc[0],targLoc[1],image=self.fpImage,tags=('attack'))
            k = genFunc(self.fightingPhysical,targLoc,count+1)
            master.after(5,k)
        elif count > 20 and count <= 40:
            self.battleCanvas.delete('attack')
            self.fpImage = ImageTk.PhotoImage(self.fpFile.resize((int(count/50*46+1),int(count/50*37+1))))
            self.battleCanvas.create_image(targLoc[0],targLoc[1],image=self.fpImage,tags=('attack'))
            self.fpImage = ImageTk.PhotoImage(self.fpFile.resize((int(count/50*46+1),int(count/50*37+1))))
            self.battleCanvas.create_image(targLoc[0]+20,targLoc[1]-20,image=self.fpImage,tags=('attack'))
            k = genFunc(self.fightingPhysical,targLoc,count+1)
            master.after(10,k)
        elif count > 40 and count <= 60:
            self.battleCanvas.delete('attack')
            if count <= 50:
                self.fpImage = ImageTk.PhotoImage(self.fpFile.resize((int(count/50*46),int(count/50*37))))
                self.battleCanvas.create_image(targLoc[0],targLoc[1],image=self.fpImage,tags=('attack'))
            elif count >=50 and count<70:
                self.fpImage = ImageTk.PhotoImage(self.fpFile.resize((int((70-count)/20*46+1),int((70-count)/20*37+1))))
                self.battleCanvas.create_image(targLoc[0],targLoc[1],image=self.fpImage,tags=('attack'))
            self.fpImage = ImageTk.PhotoImage(self.fpFile.resize((int(count/50*46+1),int(count/50*37+1))))
            self.battleCanvas.create_image(targLoc[0]+20,targLoc[1]-20,image=self.fpImage,tags=('attack'))
            self.fpImage = ImageTk.PhotoImage(self.fpFile.resize((int(count/50*46+1),int(count/50*37+1))))
            self.battleCanvas.create_image(targLoc[0]+50,targLoc[1]-5,image=self.fpImage,tags=('attack'))
            k = genFunc(self.fightingPhysical,targLoc,count+1)
            master.after(10,k)
            
                
#------------------------------------------------------------------------------------------------------------------------------#
# The following are functions pertaining to text scrolling across the box at the bottom.

    def runText(self,text):

        ## As the CustomFont things are stored as images, we have to update the entire screen everytime we want to do the rpgscroll
        ## thing. So this basically will iterate through the three textBoxes (0-2) using modulo 3.
        
        self.buttonText = '' ## we will be adding to this, character by character.
        self.tBoxPointer = 0 ## Tells us which textBox we are adding to
        if self.tBoxPointer == 0:
            self.clearText() ## Eventually, this will be changed to waiting for the player to either click, press enter, etc. But for right now, it's automatic.
        text = text.split(' ')
        altText = list(text)
        for word in text:
            if len(self.buttonText + word) <= 36: ## we need to first check to see if the word exceeds the character limit. i tested it, and with 35 pt font, it's approximately 25 characters that can fit before a new line is needed
                if len(self.buttonText + word) == 36:
                    self.addWord(word)
                else:
                    self.addWord(word + ' ') ## if we're here, the space fits. let's add it
                del altText[0]
                
            else:
                self.buttonText = '' ##reset the current updating thingie
                self.tBoxPointer = (self.tBoxPointer + 1) % 3 ##iterate to the next line
                master.after(45) ##uh maybe change the generic time.sleep() 
                if self.tBoxPointer == 0: ##if we've made it back to the beginning, time for triangle pointy thingie
                    self.waiting = True
                    result = ''
                    for element in altText:
                        result += element + ' '
                    master.bind("<Return>", self.notWaiting)
                    self.triangleUpdate(True,master,result)
                    return
                else:
                    self.addWord(word + ' ')
                    del altText[0]

    def triangleUpdate(self,up,master,txt):
        if not self.waiting:
            master.unbind("<Return>")
            self.triangle.place_forget()
            self.clearText()
            self.runText(txt)
        else:
            if up: ##if triangle is up, then put it down
                self.triangle.place(x=485,y=130,anchor='se')
                master.update()
                master.after(200,self.triangleUpdate, not up, master,txt)
            else: ##if triangle is down, then put it up
                self.triangle.place(x=485,y=135,anchor='se')
                master.update()
                master.after(200,self.triangleUpdate, not up, master,txt)

    def notWaiting(self,event):
        self.waiting = False

    def addWord(self,word):
        for character in word:
            self.buttonText += character
            if self.tBoxPointer == 0:
                self.textBox0.place_forget()
                self.textBox0.config(text=self.buttonText)
                self.textBox0.place(x=10,y=32,anchor='w')
            elif self.tBoxPointer == 1:
                self.textBox1.place_forget()
                self.textBox1.config(text=self.buttonText)
                self.textBox1.place(x=10,y=67,anchor='w')
            elif self.tBoxPointer == 2:
                self.textBox2.place_forget()
                self.textBox2.config(text=self.buttonText)
                self.textBox2.place(x=10,y=102,anchor='w')    
            master.update()
            if character in ',;:':
                master.after(200)
            if character in '.!?':
                master.after(500)
            else:
                master.after(15)

    def clearText(self):
        self.textBox0.place_forget()
        self.textBox1.place_forget()
        self.textBox2.place_forget()
#------------------------------------------------------------------------------------------------------------------------------#
##MISC... basically any function with universal and/or nonspecific use
            
            
    def runGif(self,gif,canvasID,count=1):
        self.animRunning = canvasID
        ##takes a PIL image object, and canvasID (which refers to the tag I use to identify it)
        try:
            gif.seek(count) ##gif.seek() updates the gif to the frame index, gif.tell() returns current index
                            ##this moves the gif by one frame
        except EOFError: ##end of file error, aka we've reached the end of the gif
            self.animRunning = False
            return
        coords = self.battleCanvas.coords(canvasID)
        self.d = ImageTk.PhotoImage(gif.resize((141,141)))
        self.battleCanvas.delete(canvasID)
        self.battleCanvas.create_image(coords[0],coords[1],image=self.d,anchor=S,tags=(canvasID))
        self.master.update()
        k = genFunc(self.runGif,gif,canvasID,count+1)
        self.master.after(250,k)
        
    def fadeaway(self):
        alpha = self.master.attributes("-alpha")
        if alpha > 0:
            alpha -= 0.01
            self.master.attributes("-alpha",alpha)
            master.after(10,self.fadeaway)
        else:
            master.quit()

App = app(master)
mainloop()
