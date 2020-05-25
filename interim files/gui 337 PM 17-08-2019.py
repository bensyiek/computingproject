from tkinter import *
from PIL import Image, ImageTk
from tkinter import font

master = Tk()
master.geometry('500x700')

backgrounds = {
    'route' : {'filePath' : 'routeBackground.png', 'bgColor' : 'green'}
    }

triangleImage = 'trianglePointer.jpg'

toBe = '''To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles And by opposing end them. To die—to sleep, No more; and by a sleep to say we end The heart-ache and the thousand natural shocks That flesh is heir to: 'tis a consummation Devoutly to be wish'd. To die, to sleep; To sleep, perchance to dream—ay, there's the rub: For in that sleep of death what dreams may come, When we have shuffled off this mortal coil, Must give us pause—there's the respect That makes calamity of so long life. For who would bear the whips and scorns of time, Th'oppressor's wrong, the proud man's contumely, The pangs of dispriz'd love, the law's delay, The insolence of office, and the spurns That patient merit of th'unworthy takes, When he himself might his quietus make With a bare bodkin? Who would fardels bear, To grunt and sweat under a weary life, But that the dread of something after death, The undiscovere'd country, from whose bourn No traveller returns, puzzles the will, And makes us rather bear those ills we have Than fly to others that we know not of? Thus conscience does make cowards of us all, And thus the native hue of resolution Is sicklied o'er with the pale cast of thought, And enterprises of great pitch and moment With this regard their currents turn awry And lose the name of action.'''

class app:
    def __init__(self,master):
        global backgrounds
        self.master = master
        #master.grid_rowconfigure(0,weight=7) ##sets weighting for battle
        #master.grid_rowconfigure(1,weight=3)
        #master.grid_columnconfigure(0,weight=1)
        
        self.battleFrame = Frame(master,relief=SUNKEN,borderwidth=5,height=350,width=500,bg=backgrounds['route']['bgColor'])
        self.battleFrame.grid(row=0,column=0,sticky=W+E+N+S,columnspan=2)
        
        self.backgroundImageFile = Image.open(backgrounds['route']['filePath']) ## I'm using a dict so that I can store as base64 encoded later
        self.background = ImageTk.PhotoImage(self.backgroundImageFile)
        self.label = Label(master=self.battleFrame,image=self.background,bg='white')
        self.label.pack()
        self.DPPtFont = font.Font(family='Pokemon DPPt',size=26)
        self.battlefont = font.Font(family='Pokemon DPPt',size=26)
        
        self.textFrame = Frame(master,relief=RAISED,borderwidth=5,height=150,width=500,bg='white')
        self.textFrame.grid(row=1,column=0,sticky=W+E+N+S)

        self.textBox0 = Label(self.textFrame,text="Hello",font=self.DPPtFont,bg='white',anchor='center')
        self.textBox0.place(x=10,y=32,anchor='w')
        self.textBox1 = Label(self.textFrame,text="123456789012345678901234567890",font=self.DPPtFont,bg='white',anchor='center')
        self.textBox1.place(x=10,y=67,anchor='w')
        self.textBox2 = Label(self.textFrame,text="",font=self.DPPtFont,bg='white',anchor='center')
        self.textBox2.place(x=10,y=102,anchor='w')

        self.triangleImageFile = Image.open(triangleImage)
        self.triangleImageFile = ImageTk.PhotoImage(self.triangleImageFile)
        self.triangle = Label(master=self.textFrame,image=self.triangleImageFile,bg='white')

        self.buttonFrame = Frame(master,height=200,width=500,bg='blue',relief=RAISED,bd=5)
        self.buttonFrame.grid(row=2,column=0,sticky=W+E+N+S)

        global toBe
        self.fightButton = Button(self.buttonFrame,text='Hello!',height=50,width=50,command = lambda: self.runText(toBe))
        self.fightButton.place(x=0,y=0,anchor='nw')
        self.switchButton = Button(self.buttonFrame,height=50,width=50,bg='blue',fg='white')
        self.switchButton.place(x=0,y=70,anchor='nw')

        self.tBoxPointer = 0
        self.tBox = {
            '0' : self.textBox0,
            '1' : self.textBox1,
            '2' : self.textBox2
            }

        #self.fightButton = Button(self.secondFrame,text='FIGHT',command=self.fadeaway)
        #self.fightButton.place()
        #self.switchButton = Button(self.secondFrame,text='SWITCH',command=self.fadeaway)
        #self.switchButton.place()

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
        for word in text:
            if len(self.buttonText + word) <= 36: ## we need to first check to see if the word exceeds the character limit. i tested it, and with 35 pt font, it's approximately 25 characters that can fit before a new line is needed
                if len(self.buttonText + word) == 36:
                    self.addWord(word)
                else:
                    self.addWord(word + ' ') ## if we're here, the space fits. let's add it
                
            else:
                self.buttonText = ''
                self.tBoxPointer = (self.tBoxPointer + 1) % 3
                master.after(45)
                if self.tBoxPointer == 0:
                    self.waiting = True
                    master.bind("<Return>", self.notWaiting)
                    while self.waiting:
                        self.triangle.place(x=485,y=135,anchor='se')
                        master.update()
                        if not self.waiting:
                            break
                        master.after(200)
                        self.triangle.place(x=485,y=130,anchor='se')
                        master.update()
                        if not self.waiting:
                            break
                        master.after(200)
                    master.unbind("<Return>")
                    self.triangle.place_forget()
                    self.clearText()
                self.addWord(word + ' ')
        buttonText = ''

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
