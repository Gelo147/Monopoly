from tkinter import *
from tkinter import scrolledtext as st
from tkinter import ttk

class Wid(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.marker = False
        #Parent and main container
        self.myParent = parent
        self.main_container = Frame(parent, background="gray")
        self.main_container.pack(side="top", fill="both", expand=True)

        #Top frame for top horizontal bar
        self.top_frame = Frame(self.main_container, background="green")
        self.top_frame.pack(side="top", fill="both", expand=False)

        #Bottom frame for everything else
        self.bottom_frame = Frame(self.main_container, background="yellow")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)

        #Buffer labels due to grid being a prick
        #It's kinda cheating but it works
        self.buffer1 = Label(self.top_frame, height=2, width=5, bg="blue")
        self.buffer1.grid(row=0, column=1)

        self.buffer2 = Label(self.top_frame, height=2, width=5, bg="blue")
        self.buffer2.grid(row=0, column=2)

        self.buffer3 = Label(self.top_frame, height=2, width=5, bg="blue")
        self.buffer3.grid(row=0, column=3)

        #Adding test label and quit button
        self.money = Label(self.top_frame, text="$$$$", height=2, width=10, fg="red")
        self.money.grid(row=0, column=4)

        #Quit button needed as gui diables normal toolbars and forces constant fullscreen
        self.quuit = Button(self.top_frame, text="X", command=root.destroy, height=2, width=5, fg="green")
        self.quuit.grid(row=0, column=0)

        #Left frame containing board and maybe labels
        self.left_frame = Frame(self.bottom_frame, background="purple")
        self.left_frame.grid(row=0, column=0)

        #Right frame for log and other bits
        self.right_frame = Frame(self.bottom_frame, background="blue", height=80, width=50)
        self.bottom_frame.grid_columnconfigure(11, weight=1)
        self.right_frame.grid(row=0, column=11)

        #Chat_box
        self.chat_box = st.ScrolledText(self.right_frame, width=30, height=0, undo=True)
        self.chat_box.pack(side="bottom", fill="x", expand=False)
        self.chat_box.bind("<Return>", self.toLabel)

        #Log
        self.log = st.ScrolledText(self.right_frame, width=90, wrap="word", height=50)
        self.log.pack(side="left", fill="both", expand=True)

        #Making buttons
        bh = 4
        bw = 10
        buttons = []
        for i in range(40):
            buttons.append(Button(self.left_frame, text="b"+str(i), height=bh, width=bw, command=self.create_window))
        
        #Positioning buttons
        r = 0
        c = 0
        for button in buttons:
            button.grid(row=r, column=c)
            if r == 0 and c < 10:
                c += 1
            elif c == 10 and r < 10:
                r += 1
            elif r == 10 and c > 0:
                c -= 1
            else:
                r -= 1

    def toLabel(self, *args):
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

    def create_window(self):
        toplevel = Toplevel(self)
        toplevel.wm_title("Card __")
        name = Label(toplevel, text="name goes here", fg="purple", height=5, width=8)
        name.pack(side="top", fill="both", expand=True)
#Main
if __name__ == "__main__":
    root=Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    #Overrides tooltips and forces gui to persist on screen
    root.overrideredirect(1)
    #Makes full screen
    root.geometry("%dx%d+0+0" % (w, h))
    wid = Wid(root)
    root.mainloop()
