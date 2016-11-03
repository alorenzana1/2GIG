import sys
import glob
import serial
import Tkinter
import threading
import time
import csv
import os
import time
import datetime
from zebra import zebra

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'libraries'))
    from FlexCheckSum import *
    import AT
except IndexError:
    raise RuntimeError("You must have.. /libraries to run this program!")

Radio_Model_supported = ["2GIG-3GTC90-A", "2GIG-3GTL-A-GC3"]
Radio = Radio_Model_supported[0]

csv_header = ["SNID","TestDataTime","SimType","IMEI","IMSI","RevisionID","ModuleSWPN","ICCID","ModuleSN","SignalLevel1","SignalLevel2","DC-DC","TesterSN","CAL1900M","CAL850M","Result","CartonNo"]



LableTemplate="""
^XA
^LH0,0
^FO50,30^BY2
^BCN,70,N,N,N,N^FD>;%s^FS
^FO45,110^A0,N,25,25^FDIMEI: %s-%s^FS
^FO385,30^BY2
^BCN,70,N,N,N,N^FD>;%s^FS
^FO380,110^A0,N,25,25^FDIMEI: %s-%s^FS
^XZ
"""
'''
label="""
^XA
^LH30,30
^FO50,0^BRN,12,1,2,50^FD%s^FS
^FO0,60^AD^FDIMEI: %s-%s^FS
^FO400,0^BRN,12,1,2,50^FD%s^FS
^FO350,60^AD^FDIMEI: %s-%s^FS
^XZ
"""
labelLarge="""
^XA
^JMA^FS
^LH0,0
^FO8,15^BRN,11,2,2,40^FD%s^FS
^FO50,110^A0,N,25,25^FDIMEI: %s-%s^FS
^FO348,15^BRN,11,2,2,40^FD%s^FS
^FO398,110^A0,N,25,25^FDIMEI: %s-%s^FS
^XZ
"""
'''

def CreateLabel(strValue):
    while len(strValue) < 16:
        strValue = '0' + strValue
    MSS = strValue[2:9] 
    LSS = strValue[10:16]
    return LableTemplate %(strValue,MSS,LSS,strValue,MSS,LSS)

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

    def delete(self):
        self.widget.configure(state="normal")
        self.widget.delete("0.0",'end')
        self.widget.configure(state="disabled")

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

