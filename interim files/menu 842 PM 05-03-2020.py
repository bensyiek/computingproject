from tkinter import *
from tkinter import font
from PIL import Image, ImageTk
import time, threading
from playsound import playsound

def genFunc(f, *args):
    return lambda *args2: f(*args)

class menuApp:
    def __init__(self,master):
        self.master = master
        ##these locations for canvas *just* manage to get it to fill the screen
        self.menuCanvas = Canvas(master,bg='black',height=700,width=1000)
        self.menuCanvas.place(x=-2,y=-1)
        
        self.LogoDPPtFont = font.Font(family='Pokemon DPPt',size=100)
        self.MenuDPPtFont = font.Font(family='Pokemon DPPt',size=40)
        self.smallMenuDPPtFont = font.Font(family='Pokemon DPPt',size=20)
        self.menuCanvas.create_text(500,90-120,text='POKEMON HORIZONS',fill='white',font=self.LogoDPPtFont,tags=('main-text'))
        self.logoImageFile = Image.open('assets/menu/logo.png').resize((int(360*1.7),int(100*1.7)))
        self.logoImageFile.putalpha(5)
        self.logoImage = ImageTk.PhotoImage(self.logoImageFile)
        self.menuCanvas.create_image(500,220,image=self.logoImage,tags=('logo'))

        self.testingReduceTime=0
        self.timeSinceLastActivation = time.time()
        self.currentMenu = 'main'
        self.doMovePointer = True

        self.pokemonPerRound = 6
        self.numRounds = 2

        self.moveDownText()

    def moveDownText(self,loop=0):
        if loop < 120:
            self.menuCanvas.move('main-text',0,1)
            self.master.after(5,genFunc(self.moveDownText,loop+1))
        else:
            self.fadeInLogo()

    def fadeInLogo(self,loop=5):
        if loop <= 255:
            self.menuCanvas.delete('logo')
            self.logoImageFile.putalpha(loop)
            self.logoImage = ImageTk.PhotoImage(self.logoImageFile)
            self.menuCanvas.create_image(500,220,image=self.logoImage,tags=('logo'))
            self.master.after(40-int(40*self.testingReduceTime),genFunc(self.fadeInLogo,loop+5))
        else:
            self.initMenu()

    def initMenu(self):
        self.menuCanvas.create_text(500,400,text='RANDOM BATTLE',fill='white',font=self.MenuDPPtFont,tags=('random-battle'))
        self.menuCanvas.create_text(500,500,text='START DRAFT',fill='white',font=self.MenuDPPtFont,tags=('start-draft'))
        self.pointerImage = ImageTk.PhotoImage(Image.open('assets/menu/pointer.png'))
        self.menuCanvas.create_image(300,400,image=self.pointerImage,tags=('pointer'))
        self.movePointerInAndOut()
        self.master.bind('<Down>',genFunc(self.movePointerDown))
        self.master.bind('<Up>',genFunc(self.movePointerUp))
        self.master.bind('<Return>',genFunc(self.selectOption))

    def selectOption(self):
        T = threading.Thread(target=genFunc(playsound,'sounds/select.mp3'))
        T.start()
        self.master.unbind('<Down>')
        self.master.unbind('<Up>')
        self.master.unbind('<Return>')
        self.doMovePointer = False
        if self.currentMenu == 'main':
            if self.menuCanvas.coords('pointer')[1] == 400:
                master.after(100,self.loadRandomBattle)
            elif self.menuCanvas.coords('pointer')[1] == 500:
                master.after(100,self.loadDraftingMenu)
        self.menuCanvas.delete('pointer')

    def movePointerInAndOut(self,flipFlop = 0):
        if flipFlop == 0 and self.doMovePointer:
            self.menuCanvas.move('pointer',-20,0)
            self.master.after(200,genFunc(self.movePointerInAndOut,1))
        elif self.doMovePointer:
            self.menuCanvas.move('pointer',20,0)
            self.master.after(200,genFunc(self.movePointerInAndOut,0))

    def movePointerDown(self):
        D = {'main':500,'drafting':600}
        if time.time() - self.timeSinceLastActivation < 0.05:
            return
        self.timeSinceLastActivation = time.time()
        coords = self.menuCanvas.coords('pointer')
        if coords[1] == D[self.currentMenu]:
            self.menuCanvas.move('pointer',0,-100)
        else:
            self.menuCanvas.move('pointer',0,100)

    def movePointerUp(self):
        if time.time() - self.timeSinceLastActivation < 0.05:
            return
        self.timeSinceLastActivation = time.time()
        coords = self.menuCanvas.coords('pointer')
        if coords[1] == 400:
            self.menuCanvas.move('pointer',0,100)
        else:
            self.menuCanvas.move('pointer',0,-100)

    def loadDraftingMenu(self,count=0):
        if count == 0:
            #self.menuCanvas.delete('random-battle')
            self.master.after(5,genFunc(self.loadDraftingMenu,1))
        elif count%2 == 1 and count < 9:
            self.menuCanvas.delete('start-draft')
            self.master.after(200,genFunc(self.loadDraftingMenu,count+1))
        elif count%2 == 0 and count < 9:
            self.menuCanvas.create_text(500,500,text='START DRAFT',fill='white',font=self.MenuDPPtFont,tags=('start-draft'))
            self.master.after(200,genFunc(self.loadDraftingMenu,count+1))
        elif 9 <= count <= 73:
            self.menuCanvas.move('random-battle',0,5)
            self.menuCanvas.move('start-draft',0,5)
            master.after(10,genFunc(self.loadDraftingMenu,count+1))
        elif 74 == count:
            self.menuCanvas.delete('random-battle')
            self.menuCanvas.delete('start-draft')
            self.menuCanvas.create_text(500,400+325,text='-  Number of Rounds: 2  +',fill='white',font=self.MenuDPPtFont,tags=('numRounds'))
            self.menuCanvas.create_text(500,500+325,text='-  Pokemon Per Round: 6  +',fill='white',font=self.MenuDPPtFont,tags=('pokemonPerRound'))
            self.menuCanvas.create_text(500,600+325,text='START DRAFT',fill='White',font=self.MenuDPPtFont,tags=('start-draft'))
            master.after(10,genFunc(self.loadDraftingMenu,count+1))
        elif 75 <= count <= 139:
            self.menuCanvas.move('numRounds',0,-5)
            self.menuCanvas.move('pokemonPerRound',0,-5)
            self.menuCanvas.move('start-draft',0,-5)
            master.after(10,genFunc(self.loadDraftingMenu,count+1))
        elif 140 == count:
            self.menuCanvas.create_image(200,400,image=self.pointerImage,tags=('pointer'))
            self.doMovePointer = True
            self.movePointerInAndOut()
            self.currentMenu = 'drafting'
            self.master.bind('<Down>',genFunc(self.movePointerDown))
            self.master.bind('<Up>',genFunc(self.movePointerUp))
            
    def loadRandomBattle(self):
        pass

master = Tk()
master.geometry('1000x700')
Menu = menuApp(master)
mainloop()
