from Tkinter import *

def blink():
    e.config(bg='green')
    e.after(1000, lambda: e.config(bg='white')) # after 1000ms

root = Tk()
e = Entry(root)
e.pack()
b = Button(root, text='blink', command=blink)
b.pack()
root.mainloop()