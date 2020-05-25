from tkinter import *
from tkinter import font
from PIL import Image, ImageTk
import time
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

        self.moveDownText()

    def moveDownText(self,loop=0):
        if loop < 120:
            self.menuCanvas.move('main-text',0,1)
            self.master.after(2,genFunc(self.moveDownText,loop+1))
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

    def selectOption(self):
        playsound('sounds/select.mp3')
        self.master.unbind('<Down>')
        self.master.unbind('<Up>')
        if self.currentMenu == 'main':
            if self.menuCanvas.coords('pointer')[1] == 400:
                self.loadRandomBattle()
            elif self.menuCanvas.coords('pointer')[1] == 500:
                self.loadDraftingMenu()

    def movePointerInAndOut(self,flipFlop = 0):
        if flipFlop == 0:
            self.menuCanvas.move('pointer',-20,0)
            self.master.after(250,genFunc(self.movePointerInAndOut,1))
        else:
            self.menuCanvas.move('pointer',20,0)
            self.master.after(250,genFunc(self.movePointerInAndOut,0))

    def movePointerDown(self):
        if time.time() - self.timeSinceLastActivation < 0.05:
            return
        self.timeSinceLastActivation = time.time()
        coords = self.menuCanvas.coords('pointer')
        if coords[1] == 500:
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


    def loadRandomBattle(self):
        pass

master = Tk()
master.geometry('1000x700')
Menu = menuApp(master)
mainloop()
