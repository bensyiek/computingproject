from tkinter import *
from CustomFont import *
from PIL import Image, ImageTk

master = Tk()
master.geometry('500x500')

backgrounds = {
    'route' : {'filePath' : 'routeBackground.png', 'bgColor' : 'green'}
    }

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
        self.label = Label(master=self.battleFrame,image=self.background)
        self.label.pack()

        self.textFrame = Frame(master,relief=RAISED,borderwidth=5,height=150,width=350,bg='white')
        self.textFrame.grid(row=1,column=0,sticky=W+E+N+S)

        self.buttonFrame = Frame(master,height=150,width=150,bg='blue',relief=RAISED,bd=5)
        self.buttonFrame.grid(row=1,column=1,sticky=W+E+N+S)

        self.fightButton = Button(self.buttonFrame,height=50,width=50,bg='red',fg='white',command = lambda: self.runText("Snorlax used Body Slam! Oh dear... The opposing skitty died."))
        self.fightButton.place(x=0,y=0,anchor='nw')
        self.switchButton = Button(self.buttonFrame,height=50,width=50,bg='blue',fg='white')
        self.switchButton.place(x=0,y=70,anchor='nw')

        self.textBox0 = CustomFont_Label(self.textFrame,text="",font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
        self.textBox0.place(x=10,y=32,anchor='w')
        self.textBox1 = CustomFont_Label(self.textFrame,text="",font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
        self.textBox1.place(x=10,y=67,anchor='w')
        self.textBox2 = CustomFont_Label(self.textFrame,text="",font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
        self.textBox2.place(x=10,y=102,anchor='w')

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

    def runText(self,text):

        ## As the CustomFont things are stored as images, we have to update the entire screen everytime we want to do the rpgscroll
        ## thing. So this basically will iterate through the three textBoxes (0-2) using modulo 3. I'm using the DPPt font because
        ## it's the best font, brings back nostalgia, and looks pokemon.

        ## I also need to add that it should just stop processing if it ends on a space character.
        ## turns the text into a list of characters
        buttonText = '' ## we will be adding to this, character by character.
        textCount = 0
        self.tBoxPointer = 0
        if self.tBoxPointer == 0:
            self.clearText() ## Eventually, this will be changed to waiting for the player to either click,
                                             ## press enter, etc. But for right now, it's automatic.
        for character in text:
            buttonText += character
            if self.tBoxPointer == 0:
                self.textBox0 = CustomFont_Label(self.textFrame,text=buttonText,font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
                self.textBox0.place(x=10,y=32,anchor='w')
            elif self.tBoxPointer == 1:
                self.textBox1 = CustomFont_Label(self.textFrame,text=buttonText,font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
                self.textBox1.place(x=10,y=67,anchor='w')
            elif self.tBoxPointer == 2:
                self.textBox2 = CustomFont_Label(self.textFrame,text=buttonText,font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
                self.textBox2.place(x=10,y=102,anchor='w')
            if len(buttonText) >= 25: ## i tested it, and with 35 pt font, it's approximately 25 characters that can fit before a new line is needed
                self.tBoxPointer = (self.tBoxPointer + 1) % 3
                master.after(45,self.skip)
                buttonText = ''
            self.textBox0.update()
            master.after(10)
            

    def skip(self): ## this basically does nothing so I can call master.after with no consequences. idk really what .after is, so this just sorta suffices
        pass

    def clearText(self): ## used to clear all text from the frame. Makes it so that we can write more text to the board.
        #self.textBox0 = CustomFont_Label(self.textFrame,text="",font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
        self.textBox0.destroy()
        self.textBox1.destroy()
        self.textBox2.destroy()
        #self.textBox0.place(x=10,y=32,anchor='w')
        #self.textBox1 = CustomFont_Label(self.textFrame,text="",font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
        #self.textBox1.place(x=10,y=67,anchor='w')
        #self.textBox2 = CustomFont_Label(self.textFrame,text="",font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
        #self.textBox2.place(x=10,y=102,anchor='w')

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

#     CustomFont_Label(root, text="This is a text", font_path="Pokemon DPPt.ttf", size=30).pack()
#     CustomFont_Message(root, text=lorem_ipsum, width=40, font_path="Pokemon DPPt.ttf", size=30).pack(pady=(30,0))
    

