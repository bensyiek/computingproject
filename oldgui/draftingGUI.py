from tkinter import *
from PIL import Image, ImageTk
from tkinter import font
import time
import math, threading
import random as r

##Custom built modules
import battle
from pkmnData import *
import gui

def genFunc(f, *args):
    return lambda *args2: f(*args)

master = Tk()
draftingArena = False
master.geometry('1000x700')
master.title('drafting gui or something')
master.resizable(False, True)

class draftingApp:
    def __init__(self,master,receiveInfo = False):
        
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
        
        self.DPPtFont = font.Font(family='Pokemon DPPt',size=26)
        self.DPPtFont2 = font.Font(family='Pokemon DPPt',size=24)
        self.tabletFont = font.Font(family='Pokemon DPPt',size=15,weight="bold")
        self.smallTabletFont = font.Font(family='Pokemon DPPt',size=13,weight="bold")
        
        self.pokedexFrame = Frame(master,relief=SUNKEN,borderwidth=5,height=700,width=500,bg='grey')
        self.pokedexFrame.grid(row=0,column=1,rowspan=3,sticky=W+E+N+S)
        self.screenFrame = Frame(self.pokedexFrame,relief=SUNKEN,borderwidth=5,height=500,width=400,bg='light grey')
        self.screenFrame.place(x=245,y=50,anchor=N)
        self.viewChoicesButton = Button(self.pokedexFrame,state=DISABLED,bg='#9fe8c4',font=self.DPPtFont2,text='View Choices',command=self.showChoices)
        self.viewChoicesButton.place(x=245,y=602,anchor=N)
        self.tabletCanvas = Canvas(self.screenFrame,width=380,height=500,bg='light grey')
        self.tabletCanvas.pack()

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


        #vars used for team creation
        self.team = {0:None,1:None,2:None,3:None}
        self.teamToChoicesLink = {0:None,1:None,2:None,3:None}
        self.teamIDs = {0:None,1:None,2:None,3:None}
        self.teamImages = {0:None,1:None,2:None,3:None}
        self.transparentBoxImage1 = {} ##bigger one used for team
        self.transparentBoxImage2 = {} ##smaller one used for choices
        self.teamCreation = False ##used for cursor specifiers in the choices menu

        ##these vars are for tabletCanvas:
        self.EVEntry = {}
        self.EVStringVar = {}

        ##these 'black' files are the fade in black things we see at the start of the draft.
        self.blackImageFile = Image.open('assets/black/black250.png').resize((700,700))
        self.blackImage = ImageTk.PhotoImage(self.blackImageFile)
        self.battleCanvas.create_image(0,0,anchor=NW,image=self.blackImage,tags=('black-screen'))

        ##stuff to pay attention to if we aren't drafting but are instead making a team
        ##receiveInfo in form [list of pokemon chosen, number of battles left]
        if receiveInfo != False:
            self.pokemonChosen = receiveInfo[0]
            self.battlesLeft = receiveInfo[1]
        else:
            self.battlesLeft = 5

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
            self.initDraft(1,4)
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

    def tablet_editEVs(self,pkmn):
        self.tabletCanvas.delete('tablet-data')
        self.tabletCanvas.create_rectangle([115,10,270,160],fill=typeColor[pkmn.types[0]],width=3,outline='black',stipple='gray25',tags=('tablet-data'))
        self.tab_pokemonImage = Image.open(pokemon[pkmn.name])
        self.tab_pokemonImage = ImageTk.PhotoImage(self.tab_pokemonImage.resize((141,141)))
        self.tabletCanvas.create_image(190,80,image=self.tab_pokemonImage,tags=('tablet-data','pokemon-photo'))

        self.tabletCanvas.create_text(20,195,text='Current Stats: ' + str(pkmn.stats),font=self.tabletFont,anchor=W,tags=('tablet-data','tablet-current-stats')) ##show the user their current stats
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
            if k[len(k)-x] not in '0123456789':
                print(k[len(k)-x])
                if x != 1:
                    k = k[:len(k)-x] + k[len(k)-x+1:]
                else:
                    k = k[:len(k)-x]
        if len(k) > 3:
            k = k[:3]
        elif len(k) == 0:
            k = '0'
        var.set(k)
        statTotal = 0
        for stat in ['HP','Attack','Defense','Sp. Attack', 'Sp. Defense', 'Speed']:
            statTotal += int(self.EVStringVar[stat].get())
        if statTotal > 508:
            k = str(int(k) - (statTotal-508))
        if int(k) > 252:
            k = '252'
        var.set(k)
        
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
            self.battleCanvas.create_rectangle(0+490,0,490+490,542,width=2,fill='light grey',tags=('choices-data','choices-background'))
            xOffset = 7
            yOffset = 5
            for x in range(0,18):
                if x == 15:
                    xOffset = 96+7
                self.boxIDs.append(self.battleCanvas.create_rectangle(0+xOffset+490,0+yOffset,90+xOffset+490,90+yOffset,fill='light grey', outline='grey',width=2,tags=('choices-data','not-team')))
                xOffset = (xOffset + 96) % 480 ##loops aorund when xOffset gets bigger than 480
                yOffset = (yOffset) + 96*int((x%5+1)/5) ##adds 96 whenever next x is divisible by 5- i.e. when we've plotted 5 items in a row

            self.tempChoicesIDs = []
            self.tempChoicesPhotos = []
            xOffset = 7
            yOffset = 5
            count = 0
            for pkmn in self.pokemonChosen:
                if count == 15:
                    xOffset = 96+7
                self.tempChoicesPhotos.append(ImageTk.PhotoImage(Image.open(pokemon[pkmn.species]).resize((84,84))))
                ID = self.battleCanvas.create_image(0+xOffset+490,0+yOffset,anchor=NW,image=self.tempChoicesPhotos[count],tags=('choices-data','not-team'))
                xOffset = (xOffset + 96) % 480
                yOffset = (yOffset) + 96*int((count%5+1)/5)
                self.tempChoicesIDs.append(ID)
                count += 1
                
            if teamCreation: ##only applicable if team creation is in use- i.e. at the end of a draft
                xOffset = 15
                for x in range(0,4):
                    self.battleCanvas.create_rectangle(0+xOffset+490,537-125,100+xOffset+490,537-25,fill='light grey',outline='grey',width=2,tags=('choices-data','team'))
                    self.transparentBoxImage1[x] = ImageTk.PhotoImage(Image.open('assets/drafting/greyRectangleTransparent/grey100.png'))
                    self.battleCanvas.create_image(0+xOffset+490,537-125,anchor=NW,image=self.transparentBoxImage1[x],tags=('transparencyBox-team-'+str(x),'choices-data'))
                    xOffset += 120
            self.battleCanvas.lift('choices-data')
            master.after(5,genFunc(self.slideChoicesAcross,loop+1,teamCreation))
            
        elif 98 >= loop >= 1:
            self.battleCanvas.move('choices-data',-5,0)
            master.after(10,genFunc(self.slideChoicesAcross,loop+1,teamCreation))
        else:
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

    def choices_hoverOver(self,pokemon,ID):
        if self.teamCreation:        
            self.battleCanvas.config(cursor='hand2')
        self.tablet_displayEnemyPokemon(pokemon)
        self.isCursorOnPokemon = self.battleCanvas.coords(ID)
        self.choices_boxSelection(self.isCursorOnPokemon)

    def choices_hoverOff(self,event=False):
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

    def hideChoices(self):
        for ID in self.tempChoicesIDs:
            self.battleCanvas.tag_unbind(ID,'<Enter>')
            self.battleCanvas.tag_unbind(ID,'<Leave>')
        self.deactivateButtons()
        self.slideChoicesOut()

    def slideChoicesOut(self,loop=0):
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

    def initTeamCreation(self):
        q = battle.serviceQueue
        self.teamCreation = True
        style = r.choice(self.platformMovementStyles)
        q.add([style,genFunc(self.movePlatforms,'off',style,0,False)])
        q.add([False,genFunc(self.slideChoicesAcross,0,True)])
        self.executeTurn(q)

    def disableChoices(self):
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
            self.viewChoicesButton.config(text='Start Battle',bg='light green')
            self.initEVTraining()

    def initEVTraining(self):
        for x in range(0,4):
            self.battleCanvas.tag_unbind('team-'+str(x),'<Button-1>')
            self.battleCanvas.tag_bind('team-'+str(x),'<Button-1>',genFunc(self.EV_lockButtons,x))
            self.viewChoicesButton.config(text='Start Battle',bg='light green')
        self.EV_enableButtons()

    def startBattle(self):
        self.EV_disableButtons()
        enemyTrainer = battle.trainer(r.choice(names),r.choice(trainerClass))
        for x in range(4):
            battle.pokemon(r.choice(pokemonInDraft),r.randint(50,60),enemyTrainer)
            enemyTrainer.addToTeam(x)
        userTrainer = battle.trainer('Ethan','Pokemon Trainer')
        for x in range(4):
            self.team[x].getTrainer(userTrainer)
            userTrainer.addToTeam(x)
        gui.start(userTrainer,enemyTrainer,[self.pokemonChosen,self.battlesLeft])
        

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
        self.tabletCanvas.itemconfig('tablet-current-stats',text='Current Stats: ' + str(self.team[index].stats))

    def EV_handCursor(self,event=False):
        self.battleCanvas.config(cursor='hand2')

    def EV_arrowCursor(self,event=False):
        self.battleCanvas.config(cursor='arrow')
        
#------------------------------------------------------------------------------------------------------------------------------#
           # '''Drafting!! This is all of the stuff required to be able to draft.'''
#------------------------------------------------------------------------------------------------------------------------------#

    def initDraft(self,totalRounds,pokemonPerRound):
        self.totalRounds = totalRounds
        self.pokemonPerRound = 6
        self.roundsLeft = self.totalRounds
        self.numberLeftInRound = pokemonPerRound
        self.pokemonAvailable = {}
        try:
            self.pokemonChosen ##if here, then we've already got pokemonChosen and so are returning in between a battle
            self.initTeamCreation()
        except:
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
            q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft) + ' round left after this, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
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
        if self.roundsLeft > 1:                                                                                                         ##this is to take out the s of rounds if we aren't taking  about a plural
            q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft) + ' rounds left, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
        else:
            q.add([False,genFunc(self.runText,'You have ' + str(self.roundsLeft) + ' round left, and ' + str(self.numberLeftInRound) + ' Pokemon left to pick in this round.')])
        q.add(['activate-buttons',self.activateButtons])
        self.executeTurn(q)

    def checkPokemonOut(self):
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

moop = 0

DraftingApp = draftingApp(master,draftingArena)
mainloop()
