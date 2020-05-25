##yo ben wtf is up with stealth rock

from tkinter import *
from PIL import Image, ImageTk
from tkinter import font
import time
import math, threading, random
import random as r
import battle
from pkmnData import *
from playsound import playsound
from pygame import mixer

##Custom Built Modules
import battle
from pkmnData import *

def genFunc(f, *args):
    return lambda *args2: f(*args)

def Pass(event=False):
    return

class menuApp:
    ##This is the class that describes the main menu
    def __init__(self,master):
        self.master = master
        ##these locations for canvas *just* manage to get it to fill the screen
        self.menuCanvas = Canvas(master,bg='black',height=700,width=1000)
        self.menuCanvas.place(x=-2,y=-1)
        master.protocol("WM_DELETE_WINDOW",self.on_closing)

        ##As with all 'app' sections, I specify my main fonts here.
        self.LogoDPPtFont = font.Font(family='Pokemon DPPt',size=100)
        self.MenuDPPtFont = font.Font(family='Pokemon DPPt',size=40)
        self.smallMenuDPPtFont = font.Font(family='Pokemon DPPt',size=20)

        ##This creates the logo source files
        self.menuCanvas.create_text(500,90-120,text='POKEMON HORIZONS',fill='white',font=self.LogoDPPtFont,tags=('main-text'))
        self.logoImageFile = Image.open('assets/menu/logo.png').resize((int(360*1.7),int(100*1.7)))
        self.logoImageFile.putalpha(5) ##sets the fade in on the logo image to allow it to fade in
     
        self.logoImage = ImageTk.PhotoImage(self.logoImageFile) ##Turns the PIL image into a suitable Tkinter image.
        self.menuCanvas.create_image(500,220,image=self.logoImage,tags=('logo')) ##Draws the image to the screen

        ##These time variables are used to ensure that the user does not move the cursor too quickly, as otherwise it looks not-so-good
        self.testingReduceTime=0
        self.timeSinceLastActivation = time.time()

        self.currentMenu = 'main' ##user's current menu
        self.doMovePointer = True ##indicates whether the computer should continue to move the pointer in and out. Set to false if an animation is playing - i.e. buttons moving offscreen
        self.menuDistances = {'main':470,'drafting':610} ##Maximum distance downwards that can be moved in each menu.

        self.pokemonPerRound = 6
        self.numRounds = 2
        self.numBattles = 3

        self.moveDownText() ##plays opening anim for the menu

    def on_closing(self): ##this func closes the menu properly
        mixer.music.stop()
        self.master.destroy()

    def moveDownText(self,loop=0): ##moves the text downwards
        if loop < 120:
            self.menuCanvas.move('main-text',0,1)
            self.master.after(5,genFunc(self.moveDownText,loop+1))
        else:
            self.fadeInLogo()

    def fadeInLogo(self,loop=5): ##fades in the logo (when app launched)
        if loop <= 255:
            self.menuCanvas.delete('logo')
            self.logoImageFile.putalpha(loop)
            self.logoImage = ImageTk.PhotoImage(self.logoImageFile)
            self.menuCanvas.create_image(500,220,image=self.logoImage,tags=('logo'))
            self.master.after(40-int(40*self.testingReduceTime),genFunc(self.fadeInLogo,loop+5))
        else:
            self.initMenu()

    def initMenu(self): ##Places the buttons and sets up the bindings to allow the user to operate the main menu.
        self.menuCanvas.create_text(500,400,text='RANDOM BATTLE',fill='white',font=self.MenuDPPtFont,tags=('random-battle'))
        self.menuCanvas.create_text(500,470,text='START DRAFT',fill='white',font=self.MenuDPPtFont,tags=('start-draft'))
        self.pointerImage = ImageTk.PhotoImage(Image.open('assets/menu/pointer.png'))
        self.menuCanvas.create_image(300,400,image=self.pointerImage,tags=('pointer'))
        self.movePointerInAndOut()
        self.master.bind('<Down>',genFunc(self.movePointerDown))
        self.master.bind('<Up>',genFunc(self.movePointerUp))
        self.master.bind('<Return>',genFunc(self.selectOption))

#-----------------------------------------------------------------------------------------------------------

    def selectOption(self): ##Processes the selection of the button, and plays a relevant sound using threading.
        T = threading.Thread(target=genFunc(playsound,'sounds/select.mp3'))
        T.start()

        ##Need to unbind options or user could select multiple which would cause an error
        self.master.unbind('<Down>')
        self.master.unbind('<Up>')
        self.master.unbind('<Return>')
        self.doMovePointer = False
        if self.currentMenu == 'main':
            if self.menuCanvas.coords('pointer')[1] == 400:
                master.after(100,self.loadRandomBattle)
            elif self.menuCanvas.coords('pointer')[1] == 470:
                master.after(100,self.loadDraftingMenu)
        self.menuCanvas.delete('pointer')

    def movePointerInAndOut(self,flipFlop = 0): ##Moves the pointer left and right in a retro-pokemon style
        if flipFlop == 0 and self.doMovePointer:
            self.menuCanvas.move('pointer',-20,0)
            self.master.after(200,genFunc(self.movePointerInAndOut,1))
        elif self.doMovePointer:
            self.menuCanvas.move('pointer',20,0)
            self.master.after(200,genFunc(self.movePointerInAndOut,0))

    def movePointerDown(self):
        if time.time() - self.timeSinceLastActivation < 0.1:
            return
        self.timeSinceLastActivation = time.time()
        coords = self.menuCanvas.coords('pointer')
        if coords[1] == self.menuDistances[self.currentMenu]:
            self.menuCanvas.move('pointer',0,400-coords[1])
        else:
            self.menuCanvas.move('pointer',0,70)

    def movePointerUp(self):
        if time.time() - self.timeSinceLastActivation < 0.1:
            return
        self.timeSinceLastActivation = time.time()
        coords = self.menuCanvas.coords('pointer')
        if coords[1] == 400:
            self.menuCanvas.move('pointer',0, self.menuDistances[self.currentMenu] - coords[1])
        else:
            self.menuCanvas.move('pointer',0,-70)

#-----------------------------------------------------------------------------------------------------------#
            
    def loadDraftingMenu(self,count=0): ##Uses the simple recursive-esque style that I use throughout the rest of my program
        if count == 0:
            self.master.after(5,genFunc(self.loadDraftingMenu,1))
        elif count%2 == 1 and count < 9:
            self.menuCanvas.delete('start-draft')
            self.master.after(200,genFunc(self.loadDraftingMenu,count+1))
        elif count%2 == 0 and count < 9:
            self.menuCanvas.create_text(500,470,text='START DRAFT',fill='white',font=self.MenuDPPtFont,tags=('start-draft'))
            self.master.after(200,genFunc(self.loadDraftingMenu,count+1))
        elif 9 <= count <= 73:
            self.menuCanvas.move('random-battle',0,5)
            self.menuCanvas.move('start-draft',0,5)
            master.after(10,genFunc(self.loadDraftingMenu,count+1))
        elif 74 == count:
            self.menuCanvas.delete('random-battle')
            self.menuCanvas.delete('start-draft')
            self.menuCanvas.create_text(500,400+325,text='-  Number of Rounds: 2  +',fill='white',font=self.MenuDPPtFont,tags=('numRounds'))
            self.menuCanvas.create_text(500,470+325,text='-  Pokemon Per Round: 6   ',fill='white',font=self.MenuDPPtFont,tags=('pokemonPerRound'))
            self.menuCanvas.create_text(500,540+325,text='-  Number of Battles: 3  +',fill='white',font=self.MenuDPPtFont,tags=('numBattles'))
            self.menuCanvas.create_text(500,610+325,text='START DRAFT',fill='White',font=self.MenuDPPtFont,tags=('start-draft'))
            master.after(10,genFunc(self.loadDraftingMenu,count+1))
        elif 75 <= count <= 139:
            self.menuCanvas.move('numRounds',0,-5)
            self.menuCanvas.move('pokemonPerRound',0,-5)
            self.menuCanvas.move('numBattles',0,-5)
            self.menuCanvas.move('start-draft',0,-5)
            master.after(10,genFunc(self.loadDraftingMenu,count+1))
        elif 140 == count:
            self.menuCanvas.create_image(200,400,image=self.pointerImage,tags=('pointer'))
            self.doMovePointer = True
            self.movePointerInAndOut()
            self.currentMenu = 'drafting'
            self.master.bind('<Down>',genFunc(self.movePointerDown))
            self.master.bind('<Up>',genFunc(self.movePointerUp))
            self.master.bind('<Left>',genFunc(self.decreaseCurrent))
            self.master.bind('<Right>',genFunc(self.increaseCurrent))
            self.master.bind('<Return>',genFunc(self.startDraft))

    def startDraft(self):
        coords = self.menuCanvas.coords('pointer')
        if coords[1] != 610:
            return
        self.menuCanvas.place_forget()
        beginDraftingGUI(self.master,self.numRounds,self.pokemonPerRound,self.numBattles)
        

    def decreaseCurrent(self): ##Used in draft-setup screen; decreases the value of the selected variable
        coords = self.menuCanvas.coords('pointer')
        if coords[1] == 540:
            if self.numBattles == 1:
                return
            else:
                self.numBattles -= 1
                self.menuCanvas.delete('numBattles')
                Lstopper = '-  '
                if self.numBattles == 1:
                    Lstopper = '   '
                string = Lstopper+'Number of Battles: '+str(self.numBattles)+'  +'
                self.menuCanvas.create_text(500,540,text=string,fill='white',font=self.MenuDPPtFont,tags=('numBattles'))
        elif coords[1] == 470:
            if self.pokemonPerRound == 4:
                return
            else:
                self.pokemonPerRound -= 1
                self.menuCanvas.delete('pokemonPerRound')
                Lstopper = '-  '
                if self.pokemonPerRound == 4: ##min value is 4, need to have 4 min pokemon for a team!
                    Lstopper = '   '
                string = Lstopper+'Pokemon Per Round: '+str(self.pokemonPerRound)+'  +'
                self.menuCanvas.create_text(500,470,text=string,fill='white',font=self.MenuDPPtFont,tags=('pokemonPerRound'))
        elif coords[1] == 400:
            if self.numRounds == 1:
                return
            else:
                self.numRounds -= 1
                self.menuCanvas.delete('numRounds')
                Lstopper = '-  '
                if self.numRounds == 1: ##min value is 1; can't have less than 1 battle
                    Lstopper = '   '
                string = Lstopper+'Number of Rounds: '+str(self.numRounds)+'  +'
                self.menuCanvas.create_text(500,400,text=string,fill='white',font=self.MenuDPPtFont,tags=('numRounds'))

    def increaseCurrent(self): ##as above but increases it
        coords = self.menuCanvas.coords('pointer')
        if coords[1] == 540:
            if self.numBattles == 10:
                return
            else:
                self.numBattles += 1
                self.menuCanvas.delete('numBattles')
                Rstopper = '  +'
                if self.numBattles == 10: ##max is 10 battles
                    Rstopper = '   '
                string = '-  Number of Battles: '+str(self.numBattles)+Rstopper
                self.menuCanvas.create_text(500,540,text=string,fill='white',font=self.MenuDPPtFont,tags=('numBattles'))
        elif coords[1] == 470:
            if self.pokemonPerRound == 6:
                return
            else:
                self.pokemonPerRound += 1
                self.menuCanvas.delete('pokemonPerRound')
                Rstopper = '  +'
                if self.pokemonPerRound == 6: ##max is 6 pokemon as that's all there is functionality for.
                    Rstopper = '   '
                string = '-  Pokemon Per Round: '+str(self.pokemonPerRound)+Rstopper
                self.menuCanvas.create_text(500,470,text=string,fill='white',font=self.MenuDPPtFont,tags=('pokemonPerRound'))
        elif coords[1] == 400:
            if self.numRounds == 3:
                return
            else:
                self.numRounds += 1
                self.menuCanvas.delete('numRounds')
                Rstopper = '  +'
                if self.numRounds == 3: ##max is three rounds as that's all the view-choices area has room for
                    Rstopper = '   '
                string = '-  Number of Rounds: '+str(self.numRounds)+Rstopper
                self.menuCanvas.create_text(500,400,text=string,fill='white',font=self.MenuDPPtFont,tags=('numRounds'))

            
