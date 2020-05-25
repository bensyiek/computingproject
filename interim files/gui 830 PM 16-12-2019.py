from tkinter import *
from PIL import Image, ImageTk
from tkinter import font
import time

master = Tk()
master.geometry('500x700')

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

trainerSprites = {'Cynthia' : 'assets/trainers/Blue.gif'}

toBe = '''To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles And by opposing end them. To die—to sleep, No more; and by a sleep to say we end The heart-ache and the thousand natural shocks That flesh is heir to: 'tis a consummation Devoutly to be wish'd. To die, to sleep; To sleep, perchance to dream—ay, there's the rub: For in that sleep of death what dreams may come, When we have shuffled off this mortal coil, Must give us pause—there's the respect That makes calamity of so long life. For who would bear the whips and scorns of time, Th'oppressor's wrong, the proud man's contumely, The pangs of dispriz'd love, the law's delay, The insolence of office, and the spurns That patient merit of th'unworthy takes, When he himself might his quietus make With a bare bodkin? Who would fardels bear, To grunt and sweat under a weary life, But that the dread of something after death, The undiscovere'd country, from whose bourn No traveller returns, puzzles the will, And makes us rather bear those ills we have Than fly to others that we know not of? Thus conscience does make cowards of us all, And thus the native hue of resolution Is sicklied o'er with the pale cast of thought, And enterprises of great pitch and moment With this regard their currents turn awry And lose the name of action.'''

def genFunc(f, *args):
    return lambda *args2: f(*args)

class app:
    def __init__(self,master):
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
        self.scrollPlatforms(1)

#------------------------------------------------------------------------------------------------------------------------------#
# The following are functions pertaining to the initialize of battles

    def initResources(self):
        pass

    def scrollPlatforms(self,init=1,userIm=False,trainerIm=False):
        if init:
            ##First initialize the sprites for the trainers and the platforms.
            ##Trainers initialized after platforms so that they show up on top.
            
            self.enemyPlatformImageFile = Image.open(assets['indoor-enemy'])
            self.enemyPlatformImageFile = self.enemyPlatformImageFile.resize((225,75))
            self.enemyPlatformImageFile = ImageTk.PhotoImage(self.enemyPlatformImageFile)
            self.enemyPlatform = self.battleCanvas.create_image(650,175,image=self.enemyPlatformImageFile,tags=('platform','enemy-platform'))
            
            self.enemyTrainerSpriteFile = Image.open(trainerSprites['Cynthia']) ##inits the gif file we will use later
            self.enemyTrainerSprite = ImageTk.PhotoImage(self.enemyTrainerSpriteFile.resize((141,141)))
            self.enemyTrainer = self.battleCanvas.create_image(650,175,image=self.enemyTrainerSprite,anchor=S,tags=("enemy-trainer"))

            self.userPlatformImageFile = Image.open(assets['indoor-user'])
            self.userPlatformImageFile = self.userPlatformImageFile.resize((325,40))
            self.userPlatformImageFile = ImageTk.PhotoImage(self.userPlatformImageFile)
            self.userPlatform = self.battleCanvas.create_image(-300,360,image=self.userPlatformImageFile,anchor=SW,tags=('platform','user-platform'))

            self.blackFile = Image.open('assets/black/black250.png')
            self.blackFile = self.blackFile.resize((500,355))
            self.blackFileTk = ImageTk.PhotoImage(self.blackFile)
            self.black = self.battleCanvas.create_image(0,0,image=self.blackFileTk,anchor=NW,tags=('black'))
            self.blackAlpha = 250
        else:
            ##then iterate until the platforms are in place.
            if self.battleCanvas.coords('enemy-platform')[0] == 350:
                self.runGif(self.enemyTrainerSpriteFile,'enemy-trainer')
                self.runText('You have been challenged by Pokemon Trainer Blue!')
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
                self.master.update()
        k = genFunc(self.scrollPlatforms,0)
        self.master.after(15,k)

    def sendOutFirstPokemon(self):
        if self.animRunning == 'enemy-trainer':
            master.after(50,self.sendOutFirstPokemon)
        else:
            master.after(500)

    def runGif(self,gif,canvasID,count=1):
        self.animRunning = canvasID
        ##takes a PIL image object, and canvasID (which refers to the tag I use to identify it)
        try:
            gif.seek(count) ##gif.seek() updates the gif to the frame index, gif.tell() returns curr index
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
            
        ##REFERENCE: finish userPlatform at (0,360) and enemyPlatform at (350,175)

#------------------------------------------------------------------------------------------------------------------------------#


    #def userPokemonFaint(self,pokemon):
    

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
