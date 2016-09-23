from subprocess import Popen, PIPE
from time import sleep
from nbstreamreader import NonBlockingStreamReader as NBSR
import sys


nbsr = NBSR(sys.stdin)
# issue command:
#p.stdin.write('command\n')
# get the output
while True:
    output = nbsr.readline(0.1)
    # 0.1 secs to let the shell output the result
    if output:
        #print '[No more data]'
        #break
        print output