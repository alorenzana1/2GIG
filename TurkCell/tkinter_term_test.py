from Tkinter import *
import sys

class Display(Frame):
    ''' Demonstrate python interpreter output in Tkinter Text widget

type python expression in the entry, hit DoIt and see the results
in the text pane.'''
    
    def __init__(self,parent=0):
       Frame.__init__(self,parent)
       self.entry = Entry(self)
       self.entry.pack()
       self.doIt = Button(self,text="DoIt", command=self.onEnter)
       self.doIt.pack()
       self.output = Text(self)
       self.output.pack()
       sys.stdout = self
       self.pack()

    def onEnter(self):
        print eval(self.entry.get())

    def write(self, txt):
        self.output.insert(END,str(txt))

if __name__ == '__main__':
    Display().mainloop()