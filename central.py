
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

    def addFiles(self, username, port, speed ):
        #filename = "copy of " + username + ".txt"
        val = {}
        print("USER: {} ".format(username))
        f = open("{}.txt".format(username), "r")
        data = f.readlines()

        files = {}
        value = {}
        info = ''

        for line in data:
            info = line
        print(info)
        f.close()


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

    def send_retrieve_data(self, conn, addr, rfile, ruser):
        return 0

    # # Function to handle all client connections and their respective commands
    def clientthread(self, conn, addr):
        uinfo = []
        while True:
            print(addr)
            data = conn.recv(1024)
            reply = "ACK " + data.decode()
            rdata = data.decode()
            rdata = rdata.lower()
            print(rdata)
            if not data:
                break

            # Retrieve function
            if 'retrieve' in rdata:
                params = rdata.split(' ')
                rfile = params[1]
                ruser = params[2]
                target = rfile + ":" + self.users[ruser]["listening_addr"] + ":" + str(self.users[ruser]["listening_port"])
                target = target.encode()
                while(target):
                    conn.send(target)
                    if len(target) < 1024:
                        break
                print("sent target listening address and port")
                # retrieve(rfile, conn)

            # List function
            if 'list' in rdata:
                results = os.popen('ls').read().encode()  # socket sends bytes needs to be encoded
                while (results):
                    conn.send(results)  # send initial read
                    if len(results) < 1024:
                        break
            
            # handle key word searching
            if 'search' in rdata:
                terms = rdata.split(':')
                keyword = terms[1].strip()
                results = ""

                for user in self.fileslist:
                    for item in self.fileslist[user]:
                        print(item)
                        if keyword not in item:
                            continue
                        else:
                            results += ":{}|{}".format(item, user)

                if results == "":
                    results = "File not found"
                results = bytes(results.encode())
                while(results):
                    conn.send(results)
                    if (len(results) < 1024):
                        break

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
                else:
                    while True:
                        data = conn.recv(chunk_size)
                        if not data: break
                        f.write(data.decode())
                        f.flush() # Indicates last of data was received
                        if len(data) < chunk_size:
                            break
                f.close()
                print("HIT")
                
                # Parse file data to append data to filetables
                f = open(rfile, 'r')
                #filelist_to_add = {u}
                metadata = {'userinfo': [uinfo[3], uinfo[4], uinfo[5]]}
                for line in f:
                    line = line.split(':')
                    metadata[line[0].strip()] = line[1].strip()
                self.fileslist[uinfo[3]] = metadata
                print(self.fileslist)

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

                # print close mesaage
                print("Connection with " + addr[0] + ":" + str(addr[1]) + " closed")

                conn.close()
                return

            # connect
            if 'connect' in rdata:
                uinfo = rdata.split() #should be all the data from the connect
                print("\nUser {} has joined".format(uinfo[3]))

                #adding record to the user table
                self.users[uinfo[3]] = {'address': uinfo[1], 'port': uinfo[2], 'hostname':uinfo[4], 'speed': uinfo[5], "listening_addr": uinfo[6], "listening_port": uinfo[7]}

                #confirm entries
                print("User info is: ", uinfo)
                print("Users table is: ", self.users)

            # End RETRIEVE function



if __name__ == '__main__':

    print("To begin listening, enter: connect address port")
    s = -1
    
    # get ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create socket
    s.connect(("8.8.8.8", 80))
    host = s.getsockname()[0]
    port = 9000
    print(host)
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
            #hostname = socket.gethostname() #get hostname
            print("CONNECTED")
            print(addr)
            print(conn)
            print("Connected with " + addr[0] + ":" + str(addr[1]))
            #print("Your Computer Name is:" + hostname)

            # Start new thread for client each connection
            #passed an empty tuple to start_new_thread based on error below
            #TypeError: start_new_thread expected at least 2 arguments, got 1
            #start_new_thread(cServer.clientthread(conn, addr,), ()) #, (conn, addr,))  # ,s
            start_new_thread(cServer.clientthread, (conn, addr ))  # , (conn, addr,))  # ,s
        except socket.error:
            continue
        except KeyboardInterrupt:
            print("\nQuiting server...")
            s.close()
 # Close socket
#self.users[camaal] [0] =