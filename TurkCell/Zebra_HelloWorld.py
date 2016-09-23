from zebra import zebra

SN = "01351800-3269814"
#ZPL commands to be sent to your Printer
label="""
^XA
^FO10,10
^A0,40,40
^FD
Hello World
^FS
^XZ
"""

IMEI ="""
N
Q50,0
A0,22,0,1,1,1,N,"%s"
B0,0,0,3,1,2,20,N,"%s"
P1
"""

#os.system('"python -u -c "%s" "' % PowerOn)
#EPL2
#N
#B10,10,0,3,3,7,200,B,"998152-001"
#P1

#D7
#ZB

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
z.setqueue(printers[0])

print "Printing label: \n" + Label
z.output(Label)
