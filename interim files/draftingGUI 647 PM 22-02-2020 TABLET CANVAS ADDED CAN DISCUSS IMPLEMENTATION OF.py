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
    def __init__(self,master,draftingArena=False):

        self.master = master
        self.battleStart = False
        self.smallestWating = 0
        self.textRunning = False
        self.arena = draftingArena
        self.platformMovementStyles = ['diagonalSeparation','columnSeparation','rowSeparation']
        self.coordsDict = {'(115, 150)' : ('platform','platformC1','platformR1','platformC1R1','platform(115, 150)'),
                           '(115, 320)' : ('platform','platformC1','platformR2','platformC1R2','platform(115, 320)'),
                           '(115, 490)' : ('platform','platformC1','platformR3','platformC1R3','platform(115, 490)'),
                           '(375, 130)' : ('platform','platformC2','platformR1','platformC2R1','platform(375, 130)'),
                           '(375, 300)' : ('platform','platformC2','platformR2','platformC2R2','platform(375, 300)'),
                           '(375, 470)' : ('platform','platformC2','platformR3','platformC2R3','platform(375, 470)')}
        
        self.battleFrame = Frame(master,relief=SUNKEN,borderwidth=5,height=350,width=500,bg=backgrounds['indoor']['bgColor'])
        self.battleFrame.grid(row=0,column=0,sticky=W+E+N+S)
        self.battleCanvas = Canvas(self.battleFrame,width=485,height=537)
        self.battleCanvas.pack()
        
        self.pokedexFrame = Frame(master,relief=SUNKEN,borderwidth=5,height=700,width=500,bg='grey')
        self.pokedexFrame.grid(row=0,column=1,rowspan=3,sticky=W+E+N+S)
        self.screenFrame = Frame(self.pokedexFrame,relief=SUNKEN,borderwidth=5,height=500,width=400,bg='light grey')
        self.screenFrame.place(x=245,y=50,anchor=N)
        self.tabletCanvas = Canvas(self.screenFrame,width=380,height=500,bg='light grey')
        self.tabletCanvas.pack()
        
        self.DPPtFont = font.Font(family='Pokemon DPPt',size=26)
        self.DPPtFont2 = font.Font(family='Pokemon DPPt',size=24)
        self.tabletFont = font.Font(family='Pokemon DPPt',size=15,weight="bold")
        self.smallTabletFont = font.Font(family='Pokemon DPPt',size=13,weight="bold")

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
        
        self.backgroundPilImage = Image.open(backgrounds['indoor']['filePath'])
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

        ##these 'black' files are the fade in black things we see at the start of the draft.
        self.blackImageFile = Image.open('assets/black/black250.png').resize((700,700))
        self.blackImage = ImageTk.PhotoImage(self.blackImageFile)
        self.battleCanvas.create_image(0,0,anchor=NW,image=self.blackImage,tags=('black-screen'))

 ##puts the pokeballs on the platforms in preparation
        self.beginDraftAnimation() ##that draft anim happens :)

        #self.fadeOutChoice((115,150))
        #self.initDraft()

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
           # '''Drafting!! This is all of the stuff required to be able to draft.'''
#------------------------------------------------------------------------------------------------------------------------------#

    def initDraft(self):
        self.roundsLeft = 2
        self.numberLeftInRound = 6
        self.pokemonAvailable = {}
        self.pokemonChosen = []
        self.checkPokeballs()
        self.firstRoundOfDraft()

    def firstRoundOfDraft(self):
        for count in range(0,6):
            self.pokemonAvailable[str(self.pokemonCoordsSouth[count])] = battle.pokemon(r.choice(pokemonInDraft),r.randint(50,60))  ##generate a random pack. the stats/moves are already generated randomly within the pokemon class
        q = battle.serviceQueue()
        q.add(['columnSeparation',genFunc(self.movePlatforms,'on','columnSeparation',False)])
        q.add([self.pokemonCoordsSouth[self.numberLeftInRound-1],self.processPokemonSendOut])
        if self.roundsLeft > 1:                                                                                                     ##this is to take out the s of rounds if we aren't taking  about a plural
            q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft) + ' rounds left, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
        else:
            q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft) + ' round left, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
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
            elif count >= self.numberLeftInRound:                                                                                       ##packs go from 6->5->4 etc. so we need to fill the empty spaces with None (to tell program later what's going on)
                self.pokemonAvailable[str(self.pokemonCoordsSouth[count])] = None
        q = battle.serviceQueue()
        style = r.choice(self.platformMovementStyles)
        q.add([style,genFunc(self.movePlatforms,'off',style)])
        q.add([self.pokemonCoordsSouth[self.numberLeftInRound-1],self.processPokemonSendOut])                                           ##so we do it after the last one to finish
        if self.roundsLeft > 1:                                                                                                         ##this is to take out the s of rounds if we aren't taking  about a plural
            q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft) + ' rounds left, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
        else:
            q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft) + ' round left, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
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
                k = genFunc(self.handCursor,coords,self.pokemonAvailable[str(coords)])
                self.battleCanvas.tag_bind(self.pokemonCanvasItemVars[str(coords)],'<Enter>',k)
                self.battleCanvas.tag_bind(self.pokemonCanvasItemVars[str(coords)],'<Leave>',self.arrowCursor)
            else:
                break
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
        ##
        ##
        ##
        ##
        ##
        ##
        ##
        ##
        ## NOTE TO FUTURE BEN
        ## this lil line right here can be used to show us solving a bug
        ## say smth like: the tabletCanvas didn't refresh after selecting a pokemon.
        ##                I had tried to add something to arrowCursor() but then realized
        ##                the part I needed to add something to was this function.
        ##
        ##
        ##
        ##
        ##
        ##
        ##
        ##
        self.isCursorOnPokemon = False
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
            if self.roundsLeft == 0: ##need to program started battle sequence
                return                                                   ## and we've finished the draft if we've gotten here as we've got 0 rounds left and 1 pokemon left in the round.
            self.numberLeftInRound = 6
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
                        self.checkPokeballs()
                        self.battleCanvas.move('platformC1',0,-1060) ##if this is the firstTime executing movePlatforms for this instance, move the platforms to the other side of screen (offscreen)...
                        self.battleCanvas.move('platformC2',0,1060)
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
                        self.checkPokeballs()
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
                        self.checkPokeballs()
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
                        self.checkPokeballs()
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

moop = 0

DraftingApp = draftingApp(master,draftingArena)
mainloop()