#-----------------------------------------------------------------------------------------------------------#
            
    def loadRandomBattle(self): ##loads a random battle
        randClass = r.choice(trainerClass) ##Select a random trainer class
        enemyTrainer = battle.trainer(r.choice(names[randClass]),randClass,randClass) ##Select a random name from the allowable set of names for the class
        userTrainer = battle.trainer('Ethan','Pokemon Trainer','Ethan') ##user has Ethan's sprite
        Trainer = enemyTrainer 
        for x in range(12): ##6 user pokemon, 6 enemy pokemon
            if x == 6:
                Trainer = userTrainer
            P = battle.pokemon(r.choice(pokemonInDraft),r.randint(50,60),Trainer) ##random generate using the 50-60 levle range from before.
            Trainer.addToTeam(x%6) ##if greater than 6, we are defining user pokemon so must start from 0
            physical = 0
            numPhysical = 0
            special = 0
            numSpecial = 0
            bulky = 0
            numStatus = 0
            for move in P.moves: ##must find a suitable EV spread for its moves
                ##Three general types of pokemon: Physical, Special, and Bulky
                ##Physical/Special: Use moves of their respective category to beat down opposing Pokemon
                ##Bulky: Tend to try to stall out an Opponent's Pokemon using status moves or recovery moves and a weakly damaging move.
                if move[0].category == 'Physical': ##if a physical move, more likely to be a physical attacker
                    physical += 1
                    numPhysical += 1
                elif move[0].category == 'Special': ##if a special move, more likely to be a special attacker
                    special += 1
                    numSpecial += 1 
                else: ##so it's a status move and makes it more likely to be bulky
                    bulky += 1
                    numStatus += 1

                if move[0].name in ['Bullet Punch','Close Combat','Dragon Dance', ##these moves are especially physical-oriented, so even less likely to be bulky and more likely to be physical
                                    'Mach Punch','Superpower','Swords Dance']:
                    bulky -= 1
                    physical += 1
                elif move[0].name in ['Draco Meteor','Leaf Storm','Nasty Plot','Overheat']: ##as before but more likely to be special
                    bulky -= 1
                    special += 1
                elif move[0].name in ['Agility','Shell Smash']: ##not clear whether they are physical or special, but they aren't bulky.
                    bulky -= 1
                    special += 1
                    physical += 1
                elif move[0].name in ['Calm Mind']: ##Both special attacker and bulky
                    special += 1
                    bulky += 1
                elif move[0].name in ['Amnesia','Hibernate','Hypnosis','Iron Defense','Light Screen', ##These moves are used primarily by bulky pokemon
                                      'Protect','Rest','Reflect','Thunder Wave','Toxic','Will-O-Wisp']:
                    bulky += 2
                    physical -= 1
                    special -= 1
            if bulky > physical and bulky > special: ##Very bulky Pokemon, so it will have a bulky set
                if numPhysical + numSpecial <= 1: ##Has or less damaging moves, so is a Pokemon that just stalls
                    P.ev = r.choice(EVSpreads['pure stall'])
                elif numPhysical >= 2: ##Has more than 2 attacking physical moves, so is a physical wall
                    P.ev = r.choice(EVSpreads['physical wall'])
                elif numSpecial >= 2: ##As above but special
                    P.ev = r.choice(EVSpreads['special wall'])
                else: ##At least 1 physical AND 1 special, so its a mixed wall.
                    P.ev = r.choice(EVSpreads['mixed wall'])
            elif special > physical and special > bulky: ##It's a special attacker!
                if numPhysical == 0: ##If it has no physical moves, it must be a purely special attacker
                    P.ev = r.choice(EVSpreads['special sweeper'])
                else: ##So it has some physical moves and is a mixed attacker
                    P.ev = r.choice(EVSpreads['mixed attacker'])
            elif physical > special and physical > bulky: ##As above but for physical
                if numSpecial == 0:
                    P.ev = r.choice(EVSpreads['physical sweeper'])
                elif numSpecial >= 1:
                    P.ev = r.choice(EVSpreads['mixed attacker'])
            elif physical == special and physical > bulky: ##If physical and special are the same, and P is greater than B, it must be a mixed attacker
                P.ev = r.choice(EVSpreads['mixed attacker'])
            else: ##Else there's no clear reason to their set, so give them even EVs across the board
                P.ev = r.choice(EVSpreads['true balance'])
            P.statCalculate()
        switchToBattleGUI(userTrainer,enemyTrainer,self.master,[[],[0,0]]) ##See how the arguments are defined below, this transitions us to a battle with 0 battles left and 0 battles total
        

#-----------------------------------------------------------------------------------------------------------#

        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
          

class draftingApp: ##This controls the drafting process of the game.
    def __init__(self,master,numRounds,pokemonPerRound,numBattles,receiveInfo = False):
        
        self.master = master ##Store the Tk() object which acts as the 'master' of geometry
        self.battleStart = False 
        self.smallestWating = 0
        self.textRunning = False ##A variable the tracks whether text is running
        self.platformMovementStyles = ['diagonalSeparation','columnSeparation','rowSeparation'] ##Stores the different styles of movement for the platforms that are programmed

        ##Stores the coords of the platforms
        self.coordsDict = {'(115, 150)' : ('platform','platformC1','platformR1','platformC1R1','platform(115, 150)'),
                           '(115, 320)' : ('platform','platformC1','platformR2','platformC1R2','platform(115, 320)'),
                           '(115, 490)' : ('platform','platformC1','platformR3','platformC1R3','platform(115, 490)'),
                           '(375, 130)' : ('platform','platformC2','platformR1','platformC2R1','platform(375, 130)'),
                           '(375, 300)' : ('platform','platformC2','platformR2','platformC2R2','platform(375, 300)'),
                           '(375, 470)' : ('platform','platformC2','platformR3','platformC2R3','platform(375, 470)')}
        
        self.battleFrame = Frame(master,relief=SUNKEN,borderwidth=5,height=350,width=500,bg=backgrounds['indoor']['bgColor'])  ##Creates the frame to hold all of the images for the drafting process
        self.battleFrame.grid(row=0,column=0,sticky=W+E+N+S)
        self.battleCanvas = Canvas(self.battleFrame,width=485,height=537)
        self.battleCanvas.pack()

        ##Initializes the different fonts/sizes
        self.DPPtFont = font.Font(family='Pokemon DPPt',size=26)
        self.DPPtFont2 = font.Font(family='Pokemon DPPt',size=24)
        self.tabletFont = font.Font(family='Pokemon DPPt',size=15,weight="bold")
        self.tabletFontSmall = font.Font(family='Pokemon DPPt',size=13,weight="bold")
        self.smallTabletFont = font.Font(family='Pokemon DPPt',size=13,weight="bold")

        ##Loads the frame for the Tablet that is seen on the right hand side of the screen
        self.pokedexFrame = Frame(master,relief=SUNKEN,borderwidth=5,height=700,width=500,bg='grey')
        self.pokedexFrame.grid(row=0,column=1,rowspan=3,sticky=W+E+N+S)
        self.screenFrame = Frame(self.pokedexFrame,relief=SUNKEN,borderwidth=5,height=500,width=400,bg='light grey')
        self.screenFrame.place(x=245,y=50,anchor=N)
        self.viewChoicesButton = Button(self.pokedexFrame,state=DISABLED,bg='#9fe8c4',font=self.DPPtFont2,text='View Choices',command=self.showChoices)
        self.viewChoicesButton.place(x=245,y=602,anchor=N)
        self.tabletCanvas = Canvas(self.screenFrame,width=380,height=500,bg='light grey')
        self.tabletCanvas.pack()

        ##Loads the textbox that displays text
        self.textFrame = Frame(master,relief=RAISED,borderwidth=5,height=150,width=500,bg='white')
        self.textFrame.grid(row=1,column=0,sticky=W+E+N+S)
        self.textBox0 = Label(self.textFrame,text="",font=self.DPPtFont,bg='white',anchor='center')
        self.textBox0.place(x=10,y=32,anchor='w')
        self.textBox1 = Label(self.textFrame,text="",font=self.DPPtFont,bg='white',anchor='center')
        self.textBox1.place(x=10,y=67,anchor='w')
        self.textBox2 = Label(self.textFrame,text="",font=self.DPPtFont,bg='white',anchor='center')
        self.textBox2.place(x=10,y=102,anchor='w')
        self.triangleImageFile = Image.open(assets['triangle'])
        self.triangleImageFile = ImageTk.PhotoImage(self.triangleImageFile)
        self.triangle = Label(master=self.textFrame,image=self.triangleImageFile,bg='white')
        self.tBoxPointer = 0
        self.tBox = {
            '0' : self.textBox0,
            '1' : self.textBox1,
            '2' : self.textBox2
            }

        self.backgroundPilImage = Image.open(backgrounds['indoor']['filePath']) ##Loads the wavy gradient-esque background that is observed in the drafting process
        self.backgroundPilImage = self.backgroundPilImage.resize((500,600))
        self.background = ImageTk.PhotoImage(self.backgroundPilImage)
        self.backgroundImage = self.battleCanvas.create_image(0,0,image=self.background,anchor=NW,tags=('background-indoor','background','indoor'))
        
        self.platformImageFile = Image.open(assets['indoor-enemy'])
        self.platformImageFile = self.platformImageFile.resize((225,75))
        self.platformImage = ImageTk.PhotoImage(self.platformImageFile)

        ##these platforms are the platforms that show the pokemon for you to choose.
        self.battleCanvas.create_image(115,150-530,image=self.platformImage,tags=('platform','platformC1','platformR1','platformC1R1','platform(115, 150)'))
        self.battleCanvas.create_image(115,320-530,image=self.platformImage,tags=('platform','platformC1','platformR2','platformC1R2','platform(115, 320)'))
        self.battleCanvas.create_image(115,490-530,image=self.platformImage,tags=('platform','platformC1','platformR3','platformC1R3','platform(115, 490)'))
        self.battleCanvas.create_image(375,130+530,image=self.platformImage,tags=('platform','platformC2','platformR1','platformC2R1','platform(375, 130)'))
        self.battleCanvas.create_image(375,300+530,image=self.platformImage,tags=('platform','platformC2','platformR2','platformC2R2','platform(375, 300)'))
        self.battleCanvas.create_image(375,470+530,image=self.platformImage,tags=('platform','platformC2','platformR3','platformC2R3','platform(375, 470)'))

        ##important dictionaries used for indicating either a) the location of resources for a given item, b) the ID of those items, and c) whether or not a task has finished so that the system knows if it can begin the next task.
        self.pokemonCoordsSouth = [(115,150),(115,320),(115,490),(375,130),(375,300),(375,470)] ##list of pokeball/pokemon IDs, stored as the coords of them when the platforms aren't moving
        self.EpokeballImageFile = {} ##this and the following dicts store the image locations for a given id for a given pokeball/pokemon slot
        self.EpokeballImage = {}
        self.EpokemonImageFile = {}
        self.EpokemonImage = {}
        self.Epokemon = {}
        self.pokemonCanvasItemVars = {}
        self.pokeballCanvasItemVars = {'(115, 150)' : 'noneyet', '(115, 320)' : 'noneyet', '(115, 490)' : 'noneyet', '(375, 130)' : 'noneyet', '(375, 300)' : 'noneyet', '(375, 470)' : 'noneyet'}
        self.taskFinished = {'False' : True}
        for coords in self.pokemonCoordsSouth: ##must prefill the dictionary for pokeball images so that they can appear on the platforms at the very start of the draft.
            self.EpokeballImage[str(coords)] = ImageTk.PhotoImage(Image.open(pokeballs['Pokeball']).resize((24,35)))

        #input param vars
        self.pokemonPerRound = pokemonPerRound
        self.numRounds = numRounds
        self.numBattles = numBattles

        #vars used for team creation
        self.team = {0:None,1:None,2:None,3:None} ##stores the team
        self.teamToChoicesLink = {0:None,1:None,2:None,3:None} ##stores the refernece to choices
        self.teamIDs = {0:None,1:None,2:None,3:None} ##stores the IDs of the team members
        self.teamImages = {0:None,1:None,2:None,3:None} ##stores their images
        self.transparentBoxImage1 = {} ##bigger boxes used for team (the semi-transparent dark grey boxes covering the empty sections)
        self.transparentBoxImage2 = {} ##smaller one used for choices
        self.teamCreation = False ##used for cursor specifiers in the choices menu

        ##these vars are for storing EV training values
        self.EVEntry = {}
        self.EVStringVar = {}

        ##these 'black' files are the fade in black things we see at the start of the draft.
        self.blackImageFile = Image.open('assets/black/black250.png').resize((700,700))
        self.blackImage = ImageTk.PhotoImage(self.blackImageFile)
        self.battleCanvas.create_image(0,0,anchor=NW,image=self.blackImage,tags=('black-screen'))

        ##stuff to pay attention to if we aren't drafting but are instead making a team
        ##receiveInfo in form [list of pokemon chosen, number of battles left]
        ##I.e. these are used for 
        if receiveInfo != False:
            self.pokemonChosen = receiveInfo[0]
            print("RECEIVING POKEMON CHOSEN: ", self.pokemonChosen)
            self.battlesLeft = receiveInfo[1][0]
            self.numBattles = receiveInfo[1][1]
        else:
            self.pokemonChosen = []
            self.battlesLeft = self.numBattles

 ##puts the pokeballs on the platforms in preparation
        self.beginDraftAnimation() ##start of draft anim happens :)

    def beginDraftAnimation(self,alpha=0,sign=5):
        if alpha == 0 and sign == 5:
            self.beginImageFile = Image.open(assets['begin'])
            self.beginImageFile = self.beginImageFile.resize((400,188))
        self.beginImageFile.putalpha(alpha)
        self.beginImage = ImageTk.PhotoImage(self.beginImageFile)
        self.battleCanvas.delete('begin-draft')
        self.battleCanvas.create_image(245,280,image=self.beginImage,tags=('begin-draft'))
        if alpha == 255:
            if sign == 5:
                sign = -100
            elif sign < -5:
                sign += 5
        elif alpha == 0 and sign == -5:
            self.revealScreen()
            self.battleCanvas.delete('begin-draft')
            return
        if sign == -5 or sign == 5:
            k = genFunc(self.beginDraftAnimation,alpha+sign,sign)
            master.after(50,k)
        else:
            k = genFunc(self.beginDraftAnimation,alpha,sign)
            master.after(50,k)

    def revealScreen(self,alpha=255):
        self.battleCanvas.delete('blackScreen')
        if alpha == 0:
            self.initDraft()
            return
        self.blackImageFile.putalpha(alpha)
        self.blackImage = ImageTk.PhotoImage(self.blackImageFile)
        self.battleCanvas.create_image(0,0,anchor=NW,image=self.blackImage,tags=('black-screen'))
        k = genFunc(self.revealScreen,alpha-5)
        master.after(50,k)

#------------------------------------------------------------------------------------------------------------------------------#
           # This is to update the tablet. Code taken verbatim from battle GUI file.
