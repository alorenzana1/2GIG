from zebra import zebra
import os

ZebraPrinter = None

IMEI ="""
N
q450
Q80,0
A0,22,0,1,1,1,N,"IMEI: %s"
A235,22,0,1,1,1,N,"IMEI: %s"

B0,0,0,3,1,2,20,N,"%s"
B235,0,0,3,1,2,20,N,"%s"
P1
"""
labelNo = 353372080000051

Label = IMEI % (labelNo,labelNo,labelNo,labelNo)
z = zebra()
printers = z.getqueues()
print printers

for printer in printers:
	if ("Zebra" in printer) or ("zebra" in printer):
		ZebraPrinter = printer

print "Printer to be used:" + ZebraPrinter

z.setqueue(ZebraPrinter)
print "Printing label: \n" + Label
z.output(Label)

os.system("pause")