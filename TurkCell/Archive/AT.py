import serial
import time
import sys

SOF = "AT"
EOF = "\r"

class ATDevice:
    def __init__(self,comport):
        """
        :port Port where the device is attached to
        :raises: Exception Device is Busy or Device not found
        """
        self.port = None
        try:
            self.port = serial.Serial(comport)
            self.port.baudrate = 115200
            self.stopbits = 1
            self.port.timeout = 1
            self.port.bytesize = serial.EIGHTBITS
            self.port.parity = serial.PARITY_NONE
        except serial.SerialException:
            raise Exception("Device is Busy")
            
        if(self.StartCMD()):
            print "starting command line has not been successful"
            return 1
        else:
            print "connected"

    def __del__(self):
        self.port.close()

    def send_cmd(self,cmd, output=True):
        msg_out = SOF + cmd + EOF
        self.port.write(msg_out)
        msg_in = self.port.readline()
        if not msg_out.strip() == msg_in.strip():
            return [1, []]
        if output:
            msg_in = self.port.readline()
            payload = msg_in.strip()
            msg_in = self.port.readline()
        else:
            payload = None
        msg_in = self.port.readline().strip()
        if(msg_in == "OK"):
            return [0,payload]
        else:
            return [1, []]

    def StartCMD(self):
        msg_out = SOF + EOF
        self.port.write(msg_out)
        msg_in = self.port.readline()
        if not msg_out.strip() == msg_in.rstrip():
            return 1
        msg_in = self.port.readline()
        payload = msg_in.strip()
        if payload == "OK":
            return 0
        else:
            return 1
    
    def Reboot(self):
        [status, data] = self.send_cmd("#REBOOT",False)
        if status:
            return "ERROR"
        else:
            return 0

    def Get_CGSSN(self):
        [status, data] = self.send_cmd("#cgssn")
        if status:
            return "ERROR"
        else:
            return data[8:]
    
    def Get_IMEI(self):
        [status, data] = self.send_cmd("#cgsn")
        if status:
            return "ERROR"
        else:
            return data[7:]
        
    def WriteIMEI(self):
        pass
        
    def Get_IMSI(self):
        [status, data] = self.send_cmd("#cimi")
        if status:
            return "ERROR"
        else:
            return data[7:]
    
    def Get_SWVersion(self):
        [status, data] = self.send_cmd("#cgmr")
        if status:
            return "ERROR"
        else:
            return data[7:]
    
    def Get_ICCID(self):
        [status, data] = self.send_cmd("#ccid")
        if status:
            return "ERROR"
        else:
            return data[7:]
            
    def Get_ModuleSN(self):
        [status, data] = self.send_cmd("+gmm")
        if status:
            return "ERROR"
        else:
            return data
    

        
if __name__ == "__main__":

    at = ATDevice("COM4")
    
    print at.send_cmd("#CCID")