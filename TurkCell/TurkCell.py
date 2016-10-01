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
        self.widget.yview(Tkinter.END)

    def info(self, msg):
        self.write(msg,"info")

    def warn(self, msg):
        self.write(msg,"warn")

    def error(self, msg):
        self.write(msg,"error")

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
    def __init__(self,parent=None):
        Tkinter.Tk.__init__(self,parent)
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

        log_frame = Tkinter.Frame(self)
        interface_frame = Tkinter.Frame(self)

        log_frame.pack(side="right", fill="both", expand=True)
        interface_frame.pack(side="left", fill="x")

        comport_frame = Tkinter.Frame(interface_frame)
        center_frame = Tkinter.Frame(interface_frame)
        
        comport_frame.pack(side="top",)
        center_frame.pack(side="bottom",fill="y")

        #Logger
        import ScrolledText
        terminal = ScrolledText.ScrolledText(log_frame, state='disabled', height = 1)
        terminal.pack(side="left", fill="both", expand=True)
        # Create textLogger
        self.logger = TextRedirector(terminal)


        #Comport Interface
        list_frame = Tkinter.Frame(comport_frame)
        btns_frame = Tkinter.Frame(comport_frame)

        list_frame.pack(side="top", fill="both", expand=True)
        btns_frame.pack(side="bottom")

        #Listbox that lists serial comport available 
        self.listBox = Tkinter.Listbox(list_frame)
        self.listBox.pack(side="left", expand=True)
        comports = serial_ports()
        for comport in range(len(comports)):
            self.listBox.insert(Tkinter.END,comports[comport])
        
        scrollBar = Tkinter.Scrollbar(list_frame, orient=Tkinter.VERTICAL)
        scrollBar.pack(side="right", fill="y", expand=True)
        scrollBar.configure(command=self.listBox.yview)
        self.listBox.configure(yscrollcommand=scrollBar.set)

        self.Refresh_Btn = Tkinter.Button(btns_frame,text=u"Refresh",command=self.OnButtonClick, width=15)
        self.Refresh_Btn.pack()
        
        self.Connect_Btn = Tkinter.Button(btns_frame,text=u"Connect",command=self.Connect, width=15)
        self.Connect_Btn.pack()

        self.Disconnect_Btn = Tkinter.Button(btns_frame,text=u"Disconnect",command=self.Disconect, width=15,state='disable')
        self.Disconnect_Btn.pack()
    
        #Creation of IMEI entry, 
        self.CartonNo_label = Tkinter.Label(center_frame,text="Carton No.")
        self.CartonNo_label.pack()
        self.entry = Tkinter.Entry(center_frame)
        self.entry.pack()

        self.SetCarton_Btn = Tkinter.Button(center_frame,text=u"Set Carton No", command = self.SetCartonNo, width=15)
        self.SetCarton_Btn.pack()
        
        if os.path.isfile('nIMEI.bin'):
            with open('nIMEI.bin','r') as file:
                imei = file.read()
        else:
            with open('nIMEI.bin','w') as file:
                imei = "35337208000000"
                file.write(imei)

        self.IMEI_label = Tkinter.Label(center_frame,text="IMEI")
        self.IMEI_label.pack()

        self.IMEI = Tkinter.StringVar()
        self.IMEI.set(imei)
        self.IMEIentry = Tkinter.Entry(center_frame,textvariable=self.IMEI)
        self.IMEIentry.pack()
    
        self.FetchBtn = Tkinter.Button(center_frame,text=u"Write IMEI",command=self.WriteIMEI, width=15)
        self.FetchBtn.pack()

        self.PrintBtn = Tkinter.Button(center_frame,text=u"Print",command= lambda: self.PrintLabel(self.IMEI.get()), width=15)
        self.PrintBtn.pack()
        

        self.logger.info( "IMEI to be written: " + imei)

    def SetCartonNo(self):
        if self.entry.get():
            self.CartonNo = self.entry.get()

            self.logger.info( "OK" )
        else:

            self.logger.info("Please Set Carton No")
    
    def WriteIMEI(self):
        if not self.atDevice:
            self.logger.info( "Connect device")

        elif not self.CartonNo:
            self.logger.info( "Set Carton No")

        elif self.atDevice.Get_IMEI().rstrip() != "000000000000000":
            self.logger.info( "Is not blank")

        else:
            #IMEI is blank, proceed to write new IMEI
            #Generate new IMEI
            currentIMEI = self.IMEI.get()
            IMEItoWrite = currentIMEI + GetcheckSum(currentIMEI)
            self.logger.info( "IMEI to write:" + IMEItoWrite)
            
            """
            #Write IMEI
            !!!!!!!!!!!!!!!!!!!!
            """
            print self.atDevice.send_cmd("#IMEIW=%s"%IMEItoWrite)
            """
            !!!!!!!!!!!!!!!!!!!!
            """
            self.atDevice.Reboot()
            self.logger.info( "Device is being rebooting")
            self.FetchBtn.config(state='disabled')
            self.after(20000,self.VerifyIMEI,IMEItoWrite) #Device has been restarted

    def VerifyIMEI(self,IMEI):
        self.atDevice.port.close()
        self.atDevice.port.open()
        retrived = self.atDevice.Get_IMEI()
        self.logger.info( retrived )
        if retrived.rstrip() == IMEI:
            self.logger.info( "success" )
            self.IncrementIMEI()
            
            self.FetchData()
        else:
            self.logger.info( "unsuccess" )

            
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
        self.logger.info( "Fetching data" )
        
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
        self.logger.info("Printing label: " + labelNo)
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
            self.logger.info( "Connecting: " + comport )
            try:
                self.atDevice = AT.ATDevice(comport)
            except:
                self.logger.info( "Device taken" )
            else:
                self.logger.info( "Comport opened" )
                self.Disconnect_Btn.config(state="normal")
                self.Connect_Btn.config(state="disable")
        else:
            self.logger.info( "No comport selected" )

    def Disconect(self):
        port_to_close = self.atDevice.port
        try:
            port_to_close.close()
        except:
            pass
        else:
            self.atDevice = None
            self.logger.info("Comport %s closed" % port_to_close.portstr)
            self.Disconnect_Btn.config(state="disable")
            self.Connect_Btn.config(state="normal")

def GetTimestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    
if __name__ == "__main__":


    app = simpleapp_tk(None)
    app.title('my application')
    app.mainloop()
    
    