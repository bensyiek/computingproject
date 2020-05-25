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

        self.fightButton = Button(self.buttonFrame,height=50,width=50,bg='red',fg='white')
        self.fightButton.place(x=0,y=0,anchor='nw')
        self.switchButton = Button(self.buttonFrame,height=50,width=50,bg='blue',fg='white')
        self.switchButton.place(x=0,y=70,anchor='nw')

        self.textBox = CustomFont_Label(self.textFrame,text="Snorlax used Body Slam!",font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
        self.textBox.place(x=10,y=32,anchor='w')
        self.textBox2 = CustomFont_Label(self.textFrame,text="Oh dear...",font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
        self.textBox2.place(x=10,y=67,anchor='w')
        self.textBox3 = CustomFont_Label(self.textFrame,text="The opposing Skitty died.",font_path="Pokemon DPPt.ttf",size=35,bg='white',anchor='center')
        self.textBox3.place(x=10,y=102,anchor='w')

        #self.fightButton = Button(self.secondFrame,text='FIGHT',command=self.fadeaway)
        #self.fightButton.place()
        #self.switchButton = Button(self.secondFrame,text='SWITCH',command=self.fadeaway)
        #self.switchButton.place()

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
    