#------------------------------------------------------------------------------------------------------------------------------#

        ##tablet stuff
    def tablet_displayEnemyPokemon(self,pkmn):

        self.tabletCanvas.delete('tablet-data')
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

    def tablet_editEVs(self,pkmn):
        self.tabletCanvas.delete('tablet-data')
        self.tabletCanvas.create_rectangle([115,10,270,160],fill=typeColor[pkmn.types[0]],width=3,outline='black',stipple='gray25',tags=('tablet-data'))
        self.tab_pokemonImage = Image.open(pokemon[pkmn.name])
        self.tab_pokemonImage = ImageTk.PhotoImage(self.tab_pokemonImage.resize((141,141)))
        self.tabletCanvas.create_image(190,80,image=self.tab_pokemonImage,tags=('tablet-data','pokemon-photo'))

        self.tabletCanvas.create_text(20,195,text='Current Stats: ' + str(pkmn.stats),font=self.tabletFontSmall,anchor=W,tags=('tablet-data','tablet-current-stats')) ##show the user their current stats
        #self.tabletCanvas.create_text(20,210,text='Adjust EVs:',font=self.tabletFont,anchor=W,tags=('tablet-data'))

        ##init the ev defining methods
        count = 0
        for stat in ['HP','Attack','Defense','Sp. Attack', 'Sp. Defense', 'Speed']:
            self.tabletCanvas.create_text(90,240+30*count,text=stat+' EVs: ',anchor=W,font=self.tabletFont,tags=('tablet-data'))
            self.EVStringVar[stat] = StringVar()
            self.EVStringVar[stat].set(pkmn.ev[count])
            self.EVStringVar[stat].trace_variable('w',genFunc(self.adjustEVStringVarLength,self.EVStringVar[stat]))
            self.EVEntry[stat] = Entry(self.tabletCanvas,textvariable=self.EVStringVar[stat],font=self.tabletFont)
            self.tabletCanvas.create_window(250,240+30*count,window=self.EVEntry[stat],anchor=W,width=30,tags=('tablet-data'))
            count += 1

    def adjustEVStringVarLength(self,var): ##this func is used to make sure evs dont exceed a max value and that no bad char are entered
        k = var.get()
        for x in range(1,len(k)+1):
            if k[len(k)-x] not in '0123456789': ##i.e. if we have an invalid character
                print(k[len(k)-x])
                if x != 1:
                    k = k[:len(k)-x] + k[len(k)-x+1:] ##this excludes the character
                else:
                    k = k[:len(k)-x]
        if len(k) > 3: ##max len 3
            k = k[:3]
        elif len(k) == 0:
            k = '0'
        var.set(k)
        statTotal = 0
        for stat in ['HP','Attack','Defense','Sp. Attack', 'Sp. Defense', 'Speed']:
            statTotal += int(self.EVStringVar[stat].get())
        if statTotal > 510: ##max stat cap across EVs is 510
            k = str(int(k) - (statTotal-508))
        if int(k) > 252: ##cant have higher than 252 in an individual stat
            k = '252'
        var.set(k)
        
    def getUsableDesc(self,desc): ##splits the description into something usable
        res = []
        desc = desc.split(' ')
        temp = desc[0]
        del desc[0]
        for word in desc:
            if len(temp+word) > 50:
                res.append(temp)
                temp = word
            else:
                temp += ' '+word
        if temp != '':
            res.append(temp)
        return res

#------------------------------------------------------------------------------------------------------------------------------#
           ## View choices!! This is the code to update the user's choices.
#------------------------------------------------------------------------------------------------------------------------------#
    def showChoices(self):
        self.deactivateButtons()
        self.slideChoicesAcross()

    def slideChoicesAcross(self,loop=0,teamCreation=False): ##this function is also used for loading team creation.
        ##for x in range(0,17):
        ##    self.pokemonChosen.append(battle.pokemon(r.choice(pokemonInDraft),r.randint(50,60)))

        self.boxIDs = []
        if loop == 0:
            self.battleCanvas.create_rectangle(0+490,0,490+490,542,width=2,fill='light grey',tags=('choices-data','choices-background'))  ##This creates the light grey background to put the boxes on
            xOffset = 7
            yOffset = 5
            for x in range(0,18): ##this creates the light grey boxes
                if x == 15: ##if at 15, then we must start with an offset to get them centered as its 18 max
                    xOffset = 96+7
                self.boxIDs.append(self.battleCanvas.create_rectangle(0+xOffset+490,0+yOffset,90+xOffset+490,90+yOffset,fill='light grey', outline='grey',width=2,tags=('choices-data','not-team')))
                xOffset = (xOffset + 96) % 480 ##loops aorund when xOffset gets bigger than 480
                yOffset = (yOffset) + 96*int((x%5+1)/5) ##adds 96 whenever next x is divisible by 5- i.e. when we've plotted 5 items in a row

            self.tempChoicesIDs = [] ##need to store the photos because of how python handles unbound variables, even if they are used as args in a class definition
            self.tempChoicesPhotos = []
            xOffset = 7
            yOffset = 5
            count = 0
            for pkmn in self.pokemonChosen: ##adds the Pokemon to the boxes.
                if count == 15: 
                    xOffset = 96+7
                self.tempChoicesPhotos.append(ImageTk.PhotoImage(Image.open(pokemon[pkmn.species]).resize((84,84))))
                ID = self.battleCanvas.create_image(0+xOffset+490,0+yOffset,anchor=NW,image=self.tempChoicesPhotos[count],tags=('choices-data','not-team'))
                xOffset = (xOffset + 96) % 480
                yOffset = (yOffset) + 96*int((count%5+1)/5)
                self.tempChoicesIDs.append(ID)
                count += 1
                
            if teamCreation: ##only applicable if team creation is in use- i.e. at the end of a draft, or in between battles
                xOffset = 15
                for x in range(0,4):
                    self.battleCanvas.create_rectangle(0+xOffset+490,537-125,100+xOffset+490,537-25,fill='light grey',outline='grey',width=2,tags=('choices-data','team'))
                    self.transparentBoxImage1[x] = ImageTk.PhotoImage(Image.open('assets/drafting/greyRectangleTransparent/grey100.png'))
                    self.battleCanvas.create_image(0+xOffset+490,537-125,anchor=NW,image=self.transparentBoxImage1[x],tags=('transparencyBox-team-'+str(x),'choices-data'))
                    xOffset += 120
            self.battleCanvas.lift('choices-data')
            master.after(5,genFunc(self.slideChoicesAcross,loop+1,teamCreation))
            
        elif 98 >= loop >= 1: ##This just moves the choices on screen
            self.battleCanvas.move('choices-data',-5,0)
            master.after(10,genFunc(self.slideChoicesAcross,loop+1,teamCreation))
        else: ##Enables the 'hide choices' button (if in draft mode, otherwise sets it to be an inactive blue button with text 'To EV Training') and enables the hover-over bindings
            self.viewChoicesButton.config(text='Hide Choices',command=self.hideChoices,state=ACTIVE,cursor='hand2')
            master.update()
            self.viewChoicesButton.config(bg='#ff9d9d')
            master.update()
            count = 0
            for x in range(len(self.tempChoicesIDs)):
                self.battleCanvas.tag_bind(self.tempChoicesIDs[x],'<Enter>',genFunc(self.choices_hoverOver,self.pokemonChosen[x],self.tempChoicesIDs[x]))
                self.battleCanvas.tag_bind(self.tempChoicesIDs[x],'<Leave>',self.choices_hoverOff)
                if teamCreation:
                    self.battleCanvas.tag_bind(self.tempChoicesIDs[x],'<Button-1>',genFunc(self.addToTeam,x))
                    self.viewChoicesButton.config(text='To EV Training',bg='#aec1db',state=DISABLED)

    def choices_hoverOver(self,pokemon,ID): ##Changes cursor to hand cursor and shows Pokemon information on canvas
        if self.teamCreation:        
            self.battleCanvas.config(cursor='hand2')
        self.tablet_displayEnemyPokemon(pokemon)
        self.isCursorOnPokemon = self.battleCanvas.coords(ID)
        self.choices_boxSelection(self.isCursorOnPokemon)

    def choices_hoverOff(self,event=False): ##Clears canvas and resets cursor to arrow
        if self.teamCreation:        
            self.battleCanvas.config(cursor='arrow')
        self.tabletCanvas.delete('tablet-data')
        self.isCursorOnPokemon = False

    def choices_boxSelection(self,coords,offset=0,sign=0.1,posOrNeg=-0.02): ##pops up a small green box around the user's choice
        try:
            self.choices_boxImageTR
        except:
            self.choices_boxImageTR = ImageTk.PhotoImage(Image.open(assets['sBoxTR']).resize((10,10)))
            self.choices_boxImageTL = ImageTk.PhotoImage(Image.open(assets['sBoxTL']).resize((10,10)))
            self.choices_boxImageBR = ImageTk.PhotoImage(Image.open(assets['sBoxBR']).resize((10,10)))
            self.choices_boxImageBL = ImageTk.PhotoImage(Image.open(assets['sBoxBL']).resize((10,10)))
        self.battleCanvas.delete('selection-box')
        self.battleCanvas.create_image(coords[0]+1-offset,coords[1]+6-offset,image=self.choices_boxImageTL,anchor=S,tags=('selection-box'))
        self.battleCanvas.create_image(coords[0]+89+offset,coords[1]+6-offset,image=self.choices_boxImageTR,anchor=S,tags=('selection-box'))
        self.battleCanvas.create_image(coords[0]+1-offset,coords[1]+94+offset,image=self.choices_boxImageBL,anchor=S,tags=('selection-box'))
        self.battleCanvas.create_image(coords[0]+89+offset,coords[1]+94+offset,image=self.choices_boxImageBR,anchor=S,tags=('selection-box'))
        if int(sign*10) == -1:
            posOrNeg = 0.02
        elif int(sign*10) == 1:
            posOrNeg = -0.02
        if self.isCursorOnPokemon == coords:
            k = genFunc(self.choices_boxSelection,coords,offset+sign,sign+posOrNeg,posOrNeg)
            master.after(35,k)
        else:
            self.battleCanvas.delete('selection-box')

    def hideChoices(self): ##Hides the choices out to return to drafting.
        for ID in self.tempChoicesIDs:
            self.battleCanvas.tag_unbind(ID,'<Enter>')
            self.battleCanvas.tag_unbind(ID,'<Leave>')
        self.deactivateButtons()
        self.slideChoicesOut()

    def slideChoicesOut(self,loop=0): ##Slides the choices out and then deletes them
        if loop <= 97:
            self.battleCanvas.move('choices-data',5,0)
            master.after(5,genFunc(self.slideChoicesOut,loop+1))
        else:
            self.battleCanvas.delete('choices-data')
            self.viewChoicesButton.config(bg='#9fe8c4',text='View Choices',command=self.showChoices,state=ACTIVE)
            self.activateButtons()
                                                                      
#------------------------------------------------------------------------------------------------------------------------------#
           # Team creation. These are where the functions that let the user pick and EV train their team are.
