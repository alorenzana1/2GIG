from Tkinter  import *

ALL=N+S+E+W

class Application(Frame):

    def __init__(self,master=None):
        Frame.__init__(self,master)

        # the UI is made up of two major areas: a bottom row
        # of buttons, and a top area that fills the result of 
        # UI
        top_frame = Frame(self)
        button_frame = Frame(self)

        button_frame.pack(side="bottom", fill="x")
        top_frame.pack(side="top", fill="both", expand=True)

        # top frame is made up of three sections: two smaller
        # regions on the left, and a larger region on the right
        ul_frame = Frame(top_frame, background="green", width=200)
        ll_frame = Frame(top_frame, background="blue", width=200)
        right_frame = Frame(top_frame, background="red")

        ul_frame.grid(row=0, column=0, sticky=ALL)
        ll_frame.grid(row=1, column=0, sticky=ALL)
        right_frame.grid(row=0, column=1, rowspan=2, sticky=ALL)
        top_frame.columnconfigure(1, weight=1)
        top_frame.rowconfigure(0, weight=1)
        top_frame.rowconfigure(1, weight=1)

        # the right frame is made up of two widgets, an entry
        # on top and a text below
        entry = Entry(right_frame)
        text = Text(right_frame)

        entry.pack(side="top", fill="x")
        text.pack(side="top", fill="both", expand=True)

        # the button frame has five equally spaced buttons
        for color in ('Red', 'Blue', 'Green', 'Black'):
            b = Button(button_frame, text=color)
            b.pack(side="left", fill="x", expand=True)
        quit_button = Button(button_frame, text="Quit")
        quit_button.pack(side="left", fill="x", expand=True)

root = Tk()
app = Application(root)
app.pack(fill="both", expand=True)
root.mainloop()