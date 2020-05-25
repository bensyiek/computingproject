from tkinter import *

class menuApp:
    def __init__(self,master):
        self.master = master
        self.backFrame = Canvas(master,bg='black',height=700,width=1000)
        self.backFrame.pack()
        

master = Tk()
master.geometry('1000x700')
Menu = menuApp(master)
mainloop()