#------------------------------------------------------------------------------------------------------------------------------#

    def initTeamCreation(self): ##Initiates the setup for team creation in the form of an executable queue
        q = battle.serviceQueue()
        self.teamCreation = True
        style = r.choice(self.platformMovementStyles)
        q.add([style,genFunc(self.movePlatforms,'off',style,0,False)])
        q.add([False,genFunc(self.slideChoicesAcross,0,True)])
        self.executeTurn(q)

    def disableChoices(self): ##Disables the choices. This is relevant when an animation is playing, such as a fading grey box.
        for ID in self.tempChoicesIDs:
            self.battleCanvas.itemconfig(ID,state=DISABLED)
        for x in range(0,4):
            if self.team[x] != None:
                self.battleCanvas.itemconfig(self.teamIDs[x],state=DISABLED)
        self.viewChoicesButton.config(state=DISABLED,cursor='arrow')

    def enableChoices(self):
        for x in range(len(self.tempChoicesIDs)):
            self.battleCanvas.itemconfig(self.tempChoicesIDs[x],state=NORMAL)
        count = 0
        for x in range(0,4):
            if self.team[x] != None:
                count += 1
                self.battleCanvas.itemconfig(self.teamIDs[x],state=NORMAL)
                self.battleCanvas.lift('team-'+str(x))
        if count == 4:
            self.viewChoicesButton.config(state=ACTIVE,command=self.moveToEVTraining,cursor='hand2')

    def team_boxSelection(self,coords,start=True): ##pops up a small green box around the user's choice
        if start:
            try:
                self.team_boxImageTR
            except:
                self.team_boxImageTR = ImageTk.PhotoImage(Image.open(assets['sBoxTR']).resize((10,10)))
                self.team_boxImageTL = ImageTk.PhotoImage(Image.open(assets['sBoxTL']).resize((10,10)))
                self.team_boxImageBR = ImageTk.PhotoImage(Image.open(assets['sBoxBR']).resize((10,10)))
                self.team_boxImageBL = ImageTk.PhotoImage(Image.open(assets['sBoxBL']).resize((10,10)))
            self.battleCanvas.delete('selection-box')
            self.battleCanvas.create_image(coords[0]+1,coords[1]+6,image=self.team_boxImageTL,anchor=S,tags=('selection-box'))
            self.battleCanvas.create_image(coords[0]+98,coords[1]+6,image=self.team_boxImageTR,anchor=S,tags=('selection-box'))
            self.battleCanvas.create_image(coords[0]+1,coords[1]+104,image=self.team_boxImageBL,anchor=S,tags=('selection-box'))
            self.battleCanvas.create_image(coords[0]+98,coords[1]+104,image=self.team_boxImageBR,anchor=S,tags=('selection-box'))
            
        if self.isCursorOnPokemon == coords:
            k = genFunc(self.team_boxSelection,coords,False)
            master.after(10,k)
        else:
            self.battleCanvas.delete('selection-box')

    def team_hoverOver(self,index): ##this is used for EV as well
        self.battleCanvas.config(cursor='hand2')
        self.isCursorOnPokemon = self.battleCanvas.coords(self.teamIDs[index])
        self.tablet_displayEnemyPokemon(self.team[index])
        self.team_boxSelection(self.isCursorOnPokemon)

    def team_hoverOff(self,event=False): ##this is used for EVs as well
        self.battleCanvas.config(cursor='arrow')
        self.tabletCanvas.delete('tablet-data')
        self.isCursorOnPokemon = False

    def removeFromTeam(self,x):
        self.disableChoices()
        self.team[x] = None
        self.moveTeamMemberOffscreen(self.teamToChoicesLink[x],x)

    def addToTeam(self,x):
        for i in range(4):
            if self.team[i] == None:
                self.disableChoices()
                self.team[i] = self.pokemonChosen[x]
                self.teamToChoicesLink[i] = self.tempChoicesIDs[x] ##this is needed to be able to show it again later

                self.battleCanvas.itemconfig(self.tempChoicesIDs[x],state=DISABLED) ##disables the button so no funny business
                self.teamImages[i] = (ImageTk.PhotoImage(Image.open(pokemon[self.pokemonChosen[x].species]).resize((96,96))))
                
                self.teamIDs[i] = self.battleCanvas.create_image(15+120*i,537-125,anchor=NW,image=self.teamImages[i],tags=('team-'+str(i),'team'))
                self.transparentBoxImage1[i] = ImageTk.PhotoImage(Image.open('assets/drafting/greyRectangleTransparent/grey100.png'))
                self.battleCanvas.create_image(15+120*i,537-125,anchor=NW,image=self.transparentBoxImage1[i],tags=('transparencyBox-team'))
                self.battleCanvas.isCursorOnPokemon = False
                self.moveTeamMemberOnscreen(self.tempChoicesIDs[x],i)
                return

    def moveTeamMemberOnscreen(self,IDChoice,i,loop=0): ##IDChoice is the ID of the choice, i is the index in the team
        if loop < 25:
            self.battleCanvas.delete('transparencyBox-team-'+str(i)) ##delete previous transparent box for a team slot
            self.transparentBoxImage1[i] = ImageTk.PhotoImage(Image.open('assets/drafting/greyRectangleTransparent/grey'+str((25-1-loop)*4)+'.png')) ##load new transparency for transparent box
            self.temp = self.battleCanvas.create_image(15+120*i,537-125,anchor=NW,image=self.transparentBoxImage1[i],tags=('transparencyBox-team-'+str(i))) ##put on screen

            c = self.battleCanvas.coords(IDChoice) ##get coords of thing we are covering
            self.battleCanvas.delete('transparencyBox-choice-'+str(IDChoice)) ##rest is as above
            self.transparentBoxImage2[IDChoice] = ImageTk.PhotoImage(Image.open('assets/drafting/greyRectangleTransparent/grey'+str(loop*4+4)+'.png').resize((90,90)))
            self.battleCanvas.create_image(c[0],c[1],anchor=NW,image=self.transparentBoxImage2[IDChoice],tags=('transparencyBox-choice-'+str(IDChoice),'not-team'))
            
            master.after(20,genFunc(self.moveTeamMemberOnscreen,IDChoice,i,loop+1)) ##call function for next loop in 20 ms
        else:
            self.battleCanvas.delete('transparencyBox-team-'+str(i))
            self.battleCanvas.tag_bind('team-'+str(i),'<Enter>',genFunc(self.team_hoverOver,i))
            self.battleCanvas.tag_bind('team-'+str(i),'<Leave>',self.team_hoverOff)
            self.battleCanvas.tag_bind('team-'+str(i),'<Button-1>',genFunc(self.removeFromTeam,i))
            self.enableChoices()

    def moveTeamMemberOffscreen(self,IDChoice,i,loop=0):
        if loop < 25:
            self.battleCanvas.delete('transparencyBox-team-'+str(i)) ##delete previous transparent box for a team slot
            self.transparentBoxImage1[i] = ImageTk.PhotoImage(Image.open('assets/drafting/greyRectangleTransparent/grey'+str((loop*4+4))+'.png')) ##load new transparency for transparent box
            self.battleCanvas.create_image(15+120*i,537-125,anchor=NW,image=self.transparentBoxImage1[i],tags=('transparencyBox-team-'+str(i))) ##put on screen
            
            c = self.battleCanvas.coords(IDChoice) ##get coords of thing we are covering
            self.battleCanvas.delete('transparencyBox-choice-'+str(IDChoice)) ##rest is as above
            self.transparentBoxImage2[IDChoice] = ImageTk.PhotoImage(Image.open('assets/drafting/greyRectangleTransparent/grey'+str(100-loop*4-4)+'.png').resize((90,90)))
            self.battleCanvas.create_image(c[0],c[1],anchor=NW,image=self.transparentBoxImage2[IDChoice],tags=('transparencyBox-choice-'+str(IDChoice)))
            
            master.after(20,genFunc(self.moveTeamMemberOffscreen,IDChoice,i,loop+1)) ##call function for next loop in 20 ms
        else:
            self.battleCanvas.delete('transparencyBox-choice-'+str(IDChoice))
            self.battleCanvas.delete('team-'+str(i))
            self.battleCanvas.lift(IDChoice)
            self.enableChoices()

    def moveToEVTraining(self,loop=0):
        if loop == 0:
            self.disableChoices()
            master.after(10,genFunc(self.moveToEVTraining,loop+1))
        elif 0 < loop <= 98:
            self.battleCanvas.move('not-team',-5,0)
            master.after(10,genFunc(self.moveToEVTraining,loop+1))
        elif 99 == loop:
            self.battleCanvas.delete('not-team')
            master.after(10,genFunc(self.moveToEVTraining,loop+1))
        elif 99 < loop < 138:
            self.battleCanvas.move('team',0,-5)
            master.after(20,genFunc(self.moveToEVTraining,loop+1))
        elif loop == 138:
            c = self.battleCanvas.coords('team-1')
            p = self.battleCanvas.coords('team-2')
            self.runText('Click a Pokémon to EV train them.')
            self.viewChoicesButton.config(text='Start Battle',bg='light green',state=ACTIVE)
            self.initEVTraining()

    def initEVTraining(self):
        for x in range(0,4):
            self.battleCanvas.tag_unbind('team-'+str(x),'<Button-1>')
            self.battleCanvas.tag_bind('team-'+str(x),'<Button-1>',genFunc(self.EV_lockButtons,x))
            self.viewChoicesButton.config(text='Start Battle',bg='light green')
        self.EV_enableButtons()

    def startBattle(self): ##see description of the random battle generator function to understand how this works.
        self.EV_disableButtons()
        randClass = r.choice(trainerClass)
        enemyTrainer = battle.trainer(r.choice(names[randClass]),randClass,randClass)
        for x in range(4):
            P = battle.pokemon(r.choice(pokemonInDraft),r.randint(50,60),enemyTrainer)
            enemyTrainer.addToTeam(x)
            physical = 0
            numPhysical = 0
            special = 0
            numSpecial = 0
            bulky = 0
            numStatus = 0
            for move in P.moves:
                if move[0].category == 'Physical':
                    physical += 1
                    numPhysical += 1
                elif move[0].category == 'Special':
                    special += 1
                    numSpecial += 1
                else:
                    bulky += 1
                    numStatus += 1

                if move[0].name in ['Bullet Punch','Close Combat','Dragon Dance','Mach Punch','Superpower','Swords Dance']:
                    bulky -= 1
                    physical += 1
                elif move[0].name in ['Draco Meteor','Leaf Storm','Nasty Plot','Overheat']:
                    bulky -= 1
                    special += 1
                elif move[0].name in ['Agility','Shell Smash']:
                    bulky -= 1
                    special += 1
                    physical += 1
                elif move[0].name in ['Calm Mind']:
                    special += 1
                    bulky += 1
                elif move[0].name in ['Amnesia','Hibernate','Hypnosis','Iron Defense','Light Screen','Protect','Rest','Reflect','Thunder Wave','Toxic','Will-O-Wisp']:
                    bulky += 2
                    physical -= 1
                    special -= 1
            if bulky > physical and bulky > special:
                if numPhysical + numSpecial <= 1:
                    P.ev = r.choice(EVSpreads['pure stall'])
                elif numPhysical >= 2:
                    P.ev = r.choice(EVSpreads['physical wall'])
                elif numSpecial >= 2:
                    P.ev = r.choice(EVSpreads['special wall'])
                else:
                    P.ev = r.choice(EVSpreads['mixed wall'])
            elif special > physical and special > bulky:
                if numPhysical == 0:
                    P.ev = r.choice(EVSpreads['special sweeper'])
                elif numPhysical >= 1:
                    P.ev = r.choice(EVSpreads['mixed attacker'])
            elif physical > special and physical > bulky:
                if numSpecial == 0:
                    P.ev = r.choice(EVSpreads['physical sweeper'])
                elif numSpecial >= 1:
                    P.ev = r.choice(EVSpreads['mixed attacker'])
            elif physical == special and physical > bulky:
                P.ev = r.choice(EVSpreads['mixed attacker'])
            else:
                P.ev = r.choice(EVSpreads['true balance'])
            P.statCalculate()
                    

        userTrainer = battle.trainer('Ethan','Pokemon Trainer','Ethan')
        for x in range(4):
            self.team[x].getTrainer(userTrainer)
            self.team[x].fullyHeal()
            userTrainer.addToTeam(x)
        for x in [self.textFrame,self.battleFrame,self.pokedexFrame]:
            x.grid_forget()
        if self.battlesLeft == 1 and self.numBattles == 10:
            enemyTrainer = self.findBossBattleTrainer()
            switchToBattleGUI(userTrainer,enemyTrainer,self.master,[self.pokemonChosen,[self.battlesLeft,self.numBattles]],megaboss=enemyTrainer.name)
        elif (self.numBattles == 10 and self.battlesLeft == 5) or (self.battlesLeft == 1 and self.numBattles < 10):
            enemyTrainer = self.findMinibossBattleTrainer()
            switchToBattleGUI(userTrainer,enemyTrainer,self.master,[self.pokemonChosen,[self.battlesLeft,self.numBattles]],miniboss=enemyTrainer.name)
        else:
            switchToBattleGUI(userTrainer,enemyTrainer,self.master,[self.pokemonChosen,[self.battlesLeft,self.numBattles]])

    def findMinibossBattleTrainer(self):
        trainer = r.choice(miniboss) ##randomly selects a miniboss, then creates a list of pokemon for that trainer
        if trainer == 'Pedro': ##Ground
            enemyTrainer = battle.trainer('Pedro','Gym Leader','Pedro')
            pokemon = r.sample(['Quagsire','Garchomp','Gliscor','Krookodile','Swampert'],k=4)
        elif trainer == 'Ben': ##Steel
            enemyTrainer = battle.trainer('Ben','Gym Leader','Ben')
            pokemon = r.sample(['Excadrill','Ferrothorn','Lucario','Magnezone','Metagross','Scizor'],k=4)
        elif trainer == 'Sabrina': ##Psychic
            enemyTrainer = battle.trainer('Sabrina','Gym Leader','Sabrina')
            pokemon = r.sample(['Alakazam','Gallade','Slowbro','Slowking','Espeon','Metagross'],k=4)
        elif trainer == 'Falkner': ##Flying
            enemyTrainer = battle.trainer('Falkner','Gym Leader','Falkner')
            pokemon = r.sample(['Pidgeot','Crobat','Aerodactyl','Honchkrow','Talonflame'],k=4)
        elif trainer == 'Dalton': ##Poison
            enemyTrainer = battle.trainer('Dalton','Gym Leader','Dalton')
            pokemon = r.sample(['Amoonguss','Crobat','Gengar','Roserade','Toxicroak','Venusaur'],k=4)
            
        for x in range(4):
            P = battle.pokemon(pokemon[x],r.randint(58,63),enemyTrainer)
            enemyTrainer.addToTeam(x)
            physical = 0
            numPhysical = 0
            special = 0
            numSpecial = 0
            bulky = 0
            numStatus = 0
            for move in P.moves:
                if move[0].category == 'Physical':
                    physical += 1
                    numPhysical += 1
                elif move[0].category == 'Special':
                    special += 1
                    numSpecial += 1
                else:
                    bulky += 1
                    numStatus += 1

                if move[0].name in ['Bullet Punch','Close Combat','Dragon Dance','Mach Punch','Superpower','Swords Dance']:
                    bulky -= 1
                    physical += 1
                elif move[0].name in ['Draco Meteor','Leaf Storm','Nasty Plot','Overheat']:
                    bulky -= 1
                    special += 1
                elif move[0].name in ['Agility','Shell Smash']:
                    bulky -= 1
                    special += 1
                    physical += 1
                elif move[0].name in ['Calm Mind']:
                    special += 1
                    bulky += 1
                elif move[0].name in ['Amnesia','Hibernate','Hypnosis','Iron Defense','Light Screen','Protect','Rest','Reflect','Thunder Wave','Toxic','Will-O-Wisp']:
                    bulky += 2
                    physical -= 1
                    special -= 1
            if bulky > physical and bulky > special:
                if numPhysical + numSpecial <= 1:
                    P.ev = r.choice(EVSpreads['pure stall'])
                elif numPhysical >= 2:
                    P.ev = r.choice(EVSpreads['physical wall'])
                elif numSpecial >= 2:
                    P.ev = r.choice(EVSpreads['special wall'])
                else:
                    P.ev = r.choice(EVSpreads['mixed wall'])
            elif special > physical and special > bulky:
                if numPhysical == 0:
                    P.ev = r.choice(EVSpreads['special sweeper'])
                elif numPhysical >= 1:
                    P.ev = r.choice(EVSpreads['mixed attacker'])
            elif physical > special and physical > bulky:
                if numSpecial == 0:
                    P.ev = r.choice(EVSpreads['physical sweeper'])
                elif numSpecial >= 1:
                    P.ev = r.choice(EVSpreads['mixed attacker'])
            elif physical == special and physical > bulky:
                P.ev = r.choice(EVSpreads['mixed attacker'])
            else:
                P.ev = r.choice(EVSpreads['true balance'])
            P.statCalculate()
        return enemyTrainer

    def findBossBattleTrainer(self):
        trainer = r.choice(finalBoss) ##each boss trainer has a predefined set of moves and EVs for their Pokemon
                                        ##this function randomly picks a boss and creates their team using a predefined set of information
        if trainer == 'Ben':
            enemyTrainer = battle.trainer('Ben','Developer','Ben')
            pokemon = r.sample(['Gardevoir','Magnezone','Chandelure','Cloyster','Ferrothorn'],k=3)
            x = 0
            for P in pokemon:
                PKMN = battle.pokemon(P,random.randint(60,64),enemyTrainer)
                PKMN.iv = (31,31,31,31,31,31)
                if P == 'Gardevoir':
                    PKMN.forceMoves(['Moonblast','Psychic','Wish','Thunderbolt'])
                    PKMN.ev = [0,0,0,252,4,252]
                elif P == 'Magnezone':
                    PKMN.forceMoves(['Reflect','Thunder Wave','Thunderbolt','Flash Cannon'])
                    PKMN.ev = [0,0,100,252,158,0]
                elif P == 'Chandelure':
                    PKMN.forceMoves(['Minimize','Shadow Ball','Flamethrower','Energy Ball'])
                    PKMN.ev = [0,0,0,252,4,252]
                elif P == 'Cloyster':
                    PKMN.forceMoves(['Shell Smash','Pin Missile','Liquidation','Icicle Spear'])
                    PKMN.ev = [0,252,4,0,0,252]
                elif P == 'Ferrothorn':
                    PKMN.forceMoves(['Iron Defense','Power Whip','Gyro Ball','Iron Head'])
                    PKMN.ev = [4,252,252,0,0,0]
                    PKMN.iv = (31,31,31,31,31,0)
                PKMN.statCalculate()
                enemyTrainer.addToTeam(x)
                x+=1
            PKMN = battle.pokemon('Kyurem-B',67,enemyTrainer)
            enemyTrainer.addToTeam(3)
            PKMN.iv = (31,31,31,31,31,31)
            PKMN.forceMoves(['Dragon Dance','Fusion Bolt','Freeze Shock','Dragon Claw'])
            PKMN.ev = [0,252,4,0,0,252]
            PKMN.statCalculate()
        elif trainer == 'Cynthia':
            enemyTrainer = battle.trainer('Cynthia','Champion','Cynthia')
            pokemon = r.sample(['Roserade','Lucario','Spiritomb','Togekiss','Glaceon'],k=3)
            x = 0
            for P in pokemon:
                PKMN = battle.pokemon(P,random.randint(60,64),enemyTrainer)
                PKMN.iv = (31,31,31,31,31,31)
                if P == 'Roserade':
                    PKMN.forceMoves(['Leaf Storm','Sludge Bomb','Shadow Ball','Sleep Powder'])
                    PKMN.ev = [4,0,0,252,0,252]
                elif P == 'Lucario':
                    PKMN.forceMoves(['Close Combat','Dark Pulse','Stone Edge','Extreme Speed'])
                    PKMN.ev = [0,158,0,100,0,252]
                elif P == 'Spiritomb':
                    PKMN.forceMoves(['Sucker Punch','Protect','Will-O-Wisp','Rest'])
                    PKMN.ev = [252,0,129,0,129,0]
                elif P == 'Togekiss':
                    PKMN.forceMoves(['Air Slash','Aura Sphere','Shadow Ball','Nasty Plot'])
                    PKMN.ev = [100,0,75,252,75,0]
                elif P == 'Glaceon':
                    PKMN.forceMoves(['Ice Beam','Shadow Ball','Signal Beam','Freeze-Dry'])
                    PKMN.ev = [4,0,0,252,0,252]
                PKMN.statCalculate()
                enemyTrainer.addToTeam(x)
                x+=1
            PKMN = battle.pokemon('Garchomp',67,enemyTrainer)
            enemyTrainer.addToTeam(3)
            PKMN.iv = (31,31,31,31,31,31)
            PKMN.forceMoves(['Dragon Claw','Earthquake','Stone Edge','Swords Dance'])
            PKMN.statCalculate()
        return enemyTrainer

    def EV_enableButtons(self,index='no'):
        self.tabletCanvas.delete('tablet-data')
        if index != 'no':
            self.battleCanvas.tag_unbind('team-'+str(index),'<Enter>')
            self.battleCanvas.tag_unbind('team-'+str(index),'<Leave>')
            self.battleCanvas.tag_bind('team-'+str(index),'<Enter>',genFunc(self.team_hoverOver,index))
            self.battleCanvas.tag_bind('team-'+str(index),'<Leave>',self.team_hoverOff)
        for x in range(0,4):
            self.battleCanvas.tag_unbind('team-'+str(x),'<Button-1>')
            self.battleCanvas.itemconfig('team-'+str(x),state=NORMAL)
            self.battleCanvas.tag_bind('team-'+str(x),'<Button-1>',genFunc(self.EV_lockButtons,x))
        self.viewChoicesButton.config(text='Start Battle',bg='light green',command=genFunc(self.startBattle))

    def EV_disableButtons(self):
        for x in range(0,4):
            self.battleCanvas.itemconfig(self.teamIDs[x],state=DISABLED)

    def EV_lockButtons(self,index): ##index specifies the button that the user selected. i.e. index=3 implies the fourth button was clicked
        self.battleCanvas.config(cursor='arrow')
        for x in range(0,4):
            if x == index:
                self.battleCanvas.tag_unbind('team-'+str(index),'<Enter>')
                self.battleCanvas.tag_unbind('team-'+str(index),'<Leave>')
            else:
                self.battleCanvas.itemconfig(self.teamIDs[x],state=DISABLED)
        self.battleCanvas.tag_bind('team-'+str(index),'<Button-1>',genFunc(self.EV_enableButtons,index))
        self.battleCanvas.tag_bind('team-'+str(index),'<Enter>',self.EV_handCursor)
        self.battleCanvas.tag_bind('team-'+str(index),'<Leave>',self.EV_arrowCursor)
        self.tablet_editEVs(self.team[index])
        self.viewChoicesButton.config(text='Submit EVs',bg='#aec1db',command=genFunc(self.setEVs,index),state=ACTIVE)

    def setEVs(self,index):
        self.team[index].ev = [int(self.EVStringVar['HP'].get()),int(self.EVStringVar['Attack'].get()),int(self.EVStringVar['Defense'].get()),int(self.EVStringVar['Sp. Attack'].get()),int(self.EVStringVar['Sp. Defense'].get()),int(self.EVStringVar['Speed'].get())]
        self.team[index].statCalculate()
        self.EV_enableButtons(index)
        #self.tabletCanvas.itemconfig('tablet-current-stats',text='Current Stats: ' + str(self.team[index].stats))

    def EV_handCursor(self,event=False):
        self.battleCanvas.config(cursor='hand2')

    def EV_arrowCursor(self,event=False):
        self.battleCanvas.config(cursor='arrow')
        
