from Client import *
from tkinter import *
from Lobby import *
from Search import *

class Front(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        self.client = Client()
        
        self.myparent = parent

        #Variables for sanity checks below
        self.creategametrue = False
        self.joingametrue = False
        self.joining = None
        self.creating = None

        self.createGui()
        self.myparent.mainloop()

    def createGui(self):
        self.main_container = Frame(self.myparent, background="gray")
        self.main_container.pack(side="bottom", fill="both", expand=True)

        #Title label
        self.hellolabel = Label(self.main_container, text="MONOPOLY", height=5, width=30)
        self.hellolabel.pack(side="top", fill="none", expand=False)

        #Create a game on the server
        self.create = Button(self.main_container, command=self.creategame, text="CREATE GAME", height=5, width=30)
        self.create.pack(side="top", fill="none", expand=False)

        #Join a game on the server
        self.join = Button(self.main_container, command=self.joingame, text="JOIN GAME", height=5, width=30)
        self.join.pack(side="top", fill="none", expand=False)

    def creategame(self):
        
        self.creategametrue = True #They clicked create game
        
        self.creating = Toplevel(self)

        #Instruction label
        self.instruction = Label(self.creating, text="Please enter name")
        self.instruction.pack(side="left", fill="none", expand=False)

        #Text box to enter name
        self.name = Entry(self.creating, width=15)
        self.name.pack(side="left", fill="none", expand=False)

        #Accept button
        self.accept = Button(self.creating, text="ACCEPT", command=self.acceptname, height=5, width=20)
        self.accept.pack(side="bottom", fill="none", expand=False)

        #Cancel button
        self.cancel = Button(self.creating, text="CANCEL", command=self.cancelname, height=5, width=20)
        self.cancel.pack(side="bottom", fill="none", expand=False)

    def joingame(self): #Same as above method, just the sanity variable is different

        self.joingametrue = True
        
        self.joining = Toplevel(self)

        self.instruction = Label(self.joining, text="Please enter name")
        self.instruction.pack(side="left", fill="none", expand=False)

        self.name = Entry(self.joining, width=15)
        self.name.pack(side="left", fill="none", expand=False)

        self.accept = Button(self.joining, text="ACCEPT", command=self.acceptname, height=5, width=20)
        self.accept.pack(side="bottom", fill="none", expand=False)

        self.cancel = Button(self.joining, text="CANCEL", command=self.cancelname, height=5, width=20)
        self.cancel.pack(side="bottom", fill="none", expand=False)

    def acceptname(self):
        #Accepts the name if not empty and joins/creates a game
        name = self.name.get()
        if name != "":
            if self.creategametrue:
                self.client.createGame(None, name, None)
                self.main_container.destroy()
                self.creating.destroy()
                lobby = Lobby(self.myparent, self.client, name, name)
            elif self.joingametrue:
                self.main_container.destroy()
                self.joining.destroy()
                search = Search(self.myparent, self.client, name)

    def cancelname(self):
        #Resets sanity variables and destroys window
        self.creategametrue = self.joingametrue = False
        if self.joining:
            self.joining.destroy()
        else:
            self.creating.destroy()

root = Tk()
front = Front(root)
