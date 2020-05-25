from tkinter import *
from PIL import Image, ImageTk
from tkinter import font
import time
import math, threading, random
import battle
from pkmnData import *

master = Tk()
master.geometry('1000x700')
master.title(random.choice(['Pokemon Draft','Chicken Nuggets Not Included','Star Wars: Episode Look and Say','REEEEEE','Woah, thats heavy b r o','BIG CHUNGUS']))

trainerOne = battle.trainer('Ethan','Pokemon Trainer','Ethan')
trainerTwo = battle.trainer('Blue','Champion','Blue')
charizardOne = battle.pokemon('Charizard',random.randint(50,100),trainerOne)
trainerOne.addToTeam(0)
for x in range(5):
    battle.pokemon('Charizard',random.randint(1,100),trainerOne)
    trainerOne.addToTeam(x+1)
battle.pokemon('Charizard',random.randint(1,5),trainerTwo)
trainerTwo.addToTeam(0)
for x in range(5):
    battle.pokemon('Charizard',random.randint(1,5),trainerTwo)
    trainerTwo.addToTeam(x+1)
arena = battle.Arena(trainerOne,trainerTwo)

def genFunc(f, *args):
    return lambda *args2: f(*args)

def Pass():
    return

class app:
    def __init__(self,master,arena):
        self.processesComplete = 0
        
        self.battleStart = True
        self.smallestWaiting = 0
        self.taskFinished = True
        self.arena = arena
        self.serviceQueue = 0
        self.serving = 0
        self.waiting = False
        global backgrounds
        global assets
        self.master = master
        self.animRunning = False
        self.emCenterCoords = (350,180)
        self.userCenterCoords = (140,320)
        self.tabletCurrentlyGreySlide = False

        self.arena.setApp(self) ##gives arena the info needed to let 
        
        self.battleFrame = Frame(master,relief=SUNKEN,borderwidth=5,height=350,width=500,bg=backgrounds['indoor']['bgColor'])
        self.battleFrame.grid(row=0,column=0,sticky=W+E+N+S)
        self.battleCanvas = Canvas(self.battleFrame,width=480,height=350)
        self.battleCanvas.pack()
        self.backgroundPilImage = Image.open(backgrounds['indoor']['filePath'])
        self.backgroundPilImage = self.backgroundPilImage.resize((500,355))
        self.background = ImageTk.PhotoImage(self.backgroundPilImage)
        self.backgroundImage = self.battleCanvas.create_image(0,0,image=self.background,anchor=NW,tags=('background-indoor','background','indoor'))

        self.pokedexFrame = Frame(master,relief=SUNKEN,borderwidth=5,height=700,width=500,bg='grey')
        self.pokedexFrame.grid(row=0,column=1,rowspan=3,sticky=W+E+N+S)
        self.screenFrame = Frame(self.pokedexFrame,relief=SUNKEN,borderwidth=5,height=500,width=400,bg='light grey')
        self.screenFrame.place(x=245,y=50,anchor=N)
        self.tabletCanvas = Canvas(self.screenFrame,width=380,height=500,bg='light grey')
        self.tabletCanvas.pack()

        self.DPPtFont = font.Font(family='Pokemon DPPt',size=26)
        self.DPPtFont2 = font.Font(family='Pokemon DPPt',size=24)
        self.buttonFont = font.Font(family='Pokemon DPPt',size=19)
        self.battleFont = font.Font(family='Pokemon DPPt',size=26,weight="bold")
        self.HPFont = font.Font(family='Pokemon DPPt',size=15,weight="bold")
        self.LevelFont = font.Font(family='Pokemon DPPt',size=18,weight="bold")
        self.HPNameFont = font.Font(family='Pokemon DPPt',size=18,weight="bold")
        self.LevelFontB = font.Font(family='Pokemon DPPt',size=16,weight="bold")
        self.tabletFont = font.Font(family='Pokemon DPPt',size=13,weight="bold")
        self.smallTabletFont = font.Font(family='Pokemon DPPt',size=12,weight="bold")

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

        self.buttonFrame = Frame(master,height=186,width=500,bg='light grey',relief=RAISED,bd=5)
        self.buttonFrame.grid(row=2,column=0,sticky=W+E+N+S)
        self.tBoxPointer = 0
        self.tBox = {
            '0' : self.textBox0,
            '1' : self.textBox1,
            '2' : self.textBox2
            }
        self.initResources()
        