#------------------------------------------------------------------------------------------------------------------------------#
           # '''Drafting!! This is all of the stuff required to be able to draft.'''
#------------------------------------------------------------------------------------------------------------------------------#

    def initDraft(self):
        self.roundsLeft = self.numRounds
        self.numberLeftInRound = self.pokemonPerRound
        self.pokemonAvailable = {}
        if self.pokemonChosen != []:
            self.pokemonChosen ##if here, then we've already got pokemonChosen and so are returning in between a battle
            self.battlesLeft -= 1
            self.initTeamCreation()
        else:
            self.pokemonChosen = []
            self.checkPokeballs()
            self.firstRoundOfDraft()
        #self.slideChoicesAcross(0,True)

    def firstRoundOfDraft(self):
        for count in range(0,6):
            if count < self.numberLeftInRound:
                self.pokemonAvailable[str(self.pokemonCoordsSouth[count])] = battle.pokemon(r.choice(pokemonInDraft),r.randint(50,60))  ##generate a random pack. the stats/moves are already generated randomly within the pokemon class
            else:
                self.pokemonAvailable[str(self.pokemonCoordsSouth[count])] = None
        q = battle.serviceQueue()
        q.add(['columnSeparation',genFunc(self.movePlatforms,'on','columnSeparation',False)])
        q.add([False,self.checkPokemonOut])
        q.add(['all-finished',self.processPokemonSendOut])   
        if self.roundsLeft > 2 or self.roundsLeft == 1: ##this is to take out the s of rounds if we aren't taking  about a plural
            q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft-1) + ' rounds after this, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
        else:
            q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft-1) + ' round left after this, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
        q.add(['activate-buttons',self.activateButtons])
        self.executeTurn(q)

    def executeTurn(self,q,lastID=False,textWasRunning=False): ##receives slightly different input than in the battle gui.
        ##in this one, we give it a list of lists in the form [ID,func] where the ID serves to identify which proc we need
        if self.taskFinished[str(lastID)] and not self.textRunning and not textWasRunning:
            if len(q.q) == 0:##used for two things. once when executing the main turn, and second when executing the
                #self.draft()
                return
            else:
                x = q.rem()
                lastID = x[0]
                x[1]() ##executes the second item in the list of whatever q returns
        if textWasRunning:
            k = genFunc(self.executeTurn,q,lastID,self.textRunning)
            self.master.after(200,k)
        else:
            k = genFunc(self.executeTurn,q,lastID,self.textRunning)
            self.master.after(5,k)

    def draft(self):
        for count in range(0,6):
            if count < self.numberLeftInRound:
                self.pokemonAvailable[str(self.pokemonCoordsSouth[count])] = battle.pokemon(r.choice(pokemonInDraft),r.randint(50,60))  ##generate a random pack. the stats/moves are already generated randomly within the pokemon class
                self.taskFinished[str(self.pokemonCoordsSouth[count])] = False
            elif count >= self.numberLeftInRound:                                                                                       ##packs go from 6->5->4 etc. so we need to fill the empty spaces with None (to tell program later what's going on)
                self.pokemonAvailable[str(self.pokemonCoordsSouth[count])] = None
        q = battle.serviceQueue()
        style = r.choice(self.platformMovementStyles)
        q.add([style,genFunc(self.movePlatforms,'off',style)])
        q.add([False,self.checkPokemonOut])
        q.add(['all-finished',self.processPokemonSendOut])                                           ##so we do it after the last one to finish
        if self.roundsLeft > 2 or self.roundsLeft == 1:                                                                                                         ##this is to take out the s of rounds if we aren't taking  about a plural
            q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft-1) + ' rounds left after this, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
        else:
            q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft-1) + ' round left after this, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
        q.add(['activate-buttons',self.activateButtons])
        self.executeTurn(q)

    def checkPokemonOut(self): ##this is a looping script that sets the system to finished when all of the pokemon
                                ##have appeared from their pokeballs in the drafting interface.
        self.taskFinished['all-finished'] = False
        c = 0
        for x in range(self.numberLeftInRound):
            try:
                if self.taskFinished[str(self.pokemonCoordsSouth[x])] == True:
                    c += 1
            except KeyError:
                print(self.pokemonCoordsSouth[x])
                break
        if c == self.numberLeftInRound:
            self.taskFinished['all-finished'] = True
            master.after(50,self.checkPokemonOut)
        else:
            master.after(50,self.checkPokemonOut)

    def processPokemonSendOut(self): ##procedurally plays the entrance animation for 
        count = 0
        for coords in self.pokemonCoordsSouth:
            self.taskFinished[str(coords)] = False
            if self.pokemonAvailable[str(coords)] != None:
                k = genFunc(self.enemyPokemonSendOut,0,0,coords)
                master.after(5+250*count,k)
            else:
                break
            count += 1
        
    def activateButtons(self): ##activates the buttons needed to add pokemon to the team.
                                ##i.e. the buttons when you hover over a pokemon in the drafting area.
        self.taskFinished['activate-buttons'] = False
        for coords in self.pokemonCoordsSouth:
            if self.pokemonAvailable[str(coords)] != None:
                k = genFunc(self.selectPokemon,coords)
                self.battleCanvas.tag_bind(self.pokemonCanvasItemVars[str(coords)],'<Button-1>',k)
                k = genFunc(self.handCursor,coords,self.pokemonAvailable[str(coords)])
                self.battleCanvas.tag_bind(self.pokemonCanvasItemVars[str(coords)],'<Enter>',k)
                self.battleCanvas.tag_bind(self.pokemonCanvasItemVars[str(coords)],'<Leave>',self.arrowCursor)
            else:
                break
        self.viewChoicesButton.config(state=ACTIVE,cursor='hand2')
        self.taskFinished['activate-buttons'] = True

    def handCursor(self,coords,pokemon): ##updates the cursor to be a hand when a user is over an image
        self.isCursorOnPokemon = coords
        self.battleCanvas.config(cursor='hand2') ##changes to the normal hand. hand1 is truly horrific, so I use hand2
        self.boxSelection(coords) ##see below
        self.tablet_displayEnemyPokemon(pokemon)

    def arrowCursor(self,event=False):
        self.isCursorOnPokemon = False
        self.tabletCanvas.delete('tablet-data')
        self.battleCanvas.config(cursor='arrow')

    def boxSelection(self,coords,offset=0,sign=2.5,posOrNeg=-0.5): ##pops up a small green box around the user's choice
        try:
            self.boxImageTR
        except:
            self.boxImageTR = ImageTk.PhotoImage(Image.open(assets['sBoxTR']).resize((30,30)))
            self.boxImageTL = ImageTk.PhotoImage(Image.open(assets['sBoxTL']).resize((30,30)))
            self.boxImageBR = ImageTk.PhotoImage(Image.open(assets['sBoxBR']).resize((30,30)))
            self.boxImageBL = ImageTk.PhotoImage(Image.open(assets['sBoxBL']).resize((30,30)))
        self.battleCanvas.delete('selection-box')
        self.battleCanvas.create_image(coords[0]-81.25-offset,coords[1]-111.25-offset,image=self.boxImageTL,anchor=S,tags=('selection-box'))
        self.battleCanvas.create_image(coords[0]+81.25+offset,coords[1]-111.25-offset,image=self.boxImageTR,anchor=S,tags=('selection-box'))
        self.battleCanvas.create_image(coords[0]-81.25-offset,coords[1]+31.25+offset,image=self.boxImageBL,anchor=S,tags=('selection-box'))
        self.battleCanvas.create_image(coords[0]+81.25+offset,coords[1]+31.25+offset,image=self.boxImageBR,anchor=S,tags=('selection-box'))
        if sign == -2.5:
            posOrNeg = 0.5
        elif sign == 2.5:
            posOrNeg = -0.5
        if self.isCursorOnPokemon == coords:
            k = genFunc(self.boxSelection,coords,offset+sign,sign+posOrNeg,posOrNeg)
            master.after(35,k)
        else:
            self.battleCanvas.delete('selection-box')

    def deactivateButtons(self):
        self.tabletCanvas.delete('tablet-data')
        self.isCursorOnPokemon = False
        self.battleCanvas.config(cursor='arrow')
        for coords in self.pokemonCoordsSouth:
            if self.pokemonAvailable[str(coords)] != None:
                self.battleCanvas.tag_unbind(self.pokemonCanvasItemVars[str(coords)],'<Button-1>')
                self.battleCanvas.tag_unbind(self.pokemonCanvasItemVars[str(coords)],'<Enter>')
                self.battleCanvas.tag_unbind(self.pokemonCanvasItemVars[str(coords)],'<Leave>')
        self.viewChoicesButton.config(state=DISABLED,cursor='arrow')

    def selectPokemon(self,coords):
        self.deactivateButtons()
        self.pokemonChosen.append(self.pokemonAvailable[str(coords)])
        q = battle.serviceQueue()
        q.add([False,genFunc(self.runText,'You selected ' + self.pokemonAvailable[str(coords)].name+'!')])
        k = genFunc(self.switchEnemy,0,0,coords,True)
        q.add([str(coords),k])                                          ##we retrieve the one that was chosen so that the user can tell their choice has been registered. also looks pretty with the fade out on the next line.
        k = genFunc(self.fadeOutChoice,coords)
        q.add(['fade-out-choice',k])                                    ##this is a nice anim, idk. I might enjoy it too much.
        k = genFunc(self.processPokemonRetrieval,coords)
        if self.pokemonCoordsSouth[self.numberLeftInRound-1] == coords: ##the list form of [funcID,func] will finish immediately if we call it on the one we've already retrieved
            if self.numberLeftInRound == 1: ##calling self.pokemonCoordsSouth[1-2] will spit an error as we don't have a pokemon sent out for the -1th space (i.e. 6th space)
                pass
            else:
                q.add([self.pokemonCoordsSouth[self.numberLeftInRound-2],k])
        else:
            q.add([self.pokemonCoordsSouth[self.numberLeftInRound-1],k]) ##or it's not the last one so we don't need to worry
        self.numberLeftInRound -= 1                                      ##so we need to tick down the numnber left in round and our num of rounds if applicable
        if self.numberLeftInRound == 0:
            self.roundsLeft -= 1
            if self.roundsLeft == 0: ## and we've finished the draft if we've gotten here as we've got 0 rounds left and 1 pokemon left in the round.
                style = r.choice(self.platformMovementStyles)
                q.add([style,genFunc(self.movePlatforms,'off',style,0,False)])
                q.add([False,genFunc(self.slideChoicesAcross,0,True)])
                self.executeTurn(q)
                return
            self.numberLeftInRound = self.pokemonPerRound
        q.add([False,self.draft])
        self.executeTurn(q)

    def processPokemonRetrieval(self,coordsChosen): ##this function is to manage how the pokemon are brought back after a selection
        count = 0
        for coords in self.pokemonCoordsSouth:
            self.taskFinished[str(coords)] = False
            if self.pokemonAvailable[str(coords)] != None: ##can't really retrieve a None pokemon, can we?
                if coordsChosen == coords: ##if it has been chosen, we've already retrieved it separately so we skip
                    count -= 1
                else: ##else retrieve it
                    k = genFunc(self.switchEnemy,0,0,coords)
                    master.after(5+250*count,k)
            else:
                break
            count += 1
           