class IMEI_writer(Tkinter.Tk):
    atDevice = None
    CartonNo = None
    csv_file = ""
    ZebraPrinter = None
    bIMEI = None
    RUT = None

    def __init__(self, radio, parent=None):
        Tkinter.Tk.__init__(self,parent)
        self.RUT = radio
        self.initialize()

        """
        Looking for CSV under FTP_file folder, if does not exit that location create it
        and create csv file with header file.
        """
        if not os.path.exists("FTP_file"):
            os.makedirs("FTP_file")

        currentPath = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(currentPath,"FTP_file")
        
        """
        for file in os.listdir(path):
            if file.endswith(".txt"):
                self.csv_file = os.path.join(path,file)
        """

        #creating csv file if does not exist
        if(self.csv_file == ""):
            file_name = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
            file_name = self.RUT+"_"+file_name+".txt"
            self.csv_file = os.path.join(path,file_name)
            with open(self.csv_file,'a+b') as file:
                wr = csv.writer(file,quoting=csv.QUOTE_NONE)
                wr.writerow(csv_header)

        try:
            open(self.csv_file,'a+b')
        except IOError:
            self.logger.warn("Could not open file! please close excel!")

    def initialize(self):

        log_frame = Tkinter.Frame(self)
        interface_frame = Tkinter.Frame(self)
        printers_frame = Tkinter.Frame(self)

        log_frame.pack(side="right", fill="both", expand=True)
        interface_frame.pack(side="left", fill="x")
        printers_frame.pack(side="right", fill ="x")

        comport_frame = Tkinter.Frame(interface_frame)
        center_frame = Tkinter.Frame(interface_frame)

        comport_frame.pack(side="top",)
        center_frame.pack(side="bottom",fill="y")

        printList_frame = Tkinter.Frame(printers_frame)
        printBtns_frame = Tkinter.Frame(printers_frame)

        printList_frame.pack(side="top")
        printBtns_frame.pack(side="bottom")

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
        self.comport_list = Tkinter.Listbox(list_frame, height=3)
        self.comport_list.pack(side="left", expand=True)
        comports = serial_ports()
        for comport in range(len(comports)):
            self.comport_list.insert(Tkinter.END,comports[comport])
        
        comport_scrollBar = Tkinter.Scrollbar(list_frame, orient=Tkinter.VERTICAL)
        comport_scrollBar.pack(side="right", fill="y", expand=True)
        comport_scrollBar.configure(command=self.comport_list.yview)
        self.comport_list.configure(yscrollcommand=comport_scrollBar.set)

        self.Refresh_Btn = Tkinter.Button(btns_frame,text=u"Refresh",command=self.Refresh_Btn, width=15)
        self.Refresh_Btn.pack()
        
        self.Connect_Btn = Tkinter.Button(btns_frame,text=u"Connect",command=self.Connect, width=15)
        self.Connect_Btn.pack()

        self.Disconnect_Btn = Tkinter.Button(btns_frame,text=u"Disconnect",command=self.Disconect, width=15,state='disable')
        self.Disconnect_Btn.pack()
    
        self.Clear_Btn = Tkinter.Button(btns_frame,text=u"Clear log",command=self.Clear, width=15)
        self.Clear_Btn.pack()

        #Creation of IMEI entry, 
        self.CartonNo_label = Tkinter.Label(center_frame,text="Carton No.")
        self.CartonNo_label.pack()
        self.entry = Tkinter.Entry(center_frame)
        self.entry.pack()

        self.SetCarton_Btn = Tkinter.Button(center_frame,text=u"Set Carton No", command = self.SetCartonNo, width=15)
        self.SetCarton_Btn.pack()

        if self.RUT == Radio_Model_supported[0]:
            self.bIMEI = "nIMEI_"+Radio_Model_supported[0]+".bin"
        if self.RUT == Radio_Model_supported[1]:
            self.bIMEI = "nIMEI_"+Radio_Model_supported[1]+".bin"

        if os.path.isfile(self.bIMEI):
            with open(self.bIMEI,'r') as file:
                imei = file.read()
        else:
            with open(self.bIMEI,'w') as file:
                if self.RUT == Radio_Model_supported[0]:
                    imei = "35337208000000"
                if self.RUT == Radio_Model_supported[1]:
                    imei = "00000000000000"
                file.write(imei)

        self.IMEI_label = Tkinter.Label(center_frame,text="IMEI")
        self.IMEI_label.pack()

        self.IMEI = Tkinter.StringVar()
        self.IMEI.set(imei)
        self.IMEIentry = Tkinter.Entry(center_frame,textvariable=self.IMEI)
        self.IMEIentry.pack()
    
        self.FetchBtn = Tkinter.Button(center_frame,text=u"Write IMEI",command=self.WriteIMEI, width=15)
        self.FetchBtn.pack()

        self.ReadBtn = Tkinter.Button(center_frame,text=u"Read IMEI",command=self.ReadIMEI, width=15)
        self.ReadBtn.pack()
        
        #Listbox that lists printers available 
        
        self.printers_list = Tkinter.Listbox(printList_frame, width=30)
        self.printers_list.pack(side="left", expand=True)
        z = zebra()
        printers = z.getqueues()
        del z
        for port in range(len(printers)):
            self.printers_list.insert(Tkinter.END,printers[port])
        
        printers_scrollBar = Tkinter.Scrollbar(printList_frame, orient=Tkinter.VERTICAL)
        printers_scrollBar.pack(side="right", fill="y", expand=True)
        printers_scrollBar.configure(command=self.printers_list.yview)
        self.printers_list.configure(yscrollcommand=printers_scrollBar.set)

        self.printerRefresh_btn = Tkinter.Button(printBtns_frame,text=u"Refresh",command=self.printerRefresh_cb,width=15)
        self.printerRefresh_btn.pack()

        self.printerConnect_btn = Tkinter.Button(printBtns_frame,text=u"Connect printer",command=self.printerConnect_cb, width =15)
        self.printerConnect_btn.pack()
        
        self.printerDisconnect_btn = Tkinter.Button(printBtns_frame,text=u"Disconnect printer",command=self.printerDisconnect_cb,state="disable", width =15)
        self.printerDisconnect_btn.pack()

        self.printerTest_btn = Tkinter.Button(printBtns_frame,text=u"Test printer",command=self.TestPrinter, width =15)
        self.printerTest_btn.pack()

        self.PrintBtn = Tkinter.Button(printBtns_frame,text=u"Print",command= lambda: self.PrintLabel(self.IMEI.get()), width=15)
        self.PrintBtn.pack()

        self.logger.info(self.RUT)
        self.logger.info( "IMEI to be written: " + imei)

    def SetCartonNo(self):
        if self.entry.get():
            self.CartonNo = self.entry.get()
            self.logger.info( "OK" )
        else:
            self.logger.info("Please Set Carton No")

    def ReadIMEI(self):
        if not self.atDevice:
            self.logger.warn("Device not connected")
        else:
            self.logger.info(self.atDevice.Get_IMEI())

    
    def WriteIMEI(self):
        try:
            open(self.csv_file,'a+b')
        except IOError:
            self.logger.warn("Could not open file! please close excel!")
        else:
            if not self.atDevice:
                self.logger.warn( "Connect device")

            elif not self.CartonNo:
                self.logger.warn( "Set Carton No")

            elif self.atDevice.Get_IMEI().rstrip() != "000000000000000":
                self.logger.warn( "Is not blank")

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
            with open(self.bIMEI,'w+') as file:
                file.write(newIMEI)
    
    def FetchData(self):
        csv_column =[None] * len(csv_header)
        self.logger.info( "Fetching data" )

        csv_column[0] = "PlaceHolder"                      # SNID
        csv_column[1] = GetTimestamp()                     # TestDataTime

        if self.RUT == Radio_Model_supported[0]:
            csv_column[2] = Radio_Model_supported[0]       # SimType

        if self.RUT == Radio_Model_supported[1]:
            csv_column[2] = Radio_Model_supported[1]       # SimType

        csv_column[3] = self.atDevice.Get_IMEI()           # IMEI
        csv_column[4] = self.atDevice.Get_IMSI()           # IMSI
        csv_column[5] = self.atDevice.Get_SWVersion()      # RevisionID
        csv_column[6] = "NA"                               # ModuleSWPN
        csv_column[7] = self.atDevice.Get_ICCID()          # ICCID
        csv_column[8] = self.atDevice.Get_CGSSN()          # ModuleSN
        csv_column[9] = "PlaceHolder"                      # SignalLevel1
        csv_column[10] = "NA"                              # SignalLevel2
        csv_column[11] = "PlaceHolder"                     # DC-DC
        csv_column[12] = "BFT_autolink"                    # TesterSN
        csv_column[13] = "NA"                              # CAL1900M
        csv_column[14] = "NA"                              # CAL850M
        csv_column[15] = "Passed"                          # Result
        csv_column[16] = self.CartonNo                     # CartonNo

        with open(self.csv_file,'a+b') as file:
            wr = csv.writer(file,quoting=csv.QUOTE_NONE)
            wr.writerow(csv_column)

        self.PrintLabel(self.atDevice.Get_IMEI())
        
    def PrintLabel(self, labelNo ):
        try:
            self.ZebraPrinter.output(CreateLabel(labelNo))
        except Exception as e:
            self.logger.warn( "Error while printing label")
        else:
            self.logger.info( "Printing label")
        
    def Refresh_Btn(self):
        #Refreshing comport list
        self.comport_list.delete(0, self.comport_list.size())
        comports = serial_ports()
        for comport in range(len(comports)):
            self.comport_list.insert(Tkinter.END,comports[comport])
    
    def Connect(self):
        index = self.comport_list.curselection()
        if index:
            comport = self.comport_list.get(index)
            self.logger.info( "Connecting: " + comport )
            try:
                self.atDevice = AT.ATDevice(comport)
            except:
                self.logger.warn( "Device taken" )
            else:
                self.logger.info( "Comport opened" )
                self.Disconnect_Btn.config(state="normal")
                self.Connect_Btn.config(state="disable")
        else:
            self.logger.warn( "Wrong COM port selected" )

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

    def Clear(self):
        self.logger.delete()

    def printerRefresh_cb(self):
        self.printers_list.delete(0, self.printers_list.size())
        z = zebra()
        printers = z.getqueues()
        del z
        for port in range(len(printers)):
            self.printers_list.insert(Tkinter.END,printers[port])

    def printerConnect_cb(self):
        index = self.printers_list.curselection()
        if index:
            printer = self.printers_list.get(index)
            self.logger.info( "Connecting: " + printer )
            try:
                self.ZebraPrinter = zebra()
            except:
                self.logger.warn( "Error has occurred" )
            else:             
                self.ZebraPrinter.setqueue(printer)
                self.printerConnect_btn.config(state="disable")
                self.printerDisconnect_btn.config(state="normal")
        else:
            self.logger.warn( "Wrong printer selected" )
        
    def printerDisconnect_cb(self):
        self.ZebraPrinter = None
        self.printerConnect_btn.config(state="normal")
        self.printerDisconnect_btn.config(state="disable")

    def TestPrinter(self):
        index = self.printers_list.curselection()
        if index:
            printer = self.printers_list.get(index)
            self.logger.info( "Connecting: " + printer )
            try:
                from zebra import zebra
                z = zebra()
                z.setqueue(printer)
            except:
                self.logger.warn( "Error has occurred" )
            else:             
                self.logger.info( "Printing label test: Hello World")
                z.output(CreateLabel("0"))
        else:
            self.logger.warn( "Wrong printer selected" )

def GetTimestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    
if __name__ == "__main__":


    app = IMEI_writer( Radio, None)
    if Radio == Radio_Model_supported[0]:
        app.title('IMEI writer  '+Radio_Model_supported[0])
    if Radio == Radio_Model_supported[1]:
        app.title('IMEI writer  '+Radio_Model_supported[1])
    app.mainloop()
