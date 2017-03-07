from tkinter import *

class Search(Frame):
    def __init__(self, parent, client, name, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        self.client = client
        self.name = name
        self.games = None
        self.addresses = []

        self.index = 1

        self.myparent = parent

        self.maincontainer = Frame(parent, bg="gray")
        self.maincontainer.pack(side="top", fill="both", expand=True)

        self.titlelabel = Label(self.maincontainer, text="SEARCHING FOR GAMES", height=4, width=20)
        self.titlelabel.pack(side="top", fill="none", expand=False)

        self.searchlist = Listbox(self.maincontainer, selectmode="single")
        self.searchlist.pack(side="top", fill="both", expand=True)

        self.searchlist.bind("<<ListboxSelect>>", self.onselect)

        self.select = Button(self.maincontainer, command=self.selectgame, width=10, height=3, text="SELECT")
        self.select.pack(side="right", fill="none", expand=False)

        self.refresh = Button(self.maincontainer, command=self.refreshgames, width=10, height=3, text="REFRESH")
        self.refresh.pack(side="left", fill="none", expand=False)

        self.refreshgames()

    #Finds and displays games
    def refreshgames(self):
        self.selected = None
        self.addresses = []
        self.index = 1
        self.games = client.listGames()
        for game in self.games:
            self.addresses.append(game[1])
            self.searchlist.insert(self.index, "%s" % (game[0]))
            self.index += 1

    def onselect(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        self.selected = self.addresses[index-1]
    
    #Guessing client/server stuff happens here
    def selectgame(self):
        if not self.selected:
            return
        else:
            join(self.selected, self.name, None)
            self.destroy()
            lobby = Lobby(self.myparent, self.client, self.name)

    #Method to add things to box, such as found games
    def insertobox(self, data):
        self.searchlist.insert(self.index, str(data))
        self.index += 1

    #Method to reset index, does this if refresh is hit
    def reset(self):
        self.index = 1

if __name__ == "__main__":
    root=Tk()
    wid = Search(root)
    root.mainloop()