#------------------------------------------------------------------------------------------------------------------------------#
            #'''Animations!! So basically anything that moves on the screen'''
#------------------------------------------------------------------------------------------------------------------------------#

    def enemyPokemonSendOut(self,count=0,ready=0,coords=False):
        ##so this is for when the pokemon appear on screen for you to choose
        ##i have to use a lot of +str(coords) or var[str(coords)] as python makes it so that the images must be stored as vars or may be inadvertently deleted by python's memory cleanup methods
        ##there was too much I needed to change from the original (this is taken from the battle gui file) so I've had to redefine it here. The comments and description from before apply here also.
        if count == 0 and not ready:
            self.taskFinished[str(coords)] = False
            self.EpokeballImageFile[str(coords)] = Image.open(pokeballs['Pokeball'])
            self.EpokeballImageFile[str(coords)].seek(0)
            self.EpokeballImage[str(coords)] = ImageTk.PhotoImage(self.EpokeballImageFile[str(coords)].resize((24,35)))
            k = genFunc(self.enemyPokemonSendOut,count+1,ready,coords)
            master.after(250,k)
            self.Epokeball = self.battleCanvas.create_image(coords[0],coords[1],image=self.EpokeballImage[str(coords)],anchor=S,tags=('enemy-pokeball'+str(coords)))
        elif count < 3 and not ready:
            self.EpokeballImageFile[str(coords)].seek(count)
            self.EpokeballImage[str(coords)] = ImageTk.PhotoImage(self.EpokeballImageFile[str(coords)].resize((24,35)))
            self.battleCanvas.delete('enemy-pokeball'+str(coords))
            self.battleCanvas.create_image(coords[0],coords[1],image=self.EpokeballImage[str(coords)],anchor=S,tags=('enemy-pokeball'+str(coords)))
            if count == 2:
                k = genFunc(self.enemyPokemonSendOut,count,1,coords)
            else:
                k = genFunc(self.enemyPokemonSendOut,count+1,ready,coords)
            master.after(250,k)
        elif ready == 1:
            self.EpokemonImageFile[str(coords)] = Image.open(pokemon[self.pokemonAvailable[str(coords)].species])
            self.EpokemonImage[str(coords)] = ImageTk.PhotoImage(self.EpokemonImageFile[str(coords)].resize((1,1)))
            self.Epokemon[str(coords)] = self.battleCanvas.create_image(coords[0],coords[1],image=self.EpokemonImage[str(coords)],tags=('enemy-pokemon'+str(coords)))
            k = genFunc(self.enemyPokemonSendOut,count,5,coords)
            master.after(50,k)
        elif ready <= 100 and ready > 1: ##ready used as a size modifier
            self.EpokeballImageFile[str(coords)] = self.EpokeballImageFile[str(coords)].resize((int(24*(100-ready)/100+1),int(35*(100-ready)/100+1)))
            self.EpokeballImage[str(coords)] = ImageTk.PhotoImage(self.EpokeballImageFile[str(coords)])
            self.battleCanvas.delete('enemy-pokeball'+str(coords))
            self.battleCanvas.create_image(coords[0],coords[1],anchor=S,image=self.EpokeballImage[str(coords)],tags=('enemy-pokeball'+str(coords)))

            self.EpokemonImage[str(coords)] = ImageTk.PhotoImage(self.EpokemonImageFile[str(coords)].resize(((int(math.log(ready)/math.log(100)*130)),int(math.log(ready)/math.log(100)*130)))) ##basically to make it grow up quickly then slow down- i use logs. woohoo a use for a level maths
            self.battleCanvas.delete('enemy-pokemon'+str(coords))
            self.battleCanvas.create_image(coords[0],coords[1]+5,anchor=S,image=self.EpokemonImage[str(coords)],tags=('enemy-pokemon'+str(coords)))
            
            k = genFunc(self.enemyPokemonSendOut,count,ready+10,coords)
            master.after(20,k)
        elif ready == 105: ##ready used as a position modifier
            self.battleCanvas.delete('enemy-pokeball'+str(coords))
            k = genFunc(self.enemyPokemonSendOut,count,140,coords)
            master.after(100,k)
        elif ready >= 140: ##loads the next gif in the pokemon's entry anim until an end of file... at which point it just leaves it
            try:
                self.battleCanvas.delete('enemy-pokemon'+str(coords))
                self.EpokemonImageFile[str(coords)].seek(ready-140)
                self.EpokemonImage[str(coords)] = ImageTk.PhotoImage(self.EpokemonImageFile[str(coords)].resize((130,130)))
                self.pokemonCanvasItemVars[str(coords)] = self.battleCanvas.create_image(coords[0],coords[1]+10,anchor=S,image=self.EpokemonImage[str(coords)],tags=('enemy-pokemon'+str(coords)))
                k = genFunc(self.enemyPokemonSendOut,count,ready+1,coords)
                master.after(50,k)
            except EOFError:
                self.EpokemonImageFile[str(coords)].seek(ready-140-2)
                self.EpokemonImage[str(coords)] = ImageTk.PhotoImage(self.EpokemonImageFile[str(coords)].resize((130,130)))
                self.pokemonCanvasItemVars[str(coords)] = self.battleCanvas.create_image(coords[0],coords[1]+10,anchor=S,image=self.EpokemonImage[str(coords)],tags=('enemy-pokemon'+str(coords)))
                self.taskFinished[str(coords)] = True
                return

    def switchEnemy(self,tick=0,count=0,coords=False,capture=False):
        ##again this function was snatched from my other battle gui file.
        ##tick refers to pokeball and pokemon,
        ##count is for the sprite anim and things
        if tick == 0:
            self.taskFinished[str(coords)] = False
            self.EpokeballImageFile[str(coords)] = Image.open(pokeballs['Pokeball'])
            self.EpokeballImageFile[str(coords)].seek(2)
            k = genFunc(self.switchEnemy,tick+1,count,coords,capture)
            self.master.after(5,k)
        elif 1 <= tick <= 96:
            self.EpokeballImage[str(coords)] = self.EpokeballImageFile[str(coords)].resize((int(23*tick/96+1),int(35*tick/96+1)))
            self.EpokeballImage[str(coords)] = ImageTk.PhotoImage(self.EpokeballImage[str(coords)])
            self.battleCanvas.delete('enemy-pokeball'+str(coords))
            self.battleCanvas.create_image(coords[0],coords[1],anchor=S,image=self.EpokeballImage[str(coords)],tags=('enemy-pokeball'+str(coords)))

            self.EpokemonImage[str(coords)] = ImageTk.PhotoImage(self.EpokemonImageFile[str(coords)].resize((int(1+(100-tick)/100*130),int(1+(100-tick)/100*130))))
            self.battleCanvas.delete('enemy-pokemon'+str(coords))
            self.pokemonCanvasItemVars[str(coords)] = self.battleCanvas.create_image(coords[0],coords[1]+10,anchor=S,image=self.EpokemonImage[str(coords)],tags=('enemy-pokemon'+str(coords)))

            self.master.update()
            k = genFunc(self.switchEnemy,tick+1,count,coords,capture)
            self.master.after(2,k)
        elif tick == 97:
            self.battleCanvas.delete(self.pokemonCanvasItemVars[str(coords)])
            self.master.update()
            k = genFunc(self.switchEnemy,tick+1,1,coords,capture)
            self.master.after(5,k)
        elif count <= 3 and tick == 98:
            self.EpokeballImageFile[str(coords)].seek(3-count)
            self.EpokeballImage[str(coords)] = ImageTk.PhotoImage(self.EpokeballImageFile[str(coords)].resize((24,35)))
            self.battleCanvas.delete('enemy-pokeball'+str(coords))
            t = list(self.coordsDict[str(coords)])
            t.append('enemy-pokeball'+str(coords))
            self.pokeballCanvasItemVars[str(coords)] = self.battleCanvas.create_image(coords[0],coords[1],image=self.EpokeballImage[str(coords)],anchor=S,tags=tuple(t))
            self.battleCanvas.delete('enemy-pokemon'+str(coords))
            k = genFunc(self.switchEnemy,tick,count+1,coords,capture)
            self.master.after(250,k)
        elif 3 < count < 40:
            self.taskFinished[str(coords)] = True
            return

    def movePlatforms(self,direction,style=False,loop=0,firstTime=True):
        if direction == 'off': 
            self.taskFinished[style] = False
            if not style:
                style = r.choice(self.platformMovementStyles) ##the style is randomly selected.
            if style == 'columnSeparation': ##the columns move apart in opposite directions
                self.battleCanvas.move('platformC1',0,10) ##moves the elements in one column
                self.battleCanvas.move('platformC2',0,-10)##as above but for the other column
                if loop == 52:
                    if firstTime:
                        self.battleCanvas.move('platformC1',0,-1060) ##if this is the firstTime executing movePlatforms for this instance, move the platforms to the other side of screen (offscreen)...
                        self.battleCanvas.move('platformC2',0,1060)
                        self.checkPokeballs()
                        k = genFunc(self.movePlatforms,'on',style,0,False) ##...and call a function to move them on.
                        master.after(30,k)
                    else:
                        self.taskFinished[style] = True
                    return ##either way, we don't want to be going to the end of the sequence or we'll call this function going off again which would mess us up. so we return to avoid that. see ##<-- This is why we return
            elif style == 'rowSeparation':
                self.battleCanvas.move('platformR1',10,0)
                self.battleCanvas.move('platformR2',-10,0)
                self.battleCanvas.move('platformR3',10,0)
                if loop == 52:
                    if firstTime:
                        self.battleCanvas.move('platformR1',-1040,0)
                        self.battleCanvas.move('platformR2',1040,0)
                        self.battleCanvas.move('platformR3',-1040,0)
                        self.checkPokeballs()
                        k = genFunc(self.movePlatforms,'on',style,0,False)
                        master.after(30,k)
                    else:
                        self.taskFinished[style] = True
                    return
            elif style == 'diagonalSeparation': ##to keep them moving at the same speed, I'm ensuring that their vectors have magnitude 5; i.e. for C1R1 we move 4 across and 3 up, so sqrt(4^2+3^2) = 5 etc. pythagoras
                self.battleCanvas.move('platformC1R1',-4,-3)
                self.battleCanvas.move('platformC2R1',4,-3)
                self.battleCanvas.move('platformC1R2',-5,0)
                self.battleCanvas.move('platformC2R2',5,0)
                self.battleCanvas.move('platformC1R3',-4,3)
                self.battleCanvas.move('platformC2R3',4,3)
                if loop == 60:
                    if firstTime:
                        self.checkPokeballs()
                        k = genFunc(self.movePlatforms,'on',style,0,False)
                        master.after(30,k)
                    else:
                        self.taskFinished[style] = True
                    return
            k = genFunc(self.movePlatforms,direction,style,loop+1,firstTime)
            master.after(30,k) ##<-- This is why we return when loop == 52. Otherwise we weave two conflicting functions and cause mayhem- moving on and moving off.
        elif direction == 'on': ##this could be merged with the other half of the function but because of diagonalSeparation, it needs to be separate
            self.taskFinished[style] = False
            if not style:
                style = r.choice(self.platformMovementStyles)
                self.taskFinished[style] = False
            if style == 'columnSeparation':
                self.battleCanvas.move('platformC1',0,10)
                self.battleCanvas.move('platformC2',0,-10)
                if loop == 52:
                    if firstTime:
                        self.battleCanvas.move('platformC1',0,-1040)
                        self.battleCanvas.move('platformC2',0,1040)
                        self.checkPokeballs()
                        k = genFunc(self.movePlatforms,'off',style,0,False)
                    else:
                        self.taskFinished[style] = True
                    return
            elif style == 'rowSeparation':
                self.battleCanvas.move('platformR1',10,0)
                self.battleCanvas.move('platformR2',-10,0)
                self.battleCanvas.move('platformR3',10,0)
                if loop == 50:
                    if firstTime:
                        self.battleCanvas.move('platformR1',-1040,0)
                        self.battleCanvas.move('platformR2',1040,0)
                        self.battleCanvas.move('platformR3',-1040,0)
                        self.checkPokeballs()
                        k = genFunc(self.movePlatforms,style,'off',0,False)
                        master.after(30,k)
                    else:
                        self.taskFinished[style] = True
                    return
            elif style == 'diagonalSeparation':
                self.battleCanvas.move('platformC1R1',4,3)
                self.battleCanvas.move('platformC2R1',-4,3)
                self.battleCanvas.move('platformC1R2',5,0)
                self.battleCanvas.move('platformC2R2',-5,0)
                self.battleCanvas.move('platformC1R3',4,-3)
                self.battleCanvas.move('platformC2R3',-4,-3)
                if loop == 60:
                    if firstTime:
                        self.checkPokeballs()
                        k = genFunc(self.movePlatforms,'off',style,0,False)
                        master.after(30,k)
                    else:
                        self.taskFinished[style] = True
                    return
            k = genFunc(self.movePlatforms,direction,style,loop+1,False)
            master.after(30,k)

    def checkPokeballs(self): ##adds the pokeballs to the platforms so that they appear to come in with them.
        for x in range(0,6):
            self.battleCanvas.delete(self.pokeballCanvasItemVars[str(self.pokemonCoordsSouth[x])])
        ID = ('platformC1R1','platformC1R2','platformC1R3','platformC2R1','platformC2R2','platformC2R3') ##init these tuples to be able to a) get coords of the platforms and b) give the pokeballs all tags pertaining to the movement of the platforms.
        cID = ('platformC1','platformC1','platformC1','platformC2','platformC2','platformC2')
        rID = ('platformR1','platformR2','platformR1','platformR2','platformR1','platformR2')
        for x in range(0,self.numberLeftInRound):
            c = self.battleCanvas.coords(ID[x])
            self.pokeballCanvasItemVars[str(self.pokemonCoordsSouth[x])] = self.battleCanvas.create_image(c[0],c[1],anchor=S,image=self.EpokeballImage[str(self.pokemonCoordsSouth[x])],tags=(ID[x],cID[x],rID[x],'enemy-pokeball'+str(self.pokemonCoordsSouth[x])))

    def fadeOutChoice(self,coords,percentAlpha=95):
        if percentAlpha == 95:
            self.taskFinished['fade-out-choice'] = False
            self.battleCanvas.delete(self.pokeballCanvasItemVars[str(coords)])
        self.EpokeballImageFile[str(coords)] = Image.open('assets/pokeballs/pokeballtransparent/pokeball'+str(percentAlpha)+'.png')
        self.alphaPokeball = ImageTk.PhotoImage(self.EpokeballImageFile[str(coords)].resize((24,35)))
        self.battleCanvas.delete('enemy-pokeball'+str(coords))
        self.battleCanvas.create_image(coords[0],coords[1],image=self.alphaPokeball,anchor=S,tags=('enemy-pokemon'+str(coords)))
        if percentAlpha > 0:
            k = genFunc(self.fadeOutChoice,coords,percentAlpha-5)
            master.after(70,k)
        else:
            self.taskFinished['fade-out-choice'] = True