#------------------------------------------------------------------------------------------------------------------------------#

    def tabletGreySlide(self,loop=0): ##this is for adding the grey slider that slides across the screen whenever the user refreshes the tablet.
        if loop == 0:
            if self.tabletCurrentlyGreySlide:
                return
            self.tabletCurrentlyGreySlide = True
            self.tabletCanvas.create_rectangle(0,0,380,500,fill='grey',outline='light grey',tags=('tablet-grey-slide'))
            master.after(5,genFunc(self.tabletGreySlide,1))
        elif 1 <= loop < 50:
            self.tabletCanvas.move('tablet-grey-slide',0,10) ##move it 10 pxls down
            self.tabletCanvas.lift('tablet-grey-slide') ##move it to be above all other items.
            master.after(10,genFunc(self.tabletGreySlide,loop+1)) ##next in loop after 10 ms
        elif loop == 50:
            self.tabletCurrentlyGreySlide = False ##fin
            self.tabletCanvas.delete('tablet-grey-slide') ##delete it

        ##tablet stuff
    def tablet_displayEnemyPokemon(self,pkmn):
        ## important
        ##at some point add HP remaining and stats
        ## endimportant
        
        #if not self.tabletCurrentlyGreySlide: ##can't slide if you're already sliding
        #    self.tabletGreySlide()
        #else:
        #    return ##if we're already sliding then we already have a data req so don't want to be updating. 

        self.tabletCanvas.delete('tablet-data')
        #self.tab_pokemonData = self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)]
        self.tab_pokemonData = pkmn
        self.tabletCanvas.create_rectangle([115,10,270,160],fill=typeColor[self.tab_pokemonData.types[0]],width=3,outline='black',stipple='gray25',tags=('tablet-data'))
        self.tab_pokemonImage = Image.open(pokemon[self.tab_pokemonData.name])
        self.tab_pokemonImage = ImageTk.PhotoImage(self.tab_pokemonImage.resize((141,141)))
        self.tabletCanvas.create_image(190,80,image=self.tab_pokemonImage,tags=('tablet-data','pokemon-photo'))

        self.tabletCanvas.create_text(20,180,text='Pokemon Species: ' + self.tab_pokemonData.species,font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-pokemon-species'))
        self.tabletCanvas.create_text(20,200,text='Pokemon Level: ' + str(self.tab_pokemonData.level),font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-pokemon-level'))
        self.tabletCanvas.create_text(20,220,text='Types: ' + self.tab_pokemonData.types[0]+'/'+self.tab_pokemonData.types[1],font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-pokemon-types'))
        self.tabletCanvas.create_text(20,240,text='Current HP: ' + str(self.tab_pokemonData.hp) + '/' + str(self.tab_pokemonData.stats[0]),font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-pokemon-hp'))
        self.tabletCanvas.create_text(20,260,text='Stats: ' + str(self.tab_pokemonData.stats),font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-pokemon-stats'))
        self.tabletCanvas.create_text(20,280,text='Moves: ',font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-pokemon-moves'))
        moves = self.tab_pokemonData.moves
        count = 0
        for move in moves:
            x = move[0]
            desc = '(' + x.type + ') ' + x.name + ' (' +x.category + '): ' + x.description
            desc = self.getUsableDesc(desc)
            first = -20
            for phrase in desc:
                self.tabletCanvas.create_text(40+first,300+count*20,text=phrase,font=self.smallTabletFont,anchor=W,tags=('tablet-data','tablet-pokemon-moves-'+str(count)))
                first = 0
                count += 1

    def tablet_displayMove(self,move):
        #if not self.tabletCurrentlyGreySlide:
        #    self.tabletGreySlide()
        #else:
        #    return ##as above
        self.tabletCanvas.delete('tablet-data')
        self.tabletCanvas.create_rectangle([120,50,260,190],fill=typeColor[move.type],width=3,outline='black',stipple='gray25',tags=('tablet-data'))
        ## hiya ben!!!!!!!!!
        ## at least future ben or something
        ## idek
        ## eithe rway
        ## when you can be bothered can you add a type icon to be put in the move box? like a fist or smth for fighting
        ## idek i'm really not picky
        ## it could be a dalek
        ## oh well that's it
        ## ty
        desc = self.getUsableDesc(move.description)
        self.tabletCanvas.create_text(20,210,text='Description: ',font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-move-description'))
        count = 0
        for x in desc:
            self.tabletCanvas.create_text(40,240+count*30,text=x,font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-move-description'))
            count += 1
        self.tabletCanvas.create_text(20,240+count*30,text='Type: ' + move.type,font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-move-type'))
        self.tabletCanvas.create_text(20,270+count*30,text='Category: ' + move.category,font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-move-type'))
        if move.category != 'Status':
            self.tabletCanvas.create_text(20,300+count*30,text='Power: ' + str(move.power),font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-move-power'))
            count += 1
        if move.accuracy == 900:
            a = '--'
        else:
            a = str(move.accuracy)
        self.tabletCanvas.create_text(20,300+count*30,text = 'Accuracy: ' + a,font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-move-accuracy'))
    def getUsableDesc(self,desc):
        res = []
        desc = desc.split(' ')
        temp = desc[0]
        del desc[0]
        for word in desc:
            if len(temp+word) > 55:
                res.append(temp)
                temp = word
            else:
                temp += ' '+word
        if temp != '':
            res.append(temp)
        return res
#------------------------------------------------------------------------------------------------------------------------------#
        ##button stuff

    def loadButtonsFirstTime(self):
        self.moveButtons = []
        for count in range(4):
            self.moveButtons.append(Button(self.buttonFrame,bg='white',text=' ',width=12,height=4,cursor='hand2',font=self.buttonFont,state=DISABLED))
            self.moveButtons[-1].place(x=124*count,y=0,anchor="nw")
        self.switchButtons = []
        self.switchButtonsImages = []
        for count in range(6):
            temp = icons[str(arena.getUserSpecies(str(count)))]
            self.switchButtonsImages.append(Image.open(temp))
            self.switchButtonsImages[-1] = ImageTk.PhotoImage(self.switchButtonsImages[-1].resize((60,41)))
            self.switchButtons.append(Button(self.buttonFrame,height=60,width=76,cursor='hand2',state=DISABLED,bg='white',image=self.switchButtonsImages[-1]))
            self.switchButtons[-1].place(x=82*count,y=110,anchor="nw")

    def updateButtons(self):
        count = 0
        self.runText('Please select your choice!')
        for move in self.arena.returnUsefulMoveInfo(self.arena.userTrainer):
            temp = move[0].upper()
            if len(temp) > 9:
                print(temp)
                temp = temp.split(' ')
                newTemp = ''
                for x in range(0,len(temp)):
                    if x == len(temp)-1:
                        newTemp += temp[x]
                    else:
                        newTemp += temp[x] + '\n'
                temp = newTemp
            k = genFunc(self.receiveUserInput, ['attack',count,'user'])
            self.moveButtons[count].config(text=temp,bg=typeColor[move[1]],state=ACTIVE,command=k)
            k = genFunc(self.tablet_displayMove,self.arena.userTrainer.team[str(self.arena.userTrainer.active)].moves[count][0])
            self.moveButtons[count].bind('<Enter>',k)
            #self.moveButtons[count].flash()
            #self.buttons[-1].grid(row=0,column=count,sticky="WENS")
            #self.buttons[-1].place(x=123*count,y=0,anchor="nw")
            count += 1
        count = 0
        for button in self.switchButtons:
            if arena.userTrainer.team[str(count)] != None:
                k = genFunc(self.tablet_displayEnemyPokemon,arena.userTrainer.team[str(count)])
                button.bind('<Enter>',k)
                if arena.userTrainer.team[str(count)].fainted == False and count != arena.userTrainer.active:
                    k = genFunc(self.receiveUserInput, ['switch',count,'user'])
                    button.config(state=ACTIVE,command=k)
                elif arena.userTrainer.team[str(count)].fainted == True:
                    button.config(cursor='arrow')
                else:
                    button.config(cursor='arrow')
            count += 1
        master.update()

    def EOTSwitchButtons(self): ##these are used if a pokemon faints. User must switch in at end of turn.
        self.taskFinished = False
        count = 0
        for button in self.switchButtons:
            if count != arena.userTrainer.active and arena.userTrainer.team[str(count)] != None:
                k = genFunc(self.arena.setUserSwitch,count)
                button.config(state=ACTIVE,command=k)
        self.taskFinished = True

    def disableButtons(self):
        for count in range(4):
            self.moveButtons[count].config(state=DISABLED,command=Pass)
        for count in range(6):
            self.switchButtons[count].config(state=DISABLED,command=Pass)

    def receiveUserInput(self,userInput):
        self.disableButtons()
        if userInput[0] == 'attack':
            userInput[1] = self.arena.userTrainer.team[str(self.arena.userTrainer.active)].moves[userInput[1]][0]
        userInput = tuple(userInput)
        enemyInput = random.choice(['attack'])
        if enemyInput == 'attack':
            move = random.randint(0,3)
            enemyInput = ('attack',self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].moves[move][0],'enemy')
        elif enemyInput == 'switch':
            for index in range(6):
                if self.arena.enemyTrainer.team[str(index)] != None and index != self.arena.enemyTrainer.active:
                    if not self.arena.enemyTrainer.team[str(index)].fainted:
                        enemyInput = ('switch',index,'enemy')
        print(userInput)
        self.arena.processTurn(userInput,enemyInput)
#------------------------------------------------------------------------------------------------------------------------------#
# The following are functions pertaining to the initialize of battles

    def initResources(self):
        self.loadButtonsFirstTime()
        self.scrollPlatforms()

    ## FLOW FOR OPENING:
    ## Platforms scroll on screen. When finished, scrollPlatforms calls checker
    ## the firstSendOutChecker will make sure the trainer anim has finished before playing the anim for the first pokemon
    ## then play anim for user
    ## These functions are also used across different parts of the program- i.e. enemy pokemon send out is used
        ## whenever a Pokemon switches or another is knocked out.

    def scrollPlatforms(self,init=1):
        if init:
            ##First initialize the sprites for the trainers and the platforms.
            ##Trainers initialized after platforms so that they show up on top.
            ##Sprites are resized so that they appear better
            
            self.enemyPlatformImageFile = Image.open(assets['indoor-enemy'])
            self.enemyPlatformImageFile = self.enemyPlatformImageFile.resize((225,75))
            self.enemyPlatformImageFile = ImageTk.PhotoImage(self.enemyPlatformImageFile)
            self.enemyPlatform = self.battleCanvas.create_image(650,175,image=self.enemyPlatformImageFile,tags=('platform','enemy-platform'))
            
            self.enemyTrainerSpriteFile = Image.open(trainerSprites[self.arena.enemyTrainer.sprite]) ##inits the gif file we will use later
            self.enemyTrainerSprite = ImageTk.PhotoImage(self.enemyTrainerSpriteFile.resize((141,141)))
            self.enemyTrainer = self.battleCanvas.create_image(650,175,image=self.enemyTrainerSprite,anchor=S,tags=("enemy-trainer"))

            self.userPlatformImageFile = Image.open(assets['indoor-user'])
            self.userPlatformImageFile = self.userPlatformImageFile.resize((325,40))
            self.userPlatformImageFile = ImageTk.PhotoImage(self.userPlatformImageFile)
            self.userPlatform = self.battleCanvas.create_image(-300,360,image=self.userPlatformImageFile,anchor=SW,tags=('platform','user-platform'))

            self.userTrainerSpriteFile = Image.open(trainerBackSprites[self.arena.userTrainer.sprite])
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
                self.runText('You have been challenged by ' + self.arena.enemyTrainer.trainerClass + ' ' + self.arena.enemyTrainer.name + '!')
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
            self.runText(self.arena.enemyTrainer.trainerClass + ' ' + self.arena.enemyTrainer.name + ' sent out ' + self.arena.findActiveName(self.arena.enemyTrainer) + '!')
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
        self.taskFinished = False
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
            self.EpokemonImageFile = Image.open(pokemon[self.arena.findActiveName(self.arena.enemyTrainer)])
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
                print(ready)
                self.EpokemonImageFile.seek(ready-140-2)
                self.EpokemonImage = ImageTk.PhotoImage(self.EpokemonImageFile.resize((141,141)))
                self.battleCanvas.create_image(350,180,anchor=S,image=self.EpokemonImage,tags=('enemy-pokemon'))
                master.after(250,self.moveInEnemyHPBar) ##moves in the enemy's HP
                return

    def moveInEnemyHPBar(self,tick=0):
        if tick == 0: ##first load up the image
            ##ENDING COORDS (anchor=W) are (-30,90), starts at (-250,90)
            #self.useMove('fire','enemy')
            #return
            self.enemyInfo = (self.arena.getEnemyHP(),self.arena.getEnemyLevel())
            self.EnemyHPBar = Image.open(assets['EnemyHP'])
            self.EnemyHPBar = ImageTk.PhotoImage(self.EnemyHPBar.resize((242,70)))
            self.battleCanvas.create_image(-250,90,anchor=W,image=self.EnemyHPBar,tags=('enemy-hp'))
            self.battleCanvas.create_text(-120,83,anchor=W,text='Lv ' + str(self.enemyInfo[1]),
                                          tags=('enemy-hp','enemy-level'),font=self.LevelFont,fill='#474747')
            self.battleCanvas.create_text(-184,105,anchor=E,text=str(self.enemyInfo[0][0])+'/'+str(self.enemyInfo[0][1]),
                                          fill='#474747',font=self.HPFont,tags=('enemy-hp','enemy-hp-hp'))
            self.EnemyHPRaw = Image.open(assets['greenBar'])
            self.EnemyHP = ImageTk.PhotoImage(self.EnemyHPRaw.resize((96,5)))
            self.printedEnemyHP = self.enemyInfo[0][0]
            self.EnemyMaxHP = self.enemyInfo[0][1]
            self.battleCanvas.create_image(-150,104,anchor=NW,image=self.EnemyHP,tags=('enemy-hp','enemy-hp-bar'))
            self.battleCanvas.create_text(-230,83,anchor=W,text=self.arena.findActiveName(self.arena.enemyTrainer).upper(),fill='#474747',font=self.HPNameFont,tags=('enemy-hp','enemy-hp-name'))
            
            if self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].statusCondition != None:
                j = self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].status
                self.enemyStatusConditionImage = ImageTk.PhotoImage(Image.open('assets/status-conditions/'+j+'.png').resize((35,14)))
                self.battleCanvas.create_image(192-250,87,image=self.enemyStatusConditionImage,tags=('enemy-hp'))
            k = genFunc(self.moveInEnemyHPBar,tick+1)
            master.after(5,k)

        else: ##replace if True with else when rejoining
            self.battleCanvas.move('enemy-hp',5,0)
            master.update()
            if tick < 50: ##move everything 10px per tick
                k = genFunc(self.moveInEnemyHPBar,tick+1)
                master.after(5,k)
            else:
                self.taskFinished = True
                self.processesComplete += 1
                if self.battleStart:
                    master.after(5,self.moveUserTrainerOffscreen)

    def moveUserTrainerOffscreen(self,count=1):
        if count == 1:
            self.runText('Go! %s!' % self.arena.findUserActive())
        if count % 5 == 0: ##this is to allow there to be some movement in between the movement of the trainer and the sprite updates
            try:
                self.userTrainerSpriteFile.seek(int(count/5))
                coords = self.battleCanvas.coords('user-trainer')
                self.battleCanvas.delete('user-trainer')
                self.userTrainerSprite = ImageTk.PhotoImage(self.userTrainerSpriteFile.resize((180,180)))
                self.battleCanvas.create_image(coords[0],coords[1],image=self.userTrainerSprite,anchor=SW,tags=('user-trainer'))
                if count == 15:
                    self.throwStartPokeball()
            except EOFError:
                pass
        self.battleCanvas.move('user-trainer',-2,0)
        k = genFunc(self.moveUserTrainerOffscreen,count+1)
        master.after(20,k)

    def throwStartPokeball(self,count=0):
        if count == 0:
            self.taskFinished = False
            self.userPokeballImageFile = Image.open(throwpokeballs['Pokeball'])
            self.userPokeballImage = ImageTk.PhotoImage(self.userPokeballImageFile.resize((25,25)))
            self.battleCanvas.create_image(147,258,image=self.userPokeballImage,tags=('user-pokeball'))
            k = genFunc(self.throwStartPokeball,count+1)
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
            k = genFunc(self.throwStartPokeball,count+1)
            master.after(50,k)
        elif count == 16:
            self.battleCanvas.delete('user-pokeball')
            self.userPokemonAnim()
            return

    def userPokemonAnim(self,count=0):
        if count == 0:
            self.userPokemonSpriteFile = Image.open(pokemonBackSprites[self.arena.findUserActive()])
            self.userPokemonSprite = ImageTk.PhotoImage(self.userPokemonSpriteFile.resize((1,1)))
            self.battleCanvas.create_image(140,360,image=self.userPokemonSprite,anchor=S,tags=('user-pokemon'))
            k = genFunc(self.userPokemonAnim,count+1)
            master.after(10,k)
        elif count > 0 and count <= 100:
            self.userPokemonSprite = ImageTk.PhotoImage(self.userPokemonSpriteFile.resize((int(math.log(count)/math.log(100)*179+1),int(math.log(count)/math.log(100)*179+1))))
            self.battleCanvas.delete('user-pokemon')
            self.battleCanvas.create_image(140,360,image=self.userPokemonSprite,anchor=S,tags=('user-pokemon'))
            k = genFunc(self.userPokemonAnim,count+1)
            master.after(8,k)
        elif count > 100 and count <= 130:
            self.battleCanvas.move('user-pokemon',(-1) ** count * 15,0)
            k = genFunc(self.userPokemonAnim,count+1)
            master.after(int(125*math.log(count-100)/math.log(30)),k)
        elif count == 131:
            self.moveInUserHPBar()

    def moveInUserHPBar(self,tick=0): ##this function moves all of the user's HP bar elements (the green/yellow/red
                                      ## HP bar, the text displaying HP, and the name of the Pokemon into view)
        if tick == 0:
            ##finish main bar at x = 482, y = 275
            self.userInfo = (self.arena.getUserHP(),self.arena.getUserLevel(),self.arena.findActiveName(self.arena.userTrainer).upper())
            try: ##this is so that I do not need to reload the graphic whenever I update this
                self.UserHPBar
            except:
                self.UserHPBar = Image.open(assets['UserHP'])
                self.UserHPBar = ImageTk.PhotoImage(self.UserHPBar.resize((223,81)))
            self.battleCanvas.create_image(712,275,anchor=E,image=self.UserHPBar,tags=('user-hp'))
            self.battleCanvas.create_text(695,260,anchor=E,font=self.LevelFont,fill='#474747',
                                          text='Lv '+str(self.userInfo[1]),tags=('user-hp','user-level'))
            self.battleCanvas.create_text(625,260,anchor=E,font=self.HPNameFont,fill='#474747',
                                          text=self.userInfo[2],tags=('user-hp','user-hp-name'))
            self.battleCanvas.create_text(635,294,anchor=E,font=self.HPFont,fill='#474747',
                                          text=self.userInfo[0][0],tags=('user-hp','user-hp-hp'))
            self.battleCanvas.create_text(690,294,anchor=E,font=self.HPFont,fill='#474747',
                                          text=self.userInfo[0][1],tags=('user-hp','user-hp-max'))
            self.printedUserHP = self.userInfo[0][0]
            self.UserMaxHP = self.userInfo[0][1]
            if 0.2 <= self.printedUserHP/self.UserMaxHP <= 0.5:
                self.UserHPRaw = Image.open(assets['yellowBar'])
            elif self.printedUserHP/self.UserMaxHP < 0.2:
                self.UserHPRaw = Image.open(assets['redBar'])
            elif self.printedUserHP/self.UserMaxHP > 0.5 :
                self.UserHPRaw = Image.open(assets['greenBar'])
            self.lastRatio = self.printedUserHP / self.UserMaxHP
            self.UserHP = ImageTk.PhotoImage(self.UserHPRaw.resize((int(self.printedUserHP/self.UserMaxHP*83)+1,5)))
            self.battleCanvas.create_image(615,278,anchor=NW,image=self.UserHP,tags=('user-hp','user-hp-bar'))
            self.UserMaxHP = self.userInfo[0][1]
            self.printedUserHP = self.userInfo[0][0]
            if self.arena.userTrainer.team[str(self.arena.userTrainer.active)].statusCondition != None:
                j = self.arena.userTrainer.team[str(self.arena.userTrainer.active)].statusCondition
                self.userStatusConditionImage = ImageTk.PhotoImage(Image.open('assets/status-conditions/'+j+'.png').resize((40,16)))
                self.battleCanvas.create_image(340+225,292,image=self.userStatusConditionImage,tags=('user-hp'))
            k = genFunc(self.moveInUserHPBar,1)
            master.after(5,k)
        else:
            if tick < 46:
                self.battleCanvas.move('user-hp',-5,0)
                k = genFunc(self.moveInUserHPBar,tick+1)
                master.after(5,k)
            else:
                if self.battleStart:
                    self.updateButtons()
                self.battleStart = False
                self.taskFinished = True
                self.processesComplete += 1
                #self.arena.processTurn(('attack',self.arena.findUserPokemon().moves[0][0],'user'),('switch',2,'enemy'))
                
        ##REFERENCE: finish userPlatform at (0,360) and enemyPlatform at (350,175)


#------------------------------------------------------------------------------------------------------------------------------#
##Modifications on the pokemon in play
##ex. fainting

    def userPokemonFaint(self,count=0):
        if count == 0:
            self.taskFinished = False
            self.runText(self.arena.findActiveName(self.arena.userTrainer) + " fainted!")
            k = genFunc(self.userPokemonFaint,count+1)
            master.after(1,k)
            self.moveOutUserHPBar()
        elif count > 0 and count <=45:
            self.battleCanvas.move('user-pokemon',0,4)
            k = genFunc(self.userPokemonFaint,count+1)
            master.after(5,k)
        elif count == 46:
            self.battleCanvas.delete('user-pokemon')
            self.taskFinished = True

    def enemyPokemonFaint(self,count=0):
        if count == 0:
            self.taskFinished = False
            self.runText("Foe's " + self.arena.findActiveName(self.arena.enemyTrainer) + " fainted!")
            k = genFunc(self.enemyPokemonFaint,count+1)
            self.EpokemonImageFile = self.EpokemonImageFile.resize((141,141))
            self.EpokemonImageFile = self.EpokemonImageFile.convert('RGBA')
            master.after(1,k)
            self.moveOutEnemyHPBar()
        if count > 0 and count <= 150:
            size = self.EpokemonImageFile.size
            self.EpokemonImageFile = self.EpokemonImageFile.crop((0,0,size[0],size[1]-4))
            self.EpokemonImage = ImageTk.PhotoImage(self.EpokemonImageFile)
            self.battleCanvas.delete('enemy-pokemon')
            self.battleCanvas.create_image(350,180,image=self.EpokemonImage,anchor=S,tags=('enemy-pokemon'))
            k = genFunc(self.enemyPokemonFaint,count+1)
            master.after(5,k)
        elif count == 151:
            self.battleCanvas.delete('enemy-pokemon')
            self.taskFinihsed = True

    ##MOVE FUNCTION
    ##I could have merged HPUpdateUser and HPUpdateEnemy, but it was simpler to have them separate.
    def HPUpdateEnemy(self,newHP,start=1,flashing=0):
        if start:
            self.taskFinished = False
            self.lastRatio = self.printedEnemyHP / self.EnemyMaxHP ##save original HP ratio
            if self.printedEnemyHP < newHP:
                k = genFunc(self.HPUpdateEnemy,newHP,0,15) ##if we are restoring HP, we skip flashing
            else:
                k = genFunc(self.HPUpdateEnemy,newHP,0,1)
                master.after(5,k)
        elif flashing%2==1 and flashing < 9:
            self.battleCanvas.delete('enemy-pokemon')
            k = genFunc(self.HPUpdateEnemy,newHP,0,flashing+1)
            master.after(50,k)
        elif flashing%2==0 and flashing < 9:
            self.battleCanvas.create_image(350,180,anchor=S,image=self.EpokemonImage,tags=('enemy-pokemon'))
            k = genFunc(self.HPUpdateEnemy,newHP,0,flashing+1)
            master.after(100,k)
        else:
            if self.printedEnemyHP > newHP: ##these if/elif/else are used for determining whether we are increasing
                                            ##decreasing or done
                self.printedEnemyHP -= 1
            elif self.printedEnemyHP < newHP:
                self.printedEnemyHP += 1
            else:
                self.taskFinished = True
                self.processesComplete += 1
                return
            self.battleCanvas.delete('enemy-hp-bar')
            self.battleCanvas.delete('enemy-hp-hp')
            if self.printedEnemyHP/self.EnemyMaxHP < 0.5 and self.lastRatio >= 0.5: ##these if/elif/elif are used for
                                                                                    ##changing HP bar color
                self.EnemyHPRaw = Image.open(assets['yellowBar'])
            elif self.printedEnemyHP/self.EnemyMaxHP < 0.2 and self.lastRatio >= 0.2:
                self.EnemyHPRaw = Image.open(assets['redBar'])
            elif self.printedEnemyHP/self.EnemyMaxHP >= 0.2 and self.lastRatio < 0.2:
                self.EnemyHPRaw = Image.open(assets['yellowBar'])
            elif self.printedEnemyHP/self.EnemyMaxHP >= 0.5 and self.lastRatio < 0.5:
                self.EnemyHPRaw = Image.open(assets['greenBar'])
            self.lastRatio = self.printedEnemyHP / self.EnemyMaxHP
            self.EnemyHP = ImageTk.PhotoImage(self.EnemyHPRaw.resize((int(self.lastRatio*96)+1,6)))
            self.battleCanvas.create_image(100,104,anchor=NW,image=self.EnemyHP,tags=('enemy-hp','enemy-hp-bar'))
            self.battleCanvas.create_text(66,105,anchor=E,text=str(self.printedEnemyHP)+'/'+str(self.EnemyMaxHP),
                                                                   fill='#474747',font=self.HPFont,tags=('enemy-hp','enemy-hp-hp'))
            k = genFunc(self.HPUpdateEnemy,newHP,0,flashing)
            master.after(20,k)

    def HPUpdateUser(self,newHP,start=1,flashing=0):
        if start:
            self.taskFinished = False
            self.lastRatio = self.printedUserHP /self.UserMaxHP
            if self.printedUserHP < newHP:
                k = genFunc(self.HPUpdateUser,newHP,0,15) ##if we are restoring HP, we skip flashing
                master.after(5,k)
            else:
                k = genFunc(self.HPUpdateUser,newHP,0,1)
                master.after(5,k)
        elif flashing%2==1 and flashing < 9:
            self.battleCanvas.delete('user-pokemon')
            k = genFunc(self.HPUpdateUser,newHP,0,flashing+1) ##flashing is responsible for, well, the Pokemon flashing
                                    ##after taking damage. It flip flops between this elif and the one below
                                    ##until flashing is 14 then it goes to the else- which controls the HP bar thing
            master.after(100,k)
        elif flashing%2==0 and flashing < 9:
            self.battleCanvas.create_image(140,360,anchor=S,image=self.userPokemonSprite,tags=('user-pokemon'))
            k = genFunc(self.HPUpdateUser,newHP,0,flashing+1)
            master.after(100,k)
        else:
            if self.printedUserHP > newHP:
                self.printedUserHP -= 1
            elif self.printedUserHP < newHP:
                self.printedUserHP += 1
            else:
                self.taskFinished = True
                self.processesComplete += 1
                return
            self.battleCanvas.delete('user-hp-bar')
            self.battleCanvas.delete('user-hp-hp')
            if self.printedUserHP/self.UserMaxHP < 0.5 and self.lastRatio >= 0.5:
                self.UserHPRaw = Image.open(assets['yellowBar'])
            elif self.printedUserHP/self.UserMaxHP < 0.2 and self.lastRatio >= 0.2:
                self.UserHPRaw = Image.open(assets['redBar'])
            elif self.printedUserHP/self.UserMaxHP >= 0.2 and self.lastRatio < 0.2:
                self.UserHPRaw = Image.open(assets['yellowBar'])
            elif self.printedUserHP/self.UserMaxHP >= 0.5 and self.lastRatio < 0.5:
                self.UserHPRaw = Image.open(assets['greenBar'])
            self.lastRatio = self.printedUserHP / self.UserMaxHP
            self.UserHP = ImageTk.PhotoImage(self.UserHPRaw.resize((int(self.lastRatio*83)+1,5)))
            self.battleCanvas.create_image(390,278,anchor=NW,image=self.UserHP,tags=('user-hp','user-hp-bar'))
            self.battleCanvas.create_text(405,294,anchor=E,font=self.HPFont,text=str(self.printedUserHP),
                                           tags=('user-hp','user-hp-hp'),fill='#474747')
            k = genFunc(self.HPUpdateUser,newHP,0,15)
            master.after(20,k)

    def moveOutUserHPBar(self,tick=0):
        if tick < 46:
            self.battleCanvas.move('user-hp',5,0)
            k = genFunc(self.moveOutUserHPBar,tick+1)
            master.after(2,k)
        else:
            self.processesComplete += 1

    def moveOutEnemyHPBar(self,tick=0):
        if tick < 50:
            self.battleCanvas.move('enemy-hp',-5,0)
            k = genFunc(self.moveOutEnemyHPBar,tick+1)
            master.after(2,k)
        else:
            self.processesComplete += 1
            self.taskFinished = True

    def switchEnemy(self,tick=0,count=0): ##tick refers to pokeball and pokemon,
                                            ##count is for the sprite anim and things
        if tick == 0:
            self.taskFinished = False
            self.EpokeballImageFile = Image.open(pokeballs['Pokeball'])
            self.EpokeballImageFile.seek(2)
            k = genFunc(self.switchEnemy,tick+1)
            master.after(5,k)
        elif 1 <= tick <= 96:
            self.EpokeballImage = self.EpokeballImageFile.resize((int(23*tick/96+1),int(35*tick/96+1)))
            self.EpokeballImage = ImageTk.PhotoImage(self.EpokeballImage)
            self.battleCanvas.delete('enemy-pokeball')
            self.battleCanvas.create_image(350,175,anchor=S,image=self.EpokeballImage,tags=('enemy-pokeball'))

            self.EpokemonImage = ImageTk.PhotoImage(self.EpokemonImageFile.resize((int(1+(100-tick)/100*141),int(1+(100-tick)/100*141))))
            self.battleCanvas.delete('enemy-pokemon')
            self.battleCanvas.create_image(350,180,anchor=S,image=self.EpokemonImage,tags=('enemy-pokemon'))

            k = genFunc(self.switchEnemy,tick+1)
            master.after(2,k)
        elif tick == 97:
            self.battleCanvas.delete('enemy-pokemon')
            k = genFunc(self.switchEnemy,tick+1,1)
            master.after(5,k)
        elif count <= 3 and tick == 98:
            self.EpokeballImageFile.seek(3-count)
            self.EpokeballImage = ImageTk.PhotoImage(self.EpokeballImageFile.resize((24,35)))
            self.battleCanvas.delete('enemy-pokeball')
            self.battleCanvas.create_image(350,175,image=self.EpokeballImage,anchor=S,tags=('enemy-pokeball'))
            k = genFunc(self.switchEnemy,tick,count+1)
            master.after(250,k)
        elif 3 < count < 40:
            t = (int(math.log(40-count)/math.log(40)*24)+1,int(math.log(40-count)/math.log(40)*35)+1)
            self.EpokeballImage = self.EpokeballImageFile.resize(t)
            self.EpokeballImage = ImageTk.PhotoImage(self.EpokeballImage)
            self.battleCanvas.delete('enemy-pokeball')
            self.battleCanvas.create_image(350,175,image=self.EpokeballImage,anchor=S,tags=('enemy-pokeball'))
            master.update()
            k = genFunc(self.switchEnemy,tick,count+1)
            master.after(5,k)
        elif count == 40:
            self.battleCanvas.delete('enemy-pokeball')
            self.moveOutEnemyHPBar()

    def switchUser(self,tick=0):
        if tick == 0:
            self.taskFinished = False
            self.moveOutUserHPBar()
            k = genFunc(self.switchUser,1)
            master.after(5,k)
        elif tick < 50:
            self.userPokemonSprite = ImageTk.PhotoImage(self.userPokemonSpriteFile.resize((int(math.log(50-tick)/math.log(50)*179)+1,int(math.log(50-tick)/math.log(50)*179)+1)))
            self.battleCanvas.delete('user-pokemon')
            self.battleCanvas.create_image(140,360,image=self.userPokemonSprite,anchor=S,tags=('user-pokemon'))
            k = genFunc(self.switchUser,tick+1)
            master.after(8,k)
        else:
            self.taskFinished = True

    def setUserStatus(self):
        j = self.user.enemyTrainer.team[str(self.arena.userTrainer.active)].statusCondition
        self.userStatusConditionImage = ImageTk.PhotoImage(Image.open('assets/status-conditions/'+j+'.png').resize((35,14)))
        self.battleCanvas.create_image(340,292,image=self.userStatusConditionImage,tags=('user-hp','user-status'))
        master.update()

    def setEnemyStatus(self):
        j = self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].status
        self.enemyStatusConditionImage = ImageTk.PhotoImage(Image.open('assets/status-conditions/'+j+'.png').resize((35,14)))
        self.battleCanvas.create_image(192,87,image=self.enemyStatusConditionImage,tags=('enemy-hp'))

    def deleteUserStatus(self):
        self.battleCanvas.delete('user-status')

    def deleteEnemyStatus(self):
        self.battleCanvas.delete('enemy-status')
        
#------------------------------------------------------------------------------------------------------------------------------#
##MOVE ANIMATIONS

    def useMove(self,elementalType,targ,tick=0,leftOffAt=-1):
        self.taskFinished = False
        if tick == 0:
            self.moveU = ''
            self.moveE = ''
            self.delay = 100
            if elementalType.lower() in ['ground']: ##these types have attacks that vary appearance depending on whether they are used on the user or the enemy
                self.moveU = targ
            if elementalType.lower() in ['ground','normal','poison','ice','bug','fighting']:##and these vary based on how they look when they fade out
                self.moveE = 'return'
            if elementalType.lower() in ['dragon','poison','dark','flying','ice','electric','fighting','fire']: ##these moves need to operate faster
                self.delay = 50
                
            if targ == 'enemy': ##specify starting coords
                targ = self.emCenterCoords
                targetArea = 5625*2
                if elementalType.lower() in ['poison','dark','grass']:
                    targetArea = 5625*4
                self.moveOffset = -25
                if elementalType.lower() in ['dark','ice','electric']:
                    self.moveOffset = 0
            elif targ == 'user':
                targ = self.userCenterCoords
                targetArea = 5625*4 ##keeping this like this so its clear
                self.moveOffset = 40
            size = Image.open('assets/attacks/'+elementalType+'/'+elementalType+self.moveU+str(tick)+'.png').size
            self.moveImageScaleFactor = math.sqrt(targetArea/(size[0]*size[1]))
            self.moveImageNewResize = (int(size[0]*self.moveImageScaleFactor),int(size[1]*self.moveImageScaleFactor))

            master.after(5,genFunc(self.useMove,elementalType,targ,tick+1))
            
        elif 0 < tick <= 24: ##place image on screen as it fades in
            self.battleCanvas.delete('move-image')
            self.moveImage = ImageTk.PhotoImage(Image.open('assets/attacks/'+elementalType+'/'+elementalType+self.moveU+str(tick)+'.png').resize(self.moveImageNewResize))
            self.battleCanvas.create_image(targ[0],targ[1]+self.moveOffset,anchor=S,image=self.moveImage,tags=('move-image'))
            master.after(5,genFunc(self.useMove,elementalType,targ,tick+1))
            
        elif 25 <= tick <= 36: ##run the anim
            try:
                self.moveImage = ImageTk.PhotoImage(Image.open('assets/attacks/'+elementalType+'/'+elementalType+self.moveU+'anim'+str(tick-25)+'.png').resize(self.moveImageNewResize))
            except:
                if self.moveE == 'return':
                    master.after(500,genFunc(self.useMove,elementalType,targ,49))
                elif tick-25-1 > 0:
                    master.after(5,genFunc(self.useMove,elementalType,targ,37,tick-25-1))
                else:
                    master.after(5,genFunc(self.usemove,elementalType,targ,49))
                return
            self.battleCanvas.delete('move-image')
            self.battleCanvas.create_image(targ[0],targ[1]+self.moveOffset,image=self.moveImage,anchor=S,tags=('move-image'))
            master.after(self.delay,genFunc(self.useMove,elementalType,targ,tick+1))
            
        elif 37 <= tick <= 48: ##run anim in reverse
            if leftOffAt == -1:
                self.battleCanvas.delete('move-image')
                self.moveImage = ImageTk.PhotoImage(Image.open('assets/attacks/'+elementalType+'/'+elementalType+self.moveU+'anim'+str(44-tick)+'.png').resize(self.moveImageNewResize))
                self.battleCanvas.create_image(targ[0],targ[1]+self.moveOffset,image=self.moveImage,anchor=S,tags=('move-image'))
                master.after(self.delay,genFunc(self.useMove,elementalType,targ,tick+1))
            else:
                self.battleCanvas.delete('move-image')
                self.moveImage = ImageTk.PhotoImage(Image.open('assets/attacks/'+elementalType+'/'+elementalType+self.moveU+'anim'+str(leftOffAt)+'.png').resize(self.moveImageNewResize))
                self.battleCanvas.create_image(targ[0],targ[1]+self.moveOffset,anchor=S,image=self.moveImage,tags=('move-image'))
                if leftOffAt-1 == 0:
                    master.after(self.delay,genFunc(self.useMove,elementalType,targ,49))
                else:
                    master.after(self.delay,genFunc(self.useMove,elementalType,targ,tick,leftOffAt-1))
                    
        elif 48 <= tick <= 67: ##fade out
            self.battleCanvas.delete('move-image')
            self.moveImage = ImageTk.PhotoImage(Image.open('assets/attacks/'+elementalType + '/' + elementalType + self.moveU + self.moveE + str(25-(tick-44))+'.png').resize(self.moveImageNewResize))
            self.battleCanvas.create_image(targ[0],targ[1]+self.moveOffset,anchor=S,image=self.moveImage,tags=('move-image'))
            master.after(5,genFunc(self.useMove,elementalType,targ,tick+1))
            
        elif tick == 68: ##delete the image
            self.battleCanvas.delete('move-image')
            master.update()
            self.taskFinished = True

##    def useMove(self,elementalType,targ,start=True,numMovesSent=0,tick=0):
##        if start:
##            self.taskFinished = False
##            if targ == 'enemy':
##                self.startCenterCoords = self.userCenterCoords
##                self.endCenterCoords = self.emCenterCoords
##            elif targ == 'user':
##                self.startCenterCoords = self.emCenterCoords
##                self.endCenterCoords=self.userCenterCoords
##            else:
##                raise ValueError('Target must be "user" or "enemy".')
##            self.pics = []
##            self.moveImage = Image.open(attacks[elementalType])
##            self.moveImage.resize((100,100))
##            self.moveImage = ImageTk.PhotoImage(self.moveImage)
##            self.pics.append(self.battleCanvas.create_image(self.startCenterCoords[0],self.startCenterCoords[1],image=self.moveImage))
##            self.leftRightCenterDict = {'0':0,'1' : 25,'2':0,'3':-25}
##            self.dx = (self.endCenterCoords[0]-self.startCenterCoords[0])/100
##            self.dy = (self.endCenterCoords[1]-self.startCenterCoords[1])/100
##        remove = []
##        for pic in self.pics:
##            self.battleCanvas.move(pic,self.dx,self.dy)
##            if targ == 'user':
##                if self.battleCanvas.coords(pic)[1] > self.endCenterCoords[1]:
##                    self.battleCanvas.delete(pic)
##                    remove.append(pic)
##            elif targ == 'enemy':
##                if self.battleCanvas.coords(pic)[1] < self.endCenterCoords[1]:
##                    self.battleCanvas.delete(pic)
##                    remove.append(pic)
##        for pic in remove:
##            for n in range(0,len(self.pics)):
##                if self.pics[n] == pic:
##                    del self.pics[n]
##                    break
##        if tick == 12:
##            if numMovesSent < 40:
##                self.battleCanvas.move('user-pokemon',self.leftRightCenterDict[str(numMovesSent%4)]/2.5,0)
##                self.battleCanvas.move('enemy-pokemon',self.leftRightCenterDict[str((numMovesSent+1)%4)]/2.5,0)
##                self.pics.append(self.battleCanvas.create_image(self.startCenterCoords[0]+self.leftRightCenterDict[str(numMovesSent%4)],self.startCenterCoords[1],image=self.moveImage))
##                tick = 0
##                numMovesSent += 1
##        else:
##            tick += 1
##        if self.pics != []:
##            k = genFunc(self.useMove,elementalType,targ,False,numMovesSent,tick)
##            master.after(5,k)
            
                
#------------------------------------------------------------------------------------------------------------------------------#
# The following are functions pertaining to text scrolling across the box at the bottom.

    def runText(self,text):
        self.textRunning = True
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
        self.textRunning = False

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

    def waitingForTaskToFinish(self,func,waitingID=False):
        if not waitingID:
            self.smallestWaiting += 1
            waitingID = self.smallestWaiting
        if self.taskFinished == True and self.smallestWaiting == waitingID:
            master.after(5,func)
        else:
            k = genFunc(self.waiting,func,waitingID)
            master.after(5,k)
            
    def runGif(self,gif,canvasID,count=True):
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

App = app(master,arena)
mainloop()
