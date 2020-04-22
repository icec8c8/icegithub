# Using Hexiwear with Python
import sqlite3

#from __future__ import print_function
import pexpect
import time
import sys
import datetime
#获取秒级时间戳与毫秒级时间戳
body_data = 0
DEVICE = "78:a5:04:84:19:97"# device #24
if len(sys.argv) == 2:
  DEVICE = str(sys.argv[1])

child = pexpect.spawn("gatttool -I")# Run gatttool interactively.
print("Connecting to:"),# Connect to the device.
print(DEVICE)
# ---------------------------------------------------------------------
# function to transform hex string like "0a cd" into signed integer
def hexStrToInt(hexstr):
    val = int(hexstr[0:2], 16) + (int(hexstr[3:5], 16) << 8)
    if ((val & 0x8000) == 0x8000):  # treat signed 16bits
        val = -((val ^ 0xffff) + 1)
    return val
# -------------------connect---------------------------------------
def loop_connect():
    NOF_REMAINING_RETRY = 3
    while True:
      try:
        child.sendline("connect {0}".format(DEVICE))
        child.expect("Connection successful", timeout=1)
      except pexpect.TIMEOUT:
        NOF_REMAINING_RETRY = 3
        if (NOF_REMAINING_RETRY>0):
          print ("timeout, retry...")
          continue
        else:
          print ("timeout, giving up.")
          break
      else:
        print("Connected!")
        break

#-----------------SQL-----------------------
def insert_sqllite(temp,body_data,otherStyleTime):
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    # print ("Opened database successfully")
    c.execute("INSERT INTO COMPANY (TEMPORARY,TYPE ,TS) \
           VALUES (?, ?, ?)", (temp, body_data, otherStyleTime))
    conn.commit()
    #print("Records created successfully")
    conn.close()
#--------------------------------------------

# def loop_send():
#     while True:
#       try:
#           child.sendline("char-write-req 36 0200 --listen")
#           child.expect("Characteristic value was written successfully", timeout=5)
#       except pexpect.TIMEOUT:
#           continue
#       else:
#         print("Connected!")
#         break

loop_connect()
# data2 = child.before
# print(data2)
while True:
    try:
        # data2 = child.before
        # print(data2)

        child.sendline("char-write-req 36 0200 --listen")
        index = child.expect(['Characteristic value was written successfully', 'GLib-WARNING','Disconnected', pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            child.expect("Indication   handle = 0x0035 value: ", timeout=1)
            child.expect(" \r\n", timeout=1)
            # get temp
            data = child.before
            temp = float(hexStrToInt(data[3:8])) / 100
            print(temp)
            # /////////////time///////////////////////
            unixTime = int(time.time())
            dateArray = datetime.datetime.utcfromtimestamp(unixTime)
            otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
            print(otherStyleTime)
            # ////////////type/////////////////////
            body = data[-2:]
            if body == b'02':
                print("Forehead")
                body_data = 2
            elif body == b'09':
                print("Ears")
                body_data = 9
            else:
                pass
            insert_sqllite(temp, body_data, otherStyleTime)  # /////////////////SQL Lite////
        elif index == 1:
            print("not connect")
            print("loop1")
            loop_connect()
        elif index == 2:
            print("loop2")
            #child.sendline("char-write-req 36 0200 --listen")
            loop_connect()
        elif index == 3:
            print("loop3")
            loop_connect()
        elif index == 4:
            print("loop4")
            loop_connect()
#        child.expect("Indication   handle = 0x0035 value: ", timeout=3)

    except pexpect.TIMEOUT:
        child.sendline("char-write-req 36 0200 --listen")
        # data2 = child.before
        # print(data2)
        # print("loop4")
        continue
    # else:
    #     print("WTF")

    #     print("no")
    #
    #     continue