#------------------------------------------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------------------------------------------#

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





        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
        ###############################################################################################################################################
                



class app:
    ##This is the main app - the one used for battling, which is where users will spend the majority of their time.
    def __init__(self,master,arena,receiveInfo,megaboss=False,miniboss=False):
        self.processesComplete = 0
        self.windowClosed = False
        master.protocol("WM_DELETE_WINDOW",self.on_closing) ##sets the function to be called when the window is closed to 'self.on_closing'
                                                            ##this turns off the music and closes tkinter.

        if receiveInfo != False: ##this is to allow the system to receive a number of battles left so it can be fed back to the drafting menu. to keep track of the desired number of battles
            self.pokemonChosen = receiveInfo[0]
            self.numBattles = receiveInfo[1]
        else:
            self.pokemonChosen,self.numBattles = False,False

        self.megaboss = megaboss
        self.miniboss = miniboss
        
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
        #master.after(1000,genFunc(self.endBattle,'win'))
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
            if len(temp+word) > 50:
                res.append(temp)
                temp = word
            else:
                temp += ' '+word
        if temp != '':
            res.append(temp)
        return res
#------------------------------------------------------------------------------------------------------------------------------#

    def endBattle(self,result,count=-1):
        if count == -1:
            mixer.music.fadeout(1000)
            master.after(1000,genFunc(self.endBattle,result,0))
        elif count == 0:
            if result == 'win':
                if self.megaboss:
                    mixer.music.load('music/victoryMegaboss.mp3')
                elif self.miniboss:
                    mixer.music.load('music/victoryMiniboss.mp3')
                else:
                    mixer.music.load('music/victory.mp3')
            else:
                mixer.music.load('music/lose.mp3')
            mixer.music.play(-1)
            master.after(25,genFunc(self.endBattle,result,1))
        elif count > 0 and count <= 50:
            self.battleCanvas.delete('fade')
            self.black = ImageTk.PhotoImage(Image.open('assets/black/black'+str(count*5)+'.png').resize((500,500)))
            self.battleCanvas.create_image(0,0,anchor=NW,image=self.black,tags=('fade'))
            master.after(25,genFunc(self.endBattle,result,count+1))
        elif count >= 51 and count <= 75:
            self.battleCanvas.delete('battle-result')
            self.result = ImageTk.PhotoImage(Image.open('assets/battleEnd/'+result+str(count-51)+'.png').resize((129,60)))
            self.battleCanvas.create_image(240,175,anchor="center",image=self.result,tags=('battle-result'))
            master.after(25,genFunc(self.endBattle,result,count+1))
        elif count == 76:
            master.after(475+500,genFunc(self.endBattle,result,count+1))
        else:
            if self.numBattles[0] <= 0 or result == 'lose':
                self.battleCanvas.create_text(240,280,text='Press Enter to Return to Menu',fill='white',font=self.DPPtFont,tags=('enter-text'))
            else:
                self.battleCanvas.create_text(240,280,text='Press Enter to Continue',fill='white',font=self.DPPtFont,tags=('enter-text'))
            if self.numBattles[0] > 0 and result == 'win':
                self.battleCanvas.create_text(240,320,text='Battles Left: '+str(self.numBattles[0]-1),fill='white',font=self.DPPtFont,tags=('enter-text'))
            #else:
            #    self.battleCanvas.create_text(240,320,text='You won the tournament!',fill='white',font=self.DPPtFont,tags=('enter-text'))
            self.enterNotPressed = True
            self.flashTextInAndOut(result)
            self.master.bind('<Return>',genFunc(self.returnToDraft,result))

    def flashTextInAndOut(self,result,M=0): ##precondition: self.enterNotPressed must be defined as a boolean
        if self.enterNotPressed:
            if M == 1:
                self.battleCanvas.delete('enter-text')
                master.after(1000,genFunc(self.flashTextInAndOut,0))
            else:
                if self.numBattles[0] > 0 and result == 'win':
                    self.battleCanvas.create_text(240,320,text='Battles Left: '+str(self.numBattles[0]-1),fill='white',font=self.DPPtFont,tags=('enter-text'))
                    self.battleCanvas.create_text(240,280,text='Press Enter to Continue',fill='white',font=self.DPPtFont,tags=('enter-text'))
                elif result == 'lose' or self.numBattles[0] <= 0:
                    self.battleCanvas.create_text(240,280,text='Press Enter to Return to Menu',fill='white',font=self.DPPtFont,tags=('enter-text'))
                #else:
                #    self.battleCanvas.create_text(240,320,text='You won the tournament!',fill='white',font=self.DPPtFont,tags=('enter-text'))
                master.after(1000,genFunc(self.flashTextInAndOut,0))

    def returnToDraft(self,result,count=0):
        if count == 0:
            self.enterNotPressed = False
            mixer.music.fadeout(2000)
            self.battleCanvas.delete('enter-text')
            self.master.after(50,genFunc(self.returnToDraft,result,1))
        elif 0 < count <= 10: ##flash text in and out repeatedly
            if count % 2 == 1:
                if result == 'win':
                    if self.numBattles[0] > 0:
                        self.battleCanvas.create_text(240,280,text='Press Enter to Continue',fill='white',font=self.DPPtFont,tags=('enter-text'))
                        self.battleCanvas.create_text(240,320,text='Battles Left: '+str(self.numBattles[0]-1),fill='white',font=self.DPPtFont,tags=('enter-text'))
                    else:
                        self.battleCanvas.create_text(240,280,text='Press Enter to Return to Menu',fill='white',font=self.DPPtFont,tags=('enter-text'))
                elif result == 'lose':
                    self.battleCanvas.create_text(240,280,text='Press Enter to Return to Menu',fill='white',font=self.DPPtFont,tags=('enter-text'))
                self.master.after(100,genFunc(self.returnToDraft,result,count+1))
            else:
                self.battleCanvas.delete('enter-text')
                master.after(100,genFunc(self.returnToDraft,result,count+1))
        elif 11 <= count <= 35:
            self.battleCanvas.delete('battle-result')
            self.result = ImageTk.PhotoImage(Image.open('assets/battleEnd/'+result+str(35-count)+'.png').resize((129,60)))
            self.battleCanvas.create_image(240,175,anchor="center",image=self.result,tags=('battle-result'))
            self.master.after(40,genFunc(self.returnToDraft,result,count+1))
        elif count == 36:
            self.battleFrame.place_forget()
            self.pokedexFrame.place_forget()
            self.textFrame.place_forget()
            self.buttonFrame.place_forget()
            if result == 'lose' or self.numBattles[0] == 0:
                switchToMenuGUI(master)
            elif result == 'win':
                switchToDraftingGUI([self.pokemonChosen,self.numBattles],master)##ben the relevant information needs to included-i.e. receiveInfo
        
    
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
            temp = icons[str(self.arena.getUserSpecies(str(count)))]
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
            if self.arena.userTrainer.team[str(count)] != None:
                k = genFunc(self.tablet_displayEnemyPokemon,self.arena.userTrainer.team[str(count)])
                button.bind('<Enter>',k)
                if self.arena.userTrainer.team[str(count)].fainted == False and count != self.arena.userTrainer.active:
                    k = genFunc(self.receiveUserInput, ['switch',count,'user'])
                    button.config(state=ACTIVE,command=k)
                elif self.arena.userTrainer.team[str(count)].fainted == True:
                    button.config(cursor='arrow')
                else:
                    button.config(cursor='arrow')
            count += 1
        master.update()

    def EOTSwitchButtons(self): ##these are used if a pokemon faints. User must switch in at end of turn.
        self.taskFinished = False
        count = 0
        for button in self.switchButtons:
            print('config button eotswtichbuttons')
            if count != self.arena.userTrainer.active and self.arena.userTrainer.team[str(count)] != None and self.arena.userTrainer.team[str(count)].fainted == False:
                print(button)
                k = genFunc(self.arena.setUserSwitch,count)
                button.config(state=ACTIVE,command=k)
            count += 1
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

        enemyActive = self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)]
        userActive = self.arena.userTrainer.team[str(self.arena.userTrainer.active)]
        print('Evs: ',userActive.ev)
        enemyInput = None
        if self.arena.enemyTrainer.powerLevel == 'regular':
            moveCount = 0

            ##use status moves on t1 of a pkmn swapping in, and supereffective attacking moves otherwise.
            for move in enemyActive.moves:
                if enemyActive.switchedInThisTurn:
                    if move[0].name == 'Fake Out':
                        enemyInput = ('attack',self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].moves[moveCount][0],'enemy')
                        break
                    elif move[0].category == 'Status':
                        enemyInput = ('attack',self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].moves[moveCount][0],'enemy')
                        break
                else:
                    if move[0].name == 'Fake Out':
                        continue
                    else:
                        if move[0].category != 'Status' and self.arena.typeModifiers(enemyActive,userActive,move[0])[1] == 2:
                            enemyInput = ('attack',self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].moves[moveCount][0],'enemy')
                            break
                moveCount += 1

            moveCount = 0
            if enemyInput == None:
                for move in enemyActive.moves:
                    if move[0].category != 'Status' and self.arena.typeModifiers(enemyActive,userActive,move[0])[1] == -1:
                        enemyInput = ('attack',self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].moves[moveCount][0],'enemy')
                    moveCount += 1

            if enemyInput == None:
                move = random.randint(0,3)
                enemyInput = ('attack',self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].moves[move][0],'enemy')
    

        elif self.arena.enemyTrainer.powerLevel == 'dumb':
            enemyInput = random.choice(['attack','attack','attack','attack','attack'])
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
            T = threading.Thread(target=genFunc(playsound,'sounds/sendin.mp3'))
            T.start()
            self.EpokemonImageFile = Image.open(pokemon[self.arena.findActiveName(self.arena.enemyTrainer)])
            self.EpokemonImage = ImageTk.PhotoImage(self.EpokemonImageFile.resize((1,1)))
            self.Epokemon = self.battleCanvas.create_image(350,75,image=self.EpokemonImage,tags=('enemy-pokemon'))
            k = genFunc(self.enemyPokemonSendOut,count,5)
            master.after(500,k)
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
            #mixer.Channel(1).play(mixer.Sound('cries/'+self.arena.findActiveName(self.arena.enemyTrainer)+'.wav'))
            T = threading.Thread(target=genFunc(playsound,'cries/'+self.arena.findActiveName(self.arena.enemyTrainer)+'.wav'))
            T.start()
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
                self.EpokemonImageFile.seek(ready-140-1)
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
                j = self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].statusCondition
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
            T = threading.Thread(target=genFunc(playsound,'sounds/sendin.mp3'))
            T.start()
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
        elif count > 100 and count <= 120:
            if count == 101:
                #mixer.Channel(1).play(mixer.Sound('cries/'+self.arena.findUserActive()+'.wav'))
                T = threading.Thread(target=genFunc(playsound,'cries/'+self.arena.findUserActive()+'.wav'))
                T.start()
            self.battleCanvas.move('user-pokemon',(-1) ** count * 15,0)
            k = genFunc(self.userPokemonAnim,count+1)
            master.after(int(125*math.log(count-100)/math.log(30)),k)
        elif count == 121:
            self.moveInUserHPBar()

    def moveInUserHPBar(self,tick=0,dontMarkTaskFinished=False): ##this function moves all of the user's HP bar elements (the green/yellow/red
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
            k = genFunc(self.moveInUserHPBar,1,dontMarkTaskFinished)
            master.after(5,k)
        else:
            if tick < 46:
                self.battleCanvas.move('user-hp',-5,0)
                k = genFunc(self.moveInUserHPBar,tick+1,dontMarkTaskFinished)
                master.after(5,k)
            else:
                if self.battleStart:
                    self.updateButtons()
                self.battleStart = False
                if not dontMarkTaskFinished:
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
            mixer.Channel(2).play(mixer.Sound('cries/'+self.arena.findActiveName(self.arena.userTrainer)+'.wav'))
            k = genFunc(self.userPokemonFaint,1)
            master.after(2000,k)
        elif count > 0 and count <=45:
            if count == 1:
                self.moveOutUserHPBar()
                T = threading.Thread(target=genFunc(playsound,'sounds/faint.mp3'))
                T.start()
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
            mixer.Channel(2).play(mixer.Sound('cries/'+self.arena.findActiveName(self.arena.enemyTrainer)+'.wav'))
            master.after(2000,k)
        if count > 0 and count <= 150:
            if count == 1:
                self.moveOutEnemyHPBar()
                T = threading.Thread(target=genFunc(playsound,'sounds/faint.mp3'))
                T.start()
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
    def HPUpdateEnemy(self,newHP,start=1,flashing=0,updateInGui=False,effectiveness='regular'):
        if start:
            self.taskFinished = False
            self.lastRatio = self.printedEnemyHP / self.EnemyMaxHP ##save original HP ratio
            if self.printedEnemyHP <= newHP:
                T = threading.Thread(target=genFunc(playsound,'sounds/heal.mp3'))
                T.start()
                k = genFunc(self.HPUpdateEnemy,newHP,0,15,updateInGui) ##if we are restoring HP, we skip flashing
                master.after(5,k)
            else:
                if effectiveness == 'super':
                    T = threading.Thread(target=genFunc(playsound,'sounds/superhit.mp3'))
                    T.start()
                elif effectiveness == 'weak':
                    T = threading.Thread(target=genFunc(playsound,'sounds/weakhit.mp3'))
                    T.start()
                else:
                    T = threading.Thread(target=genFunc(playsound,'sounds/normalhit.mp3'))
                    T.start()
                k = genFunc(self.HPUpdateEnemy,newHP,0,1,updateInGui)
                master.after(5,k)
        elif flashing%2==1 and flashing < 9:
            self.battleCanvas.delete('enemy-pokemon')
            k = genFunc(self.HPUpdateEnemy,newHP,0,flashing+1,updateInGui)
            master.after(50,k)
        elif flashing%2==0 and flashing < 9:
            self.battleCanvas.create_image(350,180,anchor=S,image=self.EpokemonImage,tags=('enemy-pokemon'))
            k = genFunc(self.HPUpdateEnemy,newHP,0,flashing+1,updateInGui)
            master.after(100,k)
        else:
            if self.printedEnemyHP > newHP: ##these if/elif/else are used for determining whether we are increasing
                                            ##decreasing or done
                self.printedEnemyHP -= 1
            elif self.printedEnemyHP < newHP:
                self.printedEnemyHP += 1
            else:
                if updateInGui:
                    self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].takeDamage(self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].hp-newHP)
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
            k = genFunc(self.HPUpdateEnemy,newHP,0,flashing,updateInGui)
            master.after(20,k)

    def HPUpdateUser(self,newHP,start=1,flashing=0,updateInGui=False,effectiveness='regular'):
        if start:
            print('started')
            self.taskFinished = False
            self.lastRatio = self.printedUserHP /self.UserMaxHP
            if self.printedUserHP <= newHP:
                T = threading.Thread(target=genFunc(playsound,'sounds/heal.mp3'))
                T.start()
                k = genFunc(self.HPUpdateUser,newHP,0,15,updateInGui) ##if we are restoring HP, we skip flashing
                master.after(5,k)
            else:
                if effectiveness == 'super':
                    T = threading.Thread(target=genFunc(playsound,'sounds/superhit.mp3'))
                    T.start()
                elif effectiveness == 'weak':
                    T = threading.Thread(target=genFunc(playsound,'sounds/weakhit.mp3'))
                    T.start()
                else:
                    T = threading.Thread(target=genFunc(playsound,'sounds/normalhit.mp3'))
                    T.start()
                k = genFunc(self.HPUpdateUser,newHP,0,1,updateInGui)
                master.after(5,k)
        elif flashing%2==1 and flashing < 9:
            self.battleCanvas.delete('user-pokemon')
            k = genFunc(self.HPUpdateUser,newHP,0,flashing+1,updateInGui) ##flashing is responsible for, well, the Pokemon flashing
                                    ##after taking damage. It flip flops between this elif and the one below
                                    ##until flashing is 14 then it goes to the else- which controls the HP bar thing
            master.after(100,k)
        elif flashing%2==0 and flashing < 9:
            self.battleCanvas.create_image(140,360,anchor=S,image=self.userPokemonSprite,tags=('user-pokemon'))
            k = genFunc(self.HPUpdateUser,newHP,0,flashing+1,updateInGui)
            master.after(100,k)
        else:
            if self.printedUserHP > newHP:
                self.printedUserHP -= 1
            elif self.printedUserHP < newHP:
                self.printedUserHP += 1
            else:
                if updateInGui:
                    self.arena.userTrainer.team[str(self.arena.userTrainer.active)].takeDamage(self.arena.userTrainer.team[str(self.arena.userTrainer.active)].hp - newHP)
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
            k = genFunc(self.HPUpdateUser,newHP,0,15,updateInGui)
            master.after(20,k)

    def moveOutUserHPBar(self,tick=0):
        if tick < 46:
            self.battleCanvas.move('user-hp',5,0)
            k = genFunc(self.moveOutUserHPBar,tick+1)
            master.after(2,k)
        else:
            self.processesComplete += 1

    def moveOutEnemyHPBar(self,tick=0,dontMarkTaskFinished=False):
        if tick < 50:
            self.battleCanvas.move('enemy-hp',-5,0)
            k = genFunc(self.moveOutEnemyHPBar,tick+1)
            master.after(2,k)
        else:
            self.processesComplete += 1
            if not dontMarkTaskFinished:
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
        j = self.arena.userTrainer.team[str(self.arena.userTrainer.active)].statusCondition
        if j == None:
            self.battleCanvas.delete('user-status')
        else:
            self.userStatusConditionImage = ImageTk.PhotoImage(Image.open('assets/status-conditions/'+j+'.png').resize((35,14)))
            self.battleCanvas.create_image(340,292,image=self.userStatusConditionImage,tags=('user-hp','user-status'))
        master.update()

    def setEnemyStatus(self):
        j = self.arena.enemyTrainer.team[str(self.arena.enemyTrainer.active)].statusCondition
        if j == None:
            self.battleCanvas.delete('enemy-status')
        else:
            self.enemyStatusConditionImage = ImageTk.PhotoImage(Image.open('assets/status-conditions/'+j+'.png').resize((35,14)))
            self.battleCanvas.create_image(195,87,image=self.enemyStatusConditionImage,tags=('enemy-hp','enemy-status'))

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
        self.processesComplete += 1

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
        self.master.after(50,k)
        
    def fadeaway(self):
        alpha = self.master.attributes("-alpha")
        if alpha > 0:
            alpha -= 0.01
            self.master.attributes("-alpha",alpha)
            master.after(10,self.fadeaway)
        else:
            master.quit()

    def on_closing(self):
        mixer.music.stop()
        self.master.destroy()
