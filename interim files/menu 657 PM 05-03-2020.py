from tkinter import *
from tkinter import font
from PIL import Image, ImageTk

def genFunc(f, *args):
    return lambda *args2: f(*args)

class menuApp:
    def __init__(self,master):
        self.master = master
        ##these locations for canvas *just* manage to get it to fill the screen
        self.menuCanvas = Canvas(master,bg='black',height=700,width=1000)
        self.menuCanvas.place(x=-2,y=-1)
        
        self.MenuDPPtFont = font.Font(family='Pokemon DPPt',size=100)
        self.menuCanvas.create_text(500,80-120,text='POKEMON HORIZONS',fill='white',font=self.MenuDPPtFont,tags=('main-text'))
        self.logoImageFile = Image.open('assets/logo.png').resize((int(360*1.7),int(100*1.7)))
        self.logoImageFile.putalpha(5)
        self.logoImage = ImageTk.PhotoImage(self.logoImageFile)
        self.menuCanvas.create_image(500,220,image=self.logoImage,tags=('logo'))

        self.moveDownText()

    def moveDownText(self,loop=0):
        if loop < 20:
            self.menuCanvas.move('main-text',0,5)
            print(self.menuCanvas.coords('main-text'))
            master.after(50,genFunc(self.moveDownText,loop+1))
        else:
            self.fadeInLogo()

    def fadeInLogo(self,loop=5):
        if loop <= 255:
            self.menuCanvas.delete('logo')
            self.logoImageFile.putalpha(loop)
            self.logoImage = ImageTk.PhotoImage(self.logoImageFile)
            self.menuCanvas.create_image(500,220,image=self.logoImage,tags=('logo'))
            master.after(50,genFunc(self.fadeInLogo,loop+5))

master = Tk()
master.geometry('1000x700')
Menu = menuApp(master)
mainloop()
