import sys

"""
Last Check Digit Calculation Method
Sample : 35337208001000+ check digit (14 digits + check digit)

Step 1
Take 1st, 3rd, 5th, 7th, 9th, 11th, 13th digit as one group data, then has below digits
3, 3, 7, 0, 0, 1, 0
Sum: X=3+3+7+0+0+1+0=14

Step 2
2. 1 - Take 2nd, 4th, 6th, 8th, 10th, 12th digit as one group data, then has below digits
5, 3, 2, 8, 0, 0, 0
2.2 - Capture each data to multiply 2, then divide 10, and can get quotient and remainder, then add them for each digit as the other group data
for the digit 5, quotient + remainder is 1
for the digit 8, quotient + remainder is 7
1, 6, 4, 7, 0, 0, 0
2.3 - Sum: Y=1+6+4+7+0+0+0=18

Step 3
Sum Z = X+Y = 14 +18 = 32

Step 4
Sum Z divide 10 and get the remainder 2

Step 5
Use 10 to subtract this remainder 2, then can get D-value 8, which is the last check digit; if the remainder is 0, the last check digit is 0
"""
def GetcheckSum(input):
    #converting string to a list
    input = list(input)
    #Taking odd elemnts
    oddlist  = map(int,input[0::2])
    #Taking even elemnts
    even = map(int,input[1::2])
    
    #Capture each element to multiply 2 and divide 10, then sum quotient + remainder
    evenlist = []
    for index in even:
        evenlist.append(sum(divmod((index*2),10)))
    
    #sum groups
    Step3 = sum([sum(oddlist), sum(evenlist) ])
    #Divide 10 and get remainder
    Step4 = divmod(Step3,10)
    
    #10 - remainder, if is 0 checksum is 0
    if Step4[1] > 0:
        Step5 = 10 - Step4[1]
    else:
        Step5 = 0
    
    return str(Step5)
    
if __name__ == "__main__":
    x = "35337208001000"
    print x
    checksum = GetcheckSum(x)
    print checksum