
import json
import socket
import time
import os
import sys
import select
from _thread import *

class central:

    def __init__(self):
        self.users = dict()
        self.fileslist = dict()

    #self.users = dict()
    """
    users = {
    "uname": [speed, hostname] #array rep.
    };
    
    """

    #fileslist = dict()
    """
    files = {
    "filename": [description, remote_hostname, port#, remote_file_name, speed]
    };
    """
    def addFiles(self, username, port, speed ):
        #filename = "copy of " + username + ".txt"
        val = {}

        f = open("copy of {}.txt".format(username), "r")
        data = f.readlines()

        files = {}
        value = {}


        for line in data:
            value  = line.strip().split(" ", 1)
            print("Value is :", value)
            # print("Value 0 is :", value[0])
            # print("Value 1 is :", value[1])

            if value not in ["", ' ', '\n']: # != "" or value != " ":
                #files[username] = {"filename": value[0], "desc": value[1]}
                files = {"filename": value[0], "desc": value[1]}
                print("Files allocated: ", files)

            #val = line.split()
            if not value: #!= "":

                f.close()
                return
                #self.fileslist[username] = {tuple(val), username, port, speed}
                #val[key] = value.strip()


        #print("fileslist: ", self.fileslist)

        f.close()

        # with open("copy of {}.txt ".format(username)) as f:
        #     #(key, val) = [line.rstrip('\n').split(' ', 1) for line in f]
        #     # line = []
        #     # line.append(f.read().split())
        #     # #line.append(f.read().splitlines())
        #     # #values = line.split(' ', 1)
        #     # self.fileslist = {
        #     #     username: {
        #     #         tuple(line[0]), username, port, speed
        #     #     }
        #     #
        #     # }
        #
        #     fileDict = dict()
        #     #fileDict = f.split(' ', 1)
        #
        #     # values = line.strip().split(' ', 1)
        #     # print("Values 0: ", fileDict[0])
        #     # print("Values 1: ", fileDict[1])
        #
        #     self.key = ""
        #     self.val = ""
        #
        #
        #
        #     for line in f:
        #         linfo = line.strip().split(" ", 1)
        #        # (key, val ) = line.strip().split(' ', 1)
        #         self.key = linfo[0]
        #         self.val = linfo[1]
        #
        #         #print("Key is: ", linfo[0])
        #         #print("Value is: ", linfo[1])
        #         #self.fileslist = {key, val }
        #
        #         #fileDict = line.strip().split(' ', 1)
        #         #values = values.remove("")
        #         # print("Values 0: ", fileDict[0] )
        #         # print("Values 1: ", fileDict[1])
        #         #print("Values 2: ", values[2])
        #         # for temp in values:
        #         #     print("Temp is: ", temp)
        #
        #         # self.fileslist = {
        #         #     username: {
        #         #         values[0], values[1], username, port, speed
        #         #     }
        #         #
        #         # }
        #         print("Values 0: ", self.key)
        #         print("Values 1: ", self.val)
        #     #print("Values 0: ", fileDict[0])
        #     #print("Values 1: ", fileDict[1])
        #     print("files are: ", self.fileslist)

    #Get a list of keys from dictionary which has the given value
    def getKeysByValue(self, filelist, valueToFind):
        listOfKeys = list()
        listOfItems = filelist.items()
        for item in listOfItems:
            if item[1] == valueToFind:
                listOfKeys.append(item[0])
        return listOfKeys

    #Get a list of keys from dictionary which has value that matches with any value in given list of values
    def getKeysByValues(self, filelist, listOfValues): #[value1, value2]
        listOfKeys = list()
        listOfItems = filelist.items()
        for item in listOfItems:
            if item[1] in listOfValues:
                listOfKeys.append(item[0])
        return listOfKeys


    def keyword(self, filelist, desc):
        #get a list of keys that match the desc
        listOfKeys = self.getKeysByValue(filelist, desc)

        # if key in filelist:
        #     return

        return listOfKeys

    # # Function to handle all client connections and their respective commands
    def clientthread(self, conn, addr):
        while True:
            # print(conn)
            data = conn.recv(1024)
            reply = "ACK " + data.decode()
            rdata = data.decode()
            rdata = rdata.lower()
            print(rdata)
            if not data:
                break

            # Retrieve function
            if 'retrieve' in rdata:
                rfile = rdata[9:]  # parse file name
                print(rfile)  # confirms file name
                # retrieve(rfile, conn)

            # List function
            if 'list' in rdata:
                results = os.popen('ls').read().encode()  # socket sends bytes needs to be encoded
                while (results):
                    conn.send(results)  # send initial read
                    if len(results) < 1024:
                        break
            # end LIST function

            # store function
            if 'store' in rdata:
                sfile = rdata[6:]  # find file name
                print("reading " + sfile)
                chunk_size = 1024  # arbitrary chunk size but needs to be sufficient for data transfers
                rfile = sfile  # parse file name
                filesize = conn.recv(1024)  # represents the size of file requested

                print('File size received is: ', filesize.decode())
                if (os.path.exists(rfile)):
                    f = open('copy of ' + rfile, 'w')  # Added to use file in same dir then run diff
                else:
                    f = open(rfile, 'w')

                if filesize <= bytes(chunk_size):
                    data = conn.recv(chunk_size)
                    f.write(data.decode())
                    f.flush()
                    f.close()
                    return

                while True:
                    data = conn.recv(chunk_size)
                    if not data: break
                    f.write(data.decode())
                    f.flush()

                    # Indicates last of data was received
                    if len(data) < chunk_size:
                        f.close()
                        break

                f.close()
                print('Successfully received the file')


            # QUIT function
            if 'quit' in rdata:
                # assumption quit username is sent
                qdata = rdata.split()

                if qdata[1] in self.users:
                    print("User {} has left".format(qdata[1]))
                    #remove from users table
                    del self.users[qdata[1]]
                    #printing of data in users
                    #print("Updated Users Table: ", self.users)
                    conn.close()
                    break

                # print close mesaage
                print("Connection with " + addr[0] + ":" + str(addr[1]) + " closed")

                conn.close()
                break

            # connect
            if 'connect' in rdata:
                uinfo = rdata.split() #should be all the data from the connect
                #uinfo[3] = username
                #uinfo[4] = speed
                #unifo[5] = hostname

                # testDict = {}
                # testDict['guest'] = {'hostname': 'aeon/127.0.0.1', 'speed': 't1'}
                # self.users = testDict

                print("\nUser {} has joined".format(uinfo[3]))

                #adding record to the user table
                self.users[uinfo[3]] = {'port': uinfo[2], 'hostname':uinfo[4], 'speed': uinfo[5]}
                #port = 9000

                #self.addFiles(uinfo[3], uinfo[2], uinfo[5])

                #confirm entries
                print("User info is: ", uinfo)
                print("Users table is: ", self.users)

            # End RETRIEVE function



if __name__ == '__main__':

    print("To begin listening, enter: connect address port")
    s = -1
    host = "localhost"
    port = 9000

    cServer = central()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket

    # Attempt to bind socket to IP and port, error otherwise.
    try:
        s.bind((host, int(port)))
    except socket.error:
        print("Binding failed")
        sys.exit()
    print("socket bound")  # Status update

    s.listen()
    print("listening")  # Status update



    # driver loop
    while 1:
        try:
            conn, addr = s.accept()  # continuously accept client connections
            hostname = socket.gethostname() #get hostname

            # Print IP address and port# of connected client
            print("Connected with " + addr[0] + ":" + str(addr[1]))
            print("Your Computer Name is:" + hostname)

            # Start new thread for client each connection
            #passed an empty tuple to start_new_thread based on error below
            #TypeError: start_new_thread expected at least 2 arguments, got 1
            #start_new_thread(cServer.clientthread(conn, addr,), ()) #, (conn, addr,))  # ,s
            start_new_thread(cServer.clientthread, (conn, addr ))  # , (conn, addr,))  # ,s
        except socket.error:
            continue
        except KeyboardInterrupt:
            print("\nQuiting server...")
            break
    s.close()  # Close socket
#self.users[camaal] [0] =