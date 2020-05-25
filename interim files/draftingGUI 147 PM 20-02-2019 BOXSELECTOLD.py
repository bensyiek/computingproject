from tkinter import *
from PIL import Image, ImageTk
from tkinter import font
import time
import math, threading
import random as r

##Custom built modules
import battle
from pkmnData import *

def genFunc(f, *args):
    return lambda *args2: f(*args)

master = Tk()
draftingArena = False
master.geometry('1000x700')
master.title('drafting gui or something')

class draftingApp:
    def __init__(self,master,draftingArena):

        self.master = master
        self.battleStart = False
        self.smallestWating = 0
        self.textRunning = False
        self.arena = draftingArena
        self.platformMovementStyles = ['diagonalSeparation','columnSeparation','rowSeparation']
        
        self.battleFrame = Frame(master,relief=SUNKEN,borderwidth=5,height=350,width=500,bg=backgrounds['indoor']['bgColor'])
        self.battleFrame.grid(row=0,column=0,sticky=W+E+N+S)
        self.battleCanvas = Canvas(self.battleFrame,width=485,height=537)
        self.battleCanvas.pack()
        self.backgroundPilImage = Image.open(backgrounds['indoor']['filePath'])
        self.backgroundPilImage = self.backgroundPilImage.resize((500,600))
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
        self.tBoxPointer = 0
        self.tBox = {
            '0' : self.textBox0,
            '1' : self.textBox1,
            '2' : self.textBox2
            }
        self.initResources()

    def initResources(self):
        self.platformImageFile = Image.open(assets['indoor-enemy'])
        self.platformImageFile = self.platformImageFile.resize((225,75))
        self.platformImage = ImageTk.PhotoImage(self.platformImageFile)

        self.battleCanvas.create_image(115,150,image=self.platformImage,tags=('platform','platformC1','platformR1','platformC1R1','platform(115, 150)'))
        self.battleCanvas.create_image(115,320,image=self.platformImage,tags=('platform','platformC1','platformR2','platformC1R2','platform(115, 320)'))
        self.battleCanvas.create_image(115,490,image=self.platformImage,tags=('platform','platformC1','platformR3','platformC1R3','platform(115, 490)'))
        self.battleCanvas.create_image(375,130,image=self.platformImage,tags=('platform','platformC2','platformR1','platformC2R1','platform(375, 130)'))
        self.battleCanvas.create_image(375,300,image=self.platformImage,tags=('platform','platformC2','platformR2','platformC2R2','platform(375, 300)'))
        self.battleCanvas.create_image(375,470,image=self.platformImage,tags=('platform','platformC2','platformR3','platformC2R3','platform(375, 470)'))

        self.EpokeballImageFile = {}
        self.EpokeballImage = {}
        self.EpokemonImageFile = {}
        self.EpokemonImage = {}
        self.Epokemon = {}
        self.pokemonCanvasItemVars = {}
        self.pokeballCanvasItemVars = {}
        self.taskFinished = {'False' : True}
        self.pokemonCoordsSouth = [(115,150),(115,320),(115,490),(375,130),(375,300),(375,470)]

        if False:
            self.enemyPokemonSendOut(coords=(115,160))
            self.enemyPokemonSendOut(coords=(115,310))
            self.enemyPokemonSendOut(coords=(115,460))
            self.enemyPokemonSendOut(coords=(375,140))
            self.enemyPokemonSendOut(coords=(375,290))
            self.enemyPokemonSendOut(coords=(375,440))
        if False:
            pass
            self.movePlatforms('off')
        #self.fadeOutChoice((115,150))
        self.initDraft()


#------------------------------------------------------------------------------------------------------------------------------#
           # '''Drafting!! This is all of the stuff required to be able to draft.'''
