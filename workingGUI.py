from tkinter import *

class Wid():
	def __init__(self, parent):
		#Parent and main container
		self.myParent = parent
		self.main_container = Frame(parent, background="gray")
		self.main_container.pack(side="top", fill="both", expand=True)

		#Top frame for top horizontal bar
		self.top_frame = Frame(self.main_container, background="green")
		self.top_frame.pack(side="top", fill="both", expand=False)


		self.bottom_frame = Frame(self.main_container, background="yellow")
		self.bottom_frame.pack(side="bottom", fill="both", expand=True)

		#Adding test label and quit button
		self.label1 = Label(self.top_frame, text="mgh", height=2, width=5, fg="red")
		self.top_frame.grid_rowconfigure(0, weight=1)
		self.top_frame.grid_columnconfigure(5, weight=1)
		self.label1.grid(row=0, column=5)

		#Quit button needed as gui diables normal toolbars and forces constant fullscreen
		self.quuit = Button(self.top_frame, text="X", command=root.destroy, height=2, width=5, fg="green")
		self.quuit.grid(row=0, column=3)

		#Left frame containing board and maybe labels
		self.left_frame = Frame(self.bottom_frame, background="purple")
		self.left_frame.grid(row=0, column=0)

		#Right frame for log and other bits
		self.right_frame = Frame(self.bottom_frame, background="blue", height=80, width=50)
		self.bottom_frame.grid_columnconfigure(11, weight=1)
		self.right_frame.grid(row=0, column=11)

		self.chat_box = Text(self.right_frame, bg="grey", width=20, height=5)
		self.chat_box.pack(side="bottom", fill="x", expand=False)

		#Test label
		self.log_label = Label(self.right_frame, bg="blue", width=50, height=62)
		self.log_label.pack(side="bottom", fill="both", expand=True)


		#Making the buttons
		#I WILL MAKE THIS MORE EFFICIENT
		self.b0 = Button(self.left_frame, text="b0", height=5, width=10)
		self.b1 = Button(self.left_frame, text="b1", height=5, width=10)
		self.b2 = Button(self.left_frame, text="b2", height=5, width=10)
		self.b3 = Button(self.left_frame, text="b3", height=5, width=10)
		self.b4 = Button(self.left_frame, text="b4", height=5, width=10)
		self.b5 = Button(self.left_frame, text="b5", height=5, width=10)
		self.b6 = Button(self.left_frame, text="b6", height=5, width=10)
		self.b7 = Button(self.left_frame, text="b7", height=5, width=10)
		self.b8 = Button(self.left_frame, text="b8", height=5, width=10)
		self.b9 = Button(self.left_frame, text="b9", height=5, width=10)
		self.b10 = Button(self.left_frame, text="b10", height=5, width=10)
		self.b11 = Button(self.left_frame, text="b11", height=5, width=10)
		self.b12 = Button(self.left_frame, text="b12", height=5, width=10)
		self.b13 = Button(self.left_frame, text="b13", height=5, width=10)
		self.b14 = Button(self.left_frame, text="b14", height=5, width=10)
		self.b15 = Button(self.left_frame, text="b15", height=5, width=10)
		self.b16 = Button(self.left_frame, text="b16", height=5, width=10)
		self.b17 = Button(self.left_frame, text="b17", height=5, width=10)
		self.b18 = Button(self.left_frame, text="b18", height=5, width=10)
		self.b19 = Button(self.left_frame, text="b19", height=5, width=10)
		self.b20 = Button(self.left_frame, text="b20", height=5, width=10)
		self.b21 = Button(self.left_frame, text="b21", height=5, width=10)
		self.b22 = Button(self.left_frame, text="b22", height=5, width=10)
		self.b23 = Button(self.left_frame, text="b23", height=5, width=10)
		self.b24 = Button(self.left_frame, text="b24", height=5, width=10)
		self.b25 = Button(self.left_frame, text="b25", height=5, width=10)
		self.b26 = Button(self.left_frame, text="b26", height=5, width=10)
		self.b27 = Button(self.left_frame, text="b27", height=5, width=10)
		self.b28 = Button(self.left_frame, text="b28", height=5, width=10)
		self.b29 = Button(self.left_frame, text="b29", height=5, width=10)
		self.b30 = Button(self.left_frame, text="b30", height=5, width=10)
		self.b31 = Button(self.left_frame, text="b31", height=5, width=10)
		self.b32 = Button(self.left_frame, text="b32", height=5, width=10)
		self.b33 = Button(self.left_frame, text="b33", height=5, width=10)
		self.b34 = Button(self.left_frame, text="b34", height=5, width=10)
		self.b35 = Button(self.left_frame, text="b35", height=5, width=10)
		self.b36 = Button(self.left_frame, text="b36", height=5, width=10)
		self.b37 = Button(self.left_frame, text="b37", height=5, width=10)
		self.b38 = Button(self.left_frame, text="b38", height=5, width=10)
		self.b39 = Button(self.left_frame, text="b39", height=5, width=10)

		#Positioning buttons
		#WILL BE MORE NICE
		self.b0.grid(row=0, column=0)
		self.b1.grid(row=0, column=1)
		self.b2.grid(row=0, column=2)
		self.b3.grid(row=0, column=3)
		self.b4.grid(row=0, column=4)
		self.b5.grid(row=0, column=5)
		self.b6.grid(row=0, column=6)
		self.b7.grid(row=0, column=7)
		self.b8.grid(row=0, column=8)
		self.b9.grid(row=0, column=9)
		self.b10.grid(row=0, column=10)
		self.b11.grid(row=1, column=10)
		self.b12.grid(row=2, column=10)
		self.b13.grid(row=3, column=10)
		self.b14.grid(row=4, column=10)
		self.b15.grid(row=5, column=10)
		self.b16.grid(row=6, column=10)
		self.b17.grid(row=7, column=10)
		self.b18.grid(row=8, column=10)
		self.b19.grid(row=9, column=10)
		self.b20.grid(row=10, column=10)
		self.b21.grid(row=10, column=9)
		self.b22.grid(row=10, column=8)
		self.b23.grid(row=10, column=7)
		self.b24.grid(row=10, column=6)
		self.b25.grid(row=10, column=5)
		self.b26.grid(row=10, column=4)
		self.b27.grid(row=10, column=3)
		self.b28.grid(row=10, column=2)
		self.b29.grid(row=10, column=1)
		self.b30.grid(row=10, column=0)
		self.b31.grid(row=9, column=0)
		self.b32.grid(row=8, column=0)
		self.b33.grid(row=7, column=0)
		self.b34.grid(row=6, column=0)
		self.b35.grid(row=5, column=0)
		self.b36.grid(row=4, column=0)
		self.b37.grid(row=3, column=0)
		self.b38.grid(row=2, column=0)
		self.b39.grid(row=1, column=0)

#Main
root=Tk()
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
#Overrides tooltips and forces gui to persist on screen
root.overrideredirect(1)
#Makes full screen
root.geometry("%dx%d+0+0" % (w, h))
wid = Wid(root)
root.mainloop()