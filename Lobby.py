from Client import *
from Client import *
from tkinter import *
from tkinter import scrolledtext as st
from time import sleep
from testbiggui import *

class Lobby(Frame):
    def __init__(self, parent, client, name, host, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        self.client = client
        self.name = name
        self.host = host

        self.marker = False

        self.myparent = parent

        self.maincontainer = Frame(parent, bg="gray")
        self.maincontainer.pack(side="top", fill="both", expand=True)

        self.titlelabel = Label(self.maincontainer, text=self.host + "'s LOBBY", height=4, width=20)
        self.titlelabel.pack(side="top", fill="none", expand=False)

        self.log = st.ScrolledText(self.maincontainer, width=90, wrap="word", height=30)
        self.log.pack(side="top", fill="both", expand=True)

        self.chat_box = st.ScrolledText(self.maincontainer, width=30, height=0, undo=True)
        self.chat_box.pack(side="top", fill="x", expand=False)
        self.chat_box.bind("<Return>", self.toLog)

        if name == host:
            self.startbutton = Button(self.maincontainer, width=20, height=5, text="start", command=self.start)
            self.startbutton.pack(side="left", fill="none", expand=False)

    def toLog(self, *args):
        self.log.config(state="normal")
        if not self.marker:
            text = self.chat_box.get("1.0", "end-1c")
            self.marker = True
        else:
            box = self.chat_box.get("1.0", END)
            text = box[1:]
        self.log.insert("1.0", ">" + self.name + " says:  " + text)
        self.log.config(state="disabled")
        self.chat_box.delete("1.0", END)

    def start(self):
        self.client.start()
        sleep(1)
        self.maincontainer.destroy()
        self.wid = Wid(self.myparent, self.client)
