import sys
import glob
import serial
import Tkinter
import AT
import threading
import time
import csv
import os
import time
import datetime

from FlexCheckSum import *

csv_header = ["SNID","TestDataTime","SimType","IMEI","IMSI","RevisionID","ModuleSWPN","ICCID","ModuleSN","SignalLevel1","SignalLevel2","DC-DC","TesterSN","CAL1900M","CAL850M","Result","CartonNo"]

IMEI ="""
N
Q50,0
A0,22,0,1,1,1,N,"IMEI: %s"
B0,0,0,3,1,2,20,N,"%s"
P1
"""


def serial_ports():
    """ 
    Lists serial port names
    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    Successfully tested on:
    Windows 8.1 x64, 
    Windows 10 x64, 
    Mac OS X 10.9.x / 10.10.x / 10.11.x
    Ubuntu 14.04 / 14.10 / 15.04 / 15.10
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class simpleapp_tk(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()
        self.atDevice = None
        self.CartonNo = None
        self.csv_file = ""
        
        """
        Looking for CSV under FTP_file folder, if does not exit that location create it
        and create csv file with header file.
        """
        if not os.path.exists("FTP_file"):
            os.makedirs("FTP_file")

        currentPath = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(currentPath,"FTP_file")
        
        for file in os.listdir(path):
            if file.endswith(".csv"):
                self.csv_file = os.path.join(path,file)
        
        #creating csv file if does not exist
        if(self.csv_file == ""):
            pathCSVFile = os.path.join(path,"test.csv")
            with open(pathCSVFile,'a+b') as file:
                wr = csv.writer(file,quoting=csv.QUOTE_NONE)
                wr.writerow(csv_header)
    def initialize(self):
        self.grid()
        
        """
        Creation of IMEI entry, 
        """
        self.entry = Tkinter.Entry(self)
        self.entry.grid(column=3,row=0)
        
        if os.path.isfile('nIMEI.bin'):
            with open('nIMEI.bin','r') as file:
                imei = file.read()
        else:
            with open('nIMEI.bin','w') as file:
                imei = "35337208000000"
                file.write(imei)
        
        print imei

        self.terminal = Tkinter.Frame(self,height=400, width=500)
        self.terminal.grid(column=6,row=0)
        wid = self.terminal.winfo_id()
        #os.system("cmd -into %d -geometry 40x20 -sb &" %wid)

        self.IMEI = Tkinter.StringVar()
        self.IMEI.set(imei)
        self.IMEIentry = Tkinter.Entry(self,textvariable=self.IMEI)
        self.IMEIentry.grid(column=5,row=0)
        
        self.SetCartonBtn = Tkinter.Button(self,text=u"Set Carton No", command = self.SetCartonNo)
        self.SetCartonBtn.grid(column=4,row=0,sticky=Tkinter.W)
        
        #self.PrintBtn = Tkinter.Button(self,text=u"Print",command=self.PrintLabel)
        #self.PrintBtn.grid(column=3,row=1)
        
        self.FetchBtn = Tkinter.Button(self,text=u"Write IMEI",command=self.WriteIMEI)
        self.FetchBtn.grid(column=3,row=2)
        
        self.button = Tkinter.Button(self,text=u"Refresh",command=self.OnButtonClick)
        self.button.grid(column=0,row=0, sticky=Tkinter.W)
        
        self.buttonComport = Tkinter.Button(self,text=u"Connect",command=self.Connect)
        self.buttonComport.grid(column=0,row=0, sticky=Tkinter.E)
        
        """
        Listbox that lists serial comport available 
        """
        self.listBox = Tkinter.Listbox(self,height=3)
        self.listBox.grid(column=0,row=1)
        comports = serial_ports()
        print comports
        for comport in range(len(comports)):
            self.listBox.insert(Tkinter.END,comports[comport])
        
        scrollBar = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL)
        scrollBar.grid(column=1,row=1, sticky=Tkinter.W)
        
        scrollBar.configure(command=self.listBox.yview)
        self.listBox.configure(yscrollcommand=scrollBar.set)
    
    def SetCartonNo(self):
        if self.entry.get():
            self.CartonNo = self.entry.get()
            toplevel = Tkinter.Toplevel()
            label = Tkinter.Label(toplevel, text="OK", height=5, width=20)
            label.pack()
        else:
            toplevel = Tkinter.Toplevel()
            label = Tkinter.Label(toplevel, text="Please Set Carton No",height=5, width=20)
            label.pack()
        
    
    def WriteIMEI(self):
        if not self.atDevice:
            print "Connect device"
            toplevel = Tkinter.Toplevel()
            label = Tkinter.Label(toplevel, text="Connect device!", height=5, width=20)
            label.pack()
        elif not self.CartonNo:
            print "Set Carton No"
            toplevel = Tkinter.Toplevel()
            label = Tkinter.Label(toplevel, text="Set Carton No!", height=5, width=20)
            label.pack()
        elif self.atDevice.Get_IMEI().rstrip() != "000000000000000":
            print "Is not blank"
            toplevel = Tkinter.Toplevel()
            label = Tkinter.Label(toplevel, text="IMEI is not Blank!", height=5, width=20)
            label.pack()
        else:
            #IMEI is blank, proceed to write new IMEI
            #Generate new IMEI
            currentIMEI = self.IMEI.get()
            IMEItoWrite = currentIMEI + GetcheckSum(currentIMEI)
            print "IMEI to write:" + IMEItoWrite
            
            """
            #Write IMEI
            !!!!!!!!!!!!!!!!!!!!
            """
            print self.atDevice.send_cmd("#IMEIW=%s"%IMEItoWrite)
            """
            !!!!!!!!!!!!!!!!!!!!
            """
            self.atDevice.Reboot()
            print "Device is being rebooting"
            self.FetchBtn.config(state='disabled')
            self.after(20000,self.VerifyIMEI,IMEItoWrite) #Device has been restarted

    def VerifyIMEI(self,IMEI):
        self.atDevice.port.close()
        self.atDevice.port.open()
        retrived = self.atDevice.Get_IMEI()
        print retrived
        if retrived.rstrip() == IMEI:
            print "success"
            toplevel = Tkinter.Toplevel()
            label = Tkinter.Label(toplevel, text="OK!", height=5, width=20)
            label.pack()
            
            PrintBtn = Tkinter.Button(toplevel,text=u"Print label",command= lambda: self.PrintLabel(IMEI))
            PrintBtn.pack()

            self.IncrementIMEI()
            
            self.FetchData()
        else:
            print "unsuccess"
            toplevel = Tkinter.Toplevel()
            label = Tkinter.Label(toplevel, text="IMEI written unsuccessfully!", height=5, width=20)
            label.pack()
            
            PrintBtn = Tkinter.Button(toplevel,text=u"Print label",command= lambda: self.PrintLabel(IMEI))
            PrintBtn.pack()
            
        self.FetchBtn.config(state='normal')
    
    def IncrementIMEI(self):
            """
            increments IMEI and stores it in nIMEI.bin (is just a .txt file)
            """
            currentIMEI = self.IMEI.get()
            newIMEI = str(int(currentIMEI) + 1)
            self.IMEI.set(newIMEI)
            with open('nIMEI.bin','w+') as file:
                file.write(newIMEI)
    
    def FetchData(self):
        csv_row =[None] * len(csv_header)
        print "Fetching data"
        
        csv_row[0] = "PlaceHolder"
        csv_row[1] = GetTimestamp()
        csv_row[2] = "2GIG-3GTC90-A"
        csv_row[3] = self.atDevice.Get_IMEI()
        csv_row[4] = self.atDevice.Get_IMSI()
        csv_row[5] = self.atDevice.Get_SWVersion()
        csv_row[6] = "NA"
        csv_row[7] = self.atDevice.Get_ICCID()
        csv_row[8] = self.atDevice.Get_ModuleSN()
        csv_row[9] = "PlaceHolder"
        csv_row[10] = "NA"
        csv_row[11] = "PlaceHolder"
        csv_row[12] = "BFT_autolink"
        csv_row[13] = "NA"
        csv_row[14] = "NA"
        csv_row[15] = "Passed"
        csv_row[16] = self.CartonNo

        with open(self.csv_file,'a+b') as file:
            wr = csv.writer(file,quoting=csv.QUOTE_NONE)
            wr.writerow(csv_row)
        
    def PrintLabel(self, labelNo ):
        from zebra import zebra
        Label = IMEI % (labelNo,labelNo)
        z = zebra()
        printers = z.getqueues()
        print printers
        z.setqueue(printers[0])
        print "Printing label: \n" + Label
        z.output(Label)
        
    def OnButtonClick(self):
        #Refreshing comport list
        self.listBox.delete(0, self.listBox.size())
        comports = serial_ports()
        print comports
        for comport in range(len(comports)):
            self.listBox.insert(Tkinter.END,comports[comport])
    
    def Connect(self):
        index = self.listBox.curselection()
        if index:
            comport = self.listBox.get(index)
            print "Connecting: " + comport
            try:
                self.atDevice = AT.ATDevice(comport)
            except:
                print "Device taken"
                toplevel = Tkinter.Toplevel()
                label = Tkinter.Label(toplevel, text="Device is busy!", height=5, width=20)
                label.pack()
        else:
            print "No comport selected"
        
# Define a function for the thread
def print_time( threadName, delay):
   count = 0
   while count < 5:
      time.sleep(delay)
      count += 1
      print "%s" % (GetTimestamp())
      
def GetTimestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    
if __name__ == "__main__":

    """
    try:
        thread = threading.Thread(target=print_time,args=("Thread",1))
        thread.daemon = True
        thread.start()
    except:
        print "Error: unable to start thread"
    """
    
    app = simpleapp_tk(None)
    app.title('my application')
    app.mainloop()
    
    