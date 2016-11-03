from zebra import zebra


#ZPL commands to be sent to your Printer
label="""
^XA
^FO0,0
^BRN,12,1,2,50
^FD035337208000005^FS
^FS
^XZ
"""
x="""
^XA

^LH30,30
^FO50,0^BCN,50,N,N,N^FD035337208000005^FS
^FO0,60^AD^FDIMEI: 03533720-8000005^FS

^FO400,0^BCN,50,N,N,N^FD035337208000005^FS
^FO350,60^AD^FDIMEI: 03533720-8000005^FS

^XZ
"""

label="""
^XA
^LH30,30
^FO50,0^BRN,11,1,2,50^FD%s^FS
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
test="""
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


def CreateLabel(strValue):
	while len(strValue) < 16:
		strValue = '0' + strValue
	MSS = strValue[2:9] 
	LSS = strValue[10:16]
	print strValue
	print MSS
	print LSS
	return test %(strValue,MSS,LSS,strValue,MSS,LSS)








IMEI ="""
N
Q50,0
A0,22,0,1,1,1,N,"%s"
B0,0,0,3,1,2,20,N,"%s"
P1
"""


label2 ="""
N
Q50,0
A0,22,0,1,1,1,N,"IMEI: 01351800-3269814"
B0,0,0,3,1,2,20,N,"01351800-3269814"
P1
"""

label3="""
N
A0,22,0,1,1,1,N,"Code 128 UCC"
B0,0,0,0,1,2,20,N," 01351800-3269814"

A0,72,0,1,1,1,N,"Code 128 A"
B0,52,0,1A,1,2,20,N,"01351800-3269814"

A0,122,0,1,1,1,N,"Code 128 B"
B0,102,0,1B,1,2,20,N,"01351800-3269814"

A0,172,0,1,1,1,N,"Code 128 C"
B0,152,0,1C,1,2,20,N,"01351800-3269814"
P1
"""
Label = IMEI %("Testing","1234" )
z = zebra()
printers = z.getqueues()
print printers
z.setqueue(printers[1])

print "Printing label: \n" + label
z.output(CreateLabel("35337208000005"))