#------------------------------------------------------------------------------------------------------------------------------#

    def initDraft(self):
        self.roundsLeft = 2
        self.numberLeftInRound = 3
        self.pokemonAvailable = {}
        self.pokemonChosen = []
        self.draft()

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
                self.pokemonAvailable[str(self.pokemonCoordsSouth[count])] = battle.pokemon(r.choice(pokemonInDraft),r.randint(50,60))
            elif count >= self.numberLeftInRound:
                self.pokemonAvailable[str(self.pokemonCoordsSouth[count])] = None
        q = battle.serviceQueue()
        style = r.choice(self.platformMovementStyles)
        q.add([style,genFunc(self.movePlatforms,'off',style)])
        q.add([self.pokemonCoordsSouth[self.numberLeftInRound-1],self.processPokemonSendOut]) ##so we do it after the last one to finish
        q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft) + ' rounds left, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
        q.add(['activate-buttons',self.activateButtons])
        self.executeTurn(q)

    def processPokemonSendOut(self):
        count = 0
        for coords in self.pokemonCoordsSouth:
            self.taskFinished[str(coords)] = False
            if self.pokemonAvailable[str(coords)] != None:
                k = genFunc(self.enemyPokemonSendOut,0,0,coords)
                master.after(5+250*count,k)
            else:
                break
            count += 1
        
    def activateButtons(self):
        self.taskFinished['activate-buttons'] = False
        for coords in self.pokemonCoordsSouth:
            if self.pokemonAvailable[str(coords)] != None:
                k = genFunc(self.selectPokemon,coords)
                self.battleCanvas.tag_bind(self.pokemonCanvasItemVars[str(coords)],'<Button-1>',k)
                k = genFunc(self.handCursor,coords)
                self.battleCanvas.tag_bind(self.pokemonCanvasItemVars[str(coords)],'<Enter>',k)
                self.battleCanvas.tag_bind(self.pokemonCanvasItemVars[str(coords)],'<Leave>',self.arrowCursor)
            else:
                break
        self.taskFinished['activate-buttons'] = True

    def handCursor(self,coords,event=False): ##updates the cursor to be a hand when a user is over an image
        self.isCursorOnPokemon = coords
        self.battleCanvas.config(cursor='hand2') ##changes to the normal hand. hand1 is truly horrific
        self.boxSelection(coords) ##see below

    def arrowCursor(self,event=False):
        self.isCursorOnPokemon = False
        self.battleCanvas.config(cursor='arrow')

    def boxSelection(self,coords,offset=0,sign=1): ##pops up a small green box around the user's choice
        try:
            self.boxImageTR
        except:
            self.boxImageTR = ImageTk.PhotoImage(Image.open(assets['sBoxTR']).resize((30,30)))
            self.boxImageTL = ImageTk.PhotoImage(Image.open(assets['sBoxTL']).resize((30,30)))
            self.boxImageBR = ImageTk.PhotoImage(Image.open(assets['sBoxBR']).resize((30,30)))
            self.boxImageBL = ImageTk.PhotoImage(Image.open(assets['sBoxBL']).resize((30,30)))
        self.battleCanvas.delete('selection-box')
        self.battleCanvas.create_image(coords[0]-70-offset,coords[1]-90-offset,image=self.boxImageTL,anchor=S,tags=('selection-box'))
        self.battleCanvas.create_image(coords[0]+70+offset,coords[1]-90-offset,image=self.boxImageTR,anchor=S,tags=('selection-box'))
        self.battleCanvas.create_image(coords[0]-70-offset,coords[1]+30+offset,image=self.boxImageBL,anchor=S,tags=('selection-box'))
        self.battleCanvas.create_image(coords[0]+70+offset,coords[1]+30+offset,image=self.boxImageBR,anchor=S,tags=('selection-box'))

        if offset == 10:
            sign = -1
        elif offset == 0:
            sign = 1
        if self.isCursorOnPokemon == coords:
            k = genFunc(self.boxSelection,coords,offset+sign,sign)
            master.after(25,k)
        else:
            self.battleCanvas.delete('selection-box')
            
    def oldBoxSelect():
        try:
            self.boxImageFile
        except:
            self.boxImageFile = Image.open(assets['selectionBox'])
        self.boxImage = ImageTk.PhotoImage(self.boxImageFile.resize((int(150*(1+offset)),int(150*(1+offset)))))
        self.battleCanvas.delete('selection-box')
        self.battleCanvas.create_image(coords[0],coords[1]-65,image=self.boxImage)
        if offset == 0.25:
            sign == -0.01
        elif offset == -0.25:
            sign == 0.01
        if self.isCursorOnPokemon == coords:
            k = genFunc(self.boxSelection,coords,offset+sign,sign)
            master.after(50,k)
        else:
            self.battleCanvas.delete('selection-box')


    def deactivateButtons(self):
        self.battleCanvas.config(cursor='arrow')
        for coords in self.pokemonCoordsSouth:
            if self.pokemonAvailable[str(coords)] != None:
                self.battleCanvas.tag_unbind(self.pokemonCanvasItemVars[str(coords)],'<Button-1>')
                self.battleCanvas.tag_unbind(self.pokemonCanvasItemVars[str(coords)],'<Enter>')
                self.battleCanvas.tag_unbind(self.pokemonCanvasItemVars[str(coords)],'<Leave>')

    def selectPokemon(self,coords):
        self.deactivateButtons()
        self.pokemonChosen.append(self.pokemonAvailable[str(coords)])
        q = battle.serviceQueue()
        q.add([False,genFunc(self.runText,'You selected ' + self.pokemonAvailable[str(coords)].name+'!')])
        k = genFunc(self.processPokemonRetrieval,coords)
        q.add([self.pokemonCoordsSouth[self.numberLeftInRound-1],k])
        self.numberLeftInRound -= 1
        if self.numberLeftInRound == 0:
            self.roundsLeft -= 1
            if self.roundsLeft == 0: ##need to program started battle sequence
                return
            self.numberLeftInRound = 6
        q.add([False,self.draft])
        self.executeTurn(q)

    def processPokemonRetrieval(self,coordsChosen):
        count = 0
        for coords in self.pokemonCoordsSouth:
            self.taskFinished[str(coords)] = False
            if self.pokemonAvailable[str(coords)] != None:
                if coordsChosen == coords:
                    k = genFunc(self.switchEnemy,0,0,coords,True)
                    master.after(5+250*count,k)
                else:
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
            self.EpokemonImageFile[str(coords)] = Image.open(pokemon['Charizard'])
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
            self.battleCanvas.create_image(coords[0],coords[1],image=self.EpokeballImage[str(coords)],anchor=S,tags=('enemy-pokeball'+str(coords)))
            self.battleCanvas.delete('enemy-pokemon'+str(coords))
            k = genFunc(self.switchEnemy,tick,count+1,coords,capture)
            self.master.after(250,k)
        elif 3 < count < 40:
            if capture == False:
                t = (int(math.log(40-count)/math.log(40)*24)+1,int(math.log(40-count)/math.log(40)*35)+1)
                self.EpokeballImage[str(coords)] = self.EpokeballImageFile[str(coords)].resize(t)
                self.EpokeballImage[str(coords)] = ImageTk.PhotoImage(self.EpokeballImage[str(coords)])
                self.battleCanvas.delete('enemy-pokeball'+str(coords))
                self.pokeballCanvasItemVars[str(coords)] = self.battleCanvas.create_image(coords[0],coords[1],image=self.EpokeballImage[str(coords)],anchor=S,tags=('enemy-pokeball'+str(coords)))
                self.master.update()
                k = genFunc(self.switchEnemy,tick,count+1,coords,capture)
                self.master.after(5,k)
            elif capture:
                self.taskFinished[str(coords)] = True
                return
        elif count == 40:
            self.battleCanvas.delete(self.pokeballCanvasItemVars[str(coords)])
            self.taskFinished[str(coords)] = True

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
                        self.battleCanvas.move('platformC1',0,-1040) ##if this is the firstTime executing movePlatforms for this instance, move the platforms to the other side of screen (offscreen)...
                        self.battleCanvas.move('platformC2',0,1040)
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
                if loop == 50:
                    if firstTime:
                        self.battleCanvas.move('platformC1',0,-1040)
                        self.battleCanvas.move('platformC2',0,1040)
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
                        k = genFunc(self.movePlatforms,'off',style,0,False)
                        master.after(30,k)
                    else:
                        self.taskFinished[style] = True
                    return
            k = genFunc(self.movePlatforms,direction,style,loop+1,False)
            master.after(30,k)

    def fadeOutChoice(self,coords,percentAlpha=95):
        self.taskFinished['fade-out-choice'] = False
        self.EpokeballImageFile[str(coords)] = Image.open('assets/pokeballs/pokeballtransparent/pokeball'+str(percentAlpha)+'.png')
        self.alphaPokeball = ImageTk.PhotoImage(self.EpokeballImageFile[str(coords)].resize((24,35)))
        self.battleCanvas.delete('enemy-pokeball'+str(coords))
        self.battleCanvas.create_image(coords[0],coords[1],image=self.alphaPokeball,anchor=S)
        if percentAlpha > 0:
            k = genFunc(self.fadeOutChoice,coords,percentAlpha-5)
            master.after(70,k)
        else:
            self.taskFinished['fade-out-choice'] = True

    def oldCode(self,coords,alpha=255):
        self.platformImageFile.putalpha(alpha)
        
        self.battleCanvas.delete(str('platform'+str(coords)))
        self.platformImageAlpha = ImageTk.PhotoImage(self.platformImageFile)
        self.battleCanvas.create_image(coords[0],coords[1],image = self.platformImageAlpha,tags=('platform','platformC1','platformR1','platformC1R1','platform(115, 150)'))
        if alpha == 0:
            return
        k = genFunc(self.fadeOutChoice,coords,alpha-5)
        master.after(50,k)

    def captureChoice(self,coords,size=0):
        if size == 0:
            self.captureBallFile = Image.open(pokeballs['Pokeball'])
            k = genFunc(self.captureChoice,coords,5)
            master.after(25,k)
            return
        self.captureBall = ImageTk.PhotoImage(self.captureBallFile.resize((int(1+140*math.log(size)/math.log(100)),int(1+206*math.log(size)/math.log(100)))))
        self.battleCanvas.delete('capture-ball')
        self.battleCanvas.create_image(coords[0],coords[1],image=self.captureBall,anchor=S,tags=('capture-ball'))
        if size == 100:
            return
        k = genFunc(self.captureChoice,coords,size+5)
        master.after(50,k)

    def rollBallOffscreen(self,coords,angle=10):
        try:
            self.battleCanvas.delete('enemy-pokeball'+str(coords))
            self.EpokeballImageFile[str(coords)] = self.EpokeballImageFile[str(coords)].rotate(angle)
            self.EpokeballImageFile[str(coords)].convert('RGBA')
            self.rollingBall = ImageTk.PhotoImage(self.EpokeballImageFile[str(coords)].rotate(angle))
            self.battleCanvas.create_image(coords[0],coords[1],image=self.rollingBall,anchor=S)
        except:
            self.EpokeballImageFile[str(coords)] = Image.open(pokeballs['Pokeball'])
        k = genFunc(self.rollBallOffscreen,coords,angle+10)
        master.after(50,k)
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

moop = 0

DraftingApp = draftingApp(master,draftingArena)
mainloop()
