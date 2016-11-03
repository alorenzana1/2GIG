#!/usr/bin/env python

# Built-in modules
import logging
import Tkinter
import threading

logger = logging.getLogger()

class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(Tkinter.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(Tkinter.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

def printing():
    logger.debug('printing message') 
    print "test"

# Sample usage
if __name__ == '__main__':
    # Create the GUI
    root = Tkinter.Tk()

    import ScrolledText
    st = ScrolledText.ScrolledText(root, state='disabled')
    st.configure(font='TkFixedFont')
    st.pack()

    # Create textLogger
    text_handler = TextHandler(st)
    btn = Tkinter.Button(root,text=u"print", command = printing)
    btn.pack()
    

    logger.setLevel(logging.DEBUG)
    # create formatter
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #LOGFORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
    #from colorlog import ColoredFormatter
    #formatter = ColoredFormatter(LOGFORMAT)

    # add formatter to ch
    #text_handler.setFormatter(formatter)
    # Add the handler to logger
    logger.addHandler(text_handler)


    # Log some messages
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')


    root.mainloop()