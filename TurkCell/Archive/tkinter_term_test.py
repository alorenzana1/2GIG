import Tkinter as tk
import sys

class ExampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        toolbar = tk.Frame(self)
        toolbar.pack(side="top", fill="x")
        b1 = tk.Button(self, text="print to info", command=self.print_info)
        b2 = tk.Button(self, text="print to warn", command=self.print_warn)
        b3 = tk.Button(self, text="print to error", command=self.print_error)
        b1.pack(in_=toolbar, side="left")
        b2.pack(in_=toolbar, side="left")
        b3.pack(in_=toolbar, side="left")
        import ScrolledText
        self.text = ScrolledText.ScrolledText(self, state='disabled')
        self.text.pack(side="top", fill="both", expand=True)
        

        #sys.stdout = TextRedirector(self.text, "stdout")
        #sys.stderr = TextRedirector(self.text, "stderr")

        self.Logger = TextRedirector(self.text)

    def print_info(self):
        '''Illustrate that using 'print' writes to stdout'''
        self.Logger.info("Printing info to user")

    def print_warn(self):
        '''Illustrate that we can write directly to stderr'''
        self.Logger.warn("Printing info to user")

    def print_error(self):
        self.Logger.error("Printing info to user")

class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget
        self.widget.tag_configure("error", foreground="red")
        self.widget.tag_configure("warn", foreground="yellow", background="black")
        self.widget.tag_configure("info", foreground="black")

    def write(self, str, tag):
        self.widget.configure(state="normal")
        self.widget.insert("end", str + '\n', (tag,))
        self.widget.configure(state="disabled")
        # Autoscroll to the bottom
        self.widget.yview(tk.END)

    def info(self, msg):
        self.write(msg,"info")

    def warn(self, msg):
        self.write(msg,"warn")

    def error(self, msg):
        self.write(msg,"error")

app = ExampleApp()
app.mainloop()