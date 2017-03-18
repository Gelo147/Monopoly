from Client import *
from Board import *
from tkinter import *
from tkinter import scrolledtext as st

class Wid(Frame):
    def __init__(self, parent, name, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.name = name
        self.colours = {"lightgreen":"#CDE6D0","darkgreen":"#66b26f"}
        self.buttons = []
        self.toplevel = None
        self.marker = False
        #Parent and main container
        self.myParent = parent
        w, h = self.myParent.winfo_screenwidth(), self.myParent.winfo_screenheight()
        self.myParent.overrideredirect(1)
        self.myParent.geometry("%dx%d+0+0" % (w, h))
        self.board = Board("text/full_board.txt", [(0 ,"Jack"), (1 , "Crn"), (2  ,"Brain")])
        self.createGUI()
        #self.myParent.mainloop()

    def createGUI(self):        
        self.main_container = Frame(self.myParent, background="gray")
        self.main_container.pack(side="top", fill="both", expand=True)

        #Top frame for top horizontal bar
        self.top_frame = Frame(self.main_container, background="green")
        self.top_frame.pack(side="top", fill="both", expand=False)

        #Bottom frame for everything else
        self.bottom_frame = Frame(self.main_container, background=self.colours["darkgreen"])
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)

        #Buffer labels due to grid being a prick
        #It's kinda cheating but it works
        self.buffer1 = Label(self.top_frame, height=2, width=5, bg="green")
        self.buffer1.grid(row=0, column=1)

        self.buffer2 = Label(self.top_frame, height=2, width=5, bg="green")
        self.buffer2.grid(row=0, column=2)

        self.buffer3 = Label(self.top_frame, height=2, width=5, bg="green")
        self.buffer3.grid(row=0, column=3)

        #Adding money label
        self.money = Label(self.top_frame, text="$$$$", height=2, width=10, fg="red")
        self.money.grid(row=0, column=4)

        self.buffer4 = Label(self.top_frame, height=2, width=5, bg="green")
        self.buffer4.grid(row=0, column=5)

        self.buffer5 = Label(self.top_frame, height=2, width=5, bg="green")
        self.buffer5.grid(row=0, column=6)

        self.buffer6 = Label(self.top_frame, height=2, width=5, bg="green")
        self.buffer6.grid(row=0, column=7)

        #Roll button
        self.roll = Button(self.top_frame, command=self.MakeChoice, height=2, width=5, bg="red", text="test",)
        self.roll.grid(row=0, column=8)

        self.buffer7 = Label(self.top_frame, height=2, width=5, bg="green")
        self.buffer7.grid(row=0, column=9)

        self.buffer8 = Label(self.top_frame, height=2, width=5, bg="green")
        self.buffer8.grid(row=0, column=10)

        self.buffer9 = Label(self.top_frame, height=2, width=5, bg="green")
        self.buffer9.grid(row=0, column=11)

        self.buffer10 = Label(self.top_frame, height=2, width=5, bg="green")
        self.buffer10.grid(row=0, column=12)

        self.buffer11 = Label(self.top_frame, height=2, width=5, bg="green")
        self.buffer11.grid(row=0, column=13)

        self.buffer12 = Label(self.top_frame, height=2, width=25, bg="green")
        self.buffer12.grid(row=0, column=14)

        self.titlelabel = Label(self.top_frame, height=2, width=10, text="MONOPOLOY", fg="blue")
        self.titlelabel.grid(row=0, column=15)
        
    
        #Quit button needed as gui diables normal toolbars and forces constant fullscreen
        self.quuit = Button(self.top_frame, text="X", command=root.destroy, height=2, width=5, fg="green")
        self.quuit.grid(row=0, column=0)

        #Left frame containing board and maybe labels
        self.left_frame = Frame(self.bottom_frame, background=self.colours["lightgreen"])
        self.left_frame.grid(row=0, column=0)

        #Right frame for log and other bits
        self.right_frame = Frame(self.bottom_frame, background="blue", height=80, width=50)
        self.bottom_frame.grid_columnconfigure(11, weight=1)
        self.right_frame.grid(row=0, column=11)

        #Chat_box
        self.chat_box = st.ScrolledText(self.right_frame, width=30, height=0, undo=True)
        self.chat_box.pack(side="bottom", fill="x", expand=False)
        self.chat_box.bind("<Return>", self.toLog)

        #Log
        self.log = st.ScrolledText(self.right_frame, width=45, wrap="word", height=50)
        self.log.pack(side="bottom", fill="both", expand=True)

        #Making buttons
        bh = 4
        bw = 15
        for i in range(40):
            self.buttons.append(Button(self.left_frame, height=bh, width=bw,wraplength=100, command= lambda x=i: self.create_window(x)))
            print(i)

        #buttons[10]["text"] = "go to jail"
        for i in range(0, 40):
            space = self.board.getSpace(i)
            print(i,space)
            self.buttons[i]["text"] = space.getText()
        
        #Positioning buttons
        r = 0
        c = 0
        for button in self.buttons:
            button.grid(row=r, column=c)
            if r == 0 and c < 10:
                c += 1
            elif c == 10 and r < 10:
                r += 1
            elif r == 10 and c > 0:
                c -= 1
            else:
                r -= 1

        self.myParent.mainloop()

    #Adds text onto log
    def toLog(self, *args):
        self.log.config(state="normal")
        if not self.marker:
            text = ">" + self.chat_box.get("1.0", "end-1c")
            self.marker = True
        else:
            box = self.chat_box.get("1.0", END)
            box = box[1:]
            text = ">" + box
        self.log.insert("1.0", text)
        self.log.config(state="disabled")
        self.chat_box.delete("1.0", END)

    def create_window(self, i):
        space = self.board.getSpace(i)

        ownText="No Owner"
        uText="Unoccupied"
        oText=""
        found = False

        #Kill window if it already exists
        #Ensures only one window is open at a time
        if self.toplevel:
            self.toplevel.destroy()

        #Make new window        
        self.toplevel = Toplevel(self, height=50, width=60)

        #Fix size of new window and stop people making it smaller/bigger
        self.toplevel.resizable(width=False, height=False)
        self.toplevel.minsize(width=444, height=444)
        self.toplevel.maxsize(width=444, height=444)
        
        self.toplevel.update_idletasks()
        w = self.toplevel.winfo_screenwidth()
        h = self.toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in self.toplevel.geometry().split("+")[0].split("x"))
        x = w/2 - size[0]/2
        x -= 300
        y = h/2 - size[1]/2
        self.toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))
        
        self.toplevel.wm_title("Card __")

        #Add labels as such:
        #name
        #rent
        #cost
        #owned
        #occupied        
        name = Label(self.toplevel, text=str(self.board.getSpace(i).getText()),fg="purple", bg="gray", height=5, width=30)
        name.pack(side="top", fill="y", expand=False)

        occupied = Label(self.toplevel, fg="orange", bg="gray", height=5, width=30)
        occupied.pack(side="top", fill="y", expand=False)

        for player in self.board.getPlayerList():
            if player.getPosition() == i:
                oText += str(player.getName()) + "\n"
            if oText:
                found = True

        if found:
            occupied["text"] = oText
        else:
            occupied["text"] = uText

        if space.getType() == "PROPERTY":
            rent = Label(self.toplevel, text=str(self.board.getSpace(i).getRent()), fg="red", bg="gray", height=5, width=30)
            rent.pack(side="top", fill="y", expand=False)

            cost = Label(self.toplevel, text=str(self.board.getSpace(i).getPrice()), fg="blue", bg="gray", height=5, width=30)
            cost.pack(side="top", fill="y", expand=False)

            owner = self.board.getSpace(i).getOwner()
            if owner:
                ownText = owner
            owned = Label(self.toplevel, text=str(ownText), fg="green", bg="gray", height=5, width=30)
            owned.pack(side="top", fill="y", expand=False)

        elif space.getType() == "TAX":
            fee = Label(self.toplevel, text=str(space.getFee()), fg="blue", bg="gray", height=5, width=30)
            fee.pack(side="top", fill="y", expand=False)

        #OK button to close window
        OKbutton = Button(self.toplevel, bg="blue", height=5, width=30, text="OK", command=self.toplevel.destroy)
        OKbutton.pack(side="top", fill="y", expand=False)

    #Method to be called when player lands on unoccupied property
    def MakeChoice(self):
        #Make new window        
        self.decision = Toplevel(self, height=50, width=60)

        #Fix size of new window and stop people making it smaller/bigger
        self.decision.resizable(width=False, height=False)
        self.decision.minsize(width=333, height=333)
        self.decision.maxsize(width=333, height=333)
        
        self.decision.update_idletasks()
        w = self.decision.winfo_screenwidth()
        h = self.decision.winfo_screenheight()
        size = tuple(int(_) for _ in self.decision.geometry().split("+")[0].split("x"))
        x = w/2 - size[0]/2
        x += 300
        y = h/2 - size[1]/2
        self.decision.geometry("%dx%d+%d+%d" % (size + (x, y)))

        prop = "WGB" #Need to change
        txt = "Would you like to buy this property: " + prop
        question = Label(self.decision, fg="purple", text=txt, height=5, width=30)
        question.pack(side="top", fill="x", expand=False)        
            
        yes = Button(self.decision, fg="red", height=5, command=self.ChooseYes, width=30, text="yes")
        yes.pack(side="top", fill="x", expand=False)

        no = Button(self.decision, fg="red", height=5, command=self.ChooseNo, width=30, text="no")
        no.pack(side="top", fill="x", expand=False)


    def ChooseYes(self):
        self.decision.destroy()
        pass

    def ChooseNo(self):
        self.decision.destroy()
        pass

root = Tk()
wid = Wid(root, "")