#------------------------------------------------------------------------------------------------------------------------------#

def switchToBattleGUI(user,enemy,master,receiveInfo=False,megaboss=None,miniboss=None):
    mixer.music.fadeout(1000)
    arena = battle.Arena(user,enemy,receiveInfo)
    if megaboss == None and miniboss == None:
        mixer.music.load(r.choice(battleMusic))
        App = app(master,arena,receiveInfo)
    elif miniboss != None:
        mixer.music.load('music/gymLeader.mp3')
        App = app(master,arena,receiveInfo,miniboss=True)
    else:
        mixer.music.load(finalBossMusic[megaboss])
        App = app(master,arena,receiveInfo,megaboss=True)
    mixer.music.play(-1)

def beginDraftingGUI(master,numRounds,pokemonPerRound,numBattles):
    mixer.music.fadeout(1000)
    mixer.music.load(r.choice(draftingMusic))
    mixer.music.play(-1)
    DraftingApp = draftingApp(master,numRounds,pokemonPerRound,numBattles)

def switchToMenuGUI(master):
    mixer.music.load('music/Menu.mp3')
    mixer.music.play(-1)
    Menu = menuApp(master)

def switchToDraftingGUI(receiveInfo,master):
    mixer.music.fadeout(1000)
    mixer.music.load(r.choice(draftingMusic))
    mixer.music.play(-1)
    DraftingApp = draftingApp(master,0,0,0,receiveInfo)
    

flag = 'menu'
if flag == 'game':
    trainerOne = battle.trainer('Ethan','Pokemon Trainer','Ethan')
    trainerTwo = battle.trainer('Blue','Champion','Blue')
    CPT = 'Charizard' ##CPT = currentPokemonTesting
    charizardOne = battle.pokemon(CPT,60,trainerOne)
    trainerOne.addToTeam(0)
    for x in range(5):
        battle.pokemon(CPT,random.randint(50,60),trainerOne)
        trainerOne.addToTeam(x+1)
    battle.pokemon(CPT,random.randint(50,60),trainerTwo)
    trainerTwo.addToTeam(0)
    for x in range(5):
        battle.pokemon(CPT,random.randint(50,60),trainerTwo)
        trainerTwo.addToTeam(x+1)
    master = Tk()
    mixer.init()
    switchToBattleGUI(trainerOne,trainerTwo,master)
    mainloop()
    #arena = battle.Arena(trainerOne,trainerTwo)

if flag == 'drafting':
    master = Tk()
    draftingArena = False
    master.geometry('1000x700')
    master.title('drafting gui or something')
    master.resizable(False, True)
    DraftingApp = draftingApp(master,draftingArena)
    mainloop()

if flag == 'menu':
    mixer.init()
    mixer.music.load('music/Menu.mp3')
    mixer.music.play(-1)
    mixer.music.set_volume(0.5)
    master = Tk()
    master.geometry('1000x700')
    master.title('Pokémon Horizons')
    Menu = menuApp(master)
    mainloop()


moop = 0