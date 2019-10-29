import socket
import time
import os
import sys
import select
from _thread import *
import tkinter as tk #GUI
from tkinter import ttk, scrolledtext  # Labels

# client model
#=========================

class ftp_client():

    #sock = -1  # socket initialized as no connection
    #print("Enter your command: HELP to see options or QUIT to exit")
    # while True:
    #     cmd = input()  # command to go to the server
    #     potential_socket = readcmd(cmd, sock)  # read command and may return a socket
    #     if (potential_socket != 0):
    #         sock = potential_socket

    def __init__(self):
        #self.port = port
        sock = -1
        #print("Enter your command: HELP to see options or QUIT to exit")
        print("Client started")
        # while True:
        #     cmd = input()  # command to go to the server
        #     potential_socket = readcmd(cmd, sock)  # read command and may return a socket
        #     if (potential_socket != 0):
        #         sock = potential_socket



    def handle_connection(self, cmd):
        self.inputs = cmd.split()  # splits command string into whitespace seperated text
        self.host = self.inputs[1]
        self.port = self.inputs[2]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init socket
        # connect to server
        try:
            sock.connect((self.host, int(self.port)))
            print("Successfully connected")
        except:
            print("Connection Error, are you sure the server is running?")
            sys.exit()

        return sock


    def handle_quit(self, sock, cmd):
        sock.sendall(cmd.encode("UTF-8"))  # send quit to server
        time.sleep(1)  # added because close operation timing issues
        sock.close()  # close socket
        print("Connection terminated\n")


    def handle_store(self, sock, cmd):
        sock.sendall(cmd.encode("UTF-8"))  # send store to server
        file = cmd[6:]

        # Size of data to send
        chunk_size = 1024
        # try to open the file
        try:
            rfile = open(file, 'rb')  # open file passed
        except:
            print("File Not Found")
            return

        # Get file size and send it to the server
        filesize = os.path.getsize(rfile.name)
        print('File size is: ', filesize)
        sock.send(bytes(str(filesize).encode()))
        time.sleep(1)  # Added for thread timing

        # If file size is less than or equal to chunk_size we have all the data
        if int(filesize) <= chunk_size:
            s = rfile.read(chunk_size)
            sock.send(s)
            rfile.close()
            print('Successfully sent file')
            return

        # File is larger than chunk_size
        s = rfile.read(chunk_size)

        # While there is data to read in the file
        while s:
            sock.send(s)  # send initial read
            print(s.decode())  # confirm data print to screen
            s = rfile.read(chunk_size)  # continue to read
        rfile.close()
        print('Successfully sent file from client')


    def handle_retrieve(self, sock, cmd):
        chunk_size = 1024  # arbitrary chunk size but needs to be sufficient for data transfers
        rfile = cmd[9:]  # parse file name
        sock.sendall(cmd.encode('UTF-8'))  # send file request to server
        filesize = sock.recv(16)  # represents the size of file requested

        print('File size received is: ', filesize.decode())
        f = open('copy2-' + rfile, 'w')  # Added to use file in same dir then run diff

        if filesize <= bytes(chunk_size):
            data = sock.recv(chunk_size)
            f.write(data.decode())
            f.flush()
            f.close()
            return

        while True:
            data = sock.recv(chunk_size)
            if not data: break
            # print('data=%s', (data.decode()))
            f.write(data.decode())
            f.flush()

            # Indicates last of data was received
            if len(data) < chunk_size:
                f.close()
                break

        f.close()
        print('Successfully received the file')


    def handle_help(self):
        print(
            "connect address port: to connect to server\nquit: to quit\nretrieve: to retrieve files\nstore: to store files to server\nlist: to list the files on server\n")


    def readcmd(self, rcmd, sock):
        cmd = rcmd.lower()  # .upper()

        # handle connection
        if 'connect' in cmd:
            if sock != -1:
                print('Must be disconnected to connect to a server')
            else:
                return self.handle_connection(cmd)  # returns socket to main

        # handle help
        elif 'help' in cmd:
            self.handle_help()
            return 0

        # handle exit
        elif 'exit' in cmd:
            if sock != -1:
                print('Must be disconnected before exiting program')
            else:
                print('Exiting...')
                exit()

        # handle quit
        elif 'quit' in cmd:
            # check that socket has been initialized
            if sock == -1:
                print('Must connect to server before issuing commands')
                print('Enter the help command for more details')
            else:
                self.handle_quit(sock, cmd)
                return -1
            return 0

        # handle retrieve
        elif 'retrieve' in cmd:
            # check that socket has been initialized
            if sock == -1:
                print('Must connect to server before issuing commands')
                print('Enter the help command for more details')
            else:
                self.handle_retrieve(sock, cmd)
            return 0

        elif 'store' in cmd:
            # check that socket has been initialized
            if sock == -1:
                print('Must connect to server before issuing commands')
                print('Enter the help command for more details')
            else:
                self.handle_store(sock, cmd)
            return 0

        # handle list
        if 'list' in cmd:
            # check that socket has been initialized
            if sock == -1:
                print('Must connect to server before issuing commands')
                print('Enter the help command for more details')
            else:
                sock.sendall(cmd.encode("UTF-8"))
                data = sock.recv(1024).strip()
                print(data.decode())
            return 0

        else:
            print("Invalid command")

        return 0
#server model
#====================================
class ftp_server:
    # s =  #-1
    # host = -1
    # port = -1
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket

    def __init__(self, port):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket
        port = 8800

        try:
            s.bind(("localhost", int(port)))
            print("Starting up at: %s port %s ", s)
        except socket.error:
            print("Binding failed")
            sys.exit()
        print("socket bound")  # Status update

        s.listen()
        print("listening")  # Status update

    def store(file, conn):
        chunk_size = 1024  # arbitrary chunk size but needs to be sufficient for data transfers
        rfile = file  # parse file name
        filesize = conn.recv(16)  # represents the size of file requested

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

    def retrieve(file, conn):
        # Size of data to send
        chunk_size = 1024
        # try to open the file
        try:
            rfile = open(file, 'rb')  # open file passed

        except:
            print("File Not Found")

        # Get file size and send it to the client
        filesize = os.path.getsize(file)
        print('File size is: ', filesize)
        conn.send(bytes(str(filesize).encode()))
        time.sleep(1)  # Added for thread timing

        # If file size is less than or equal to chunk_size we have all the data
        if int(filesize) <= chunk_size:
            s = rfile.read(chunk_size)
            conn.send(s)
            rfile.close()
            print('Successfully sent file')
            return

        # File is larger than chunk_size
        s = rfile.read(chunk_size)

        # While there is data to read in the file
        while s:
            conn.send(s)  # send initial read
            print(s.decode())  # confirm data print to screen
            s = rfile.read(chunk_size)  # continue to read
        rfile.close()
        print('Successfully sent file')

    # Function to handle all client connections and their respective commands
    def clientthread(conn, addr):
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
                #retrieve(rfile, conn)

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
                #store(sfile, conn)

            # QUIT function
            if 'quit' in rdata:
                # print close mesaage
                print("Connection with " + addr[0] + ":" + str(addr[1]) + " closed")
                conn.close()
                break
            # End RETRIEVE function



        # driver loop
    # while 1:
    #     try:
    #         conn, addr = s.accept()  # continuously accept client connections
    #         # Print IP address and port# of connected client
    #         print("Connected with " + addr[0] + ":" + str(addr[1]))
    #         # Start new thread for client each connection
    #         start_new_thread(clientthread, (conn, addr,))  # ,s
    #     except socket.error:
    #         continue
    #     except KeyboardInterrupt:
    #         print("\nQuiting server...")
    #         break
    #     s.close()  # Close socket



#View
#====================================

class View:

    def __init__(self, master, control): #, client, server, controller):
        #self.win = tk.Tk().frame(master)
        self.win = master
        self.win.title("GV-NAP")

        self.createframe()
        # self.client = client
        # self.server = server
        self.controller = control

        #self.win.mainloop()


    # def view(self, client, server, controller):
    #     self.client = client
    #     self.server = server
    #     self.controller = controller

    def createframe(self):
        # self.win = tk.Tk()  # .frame(master)
        # self.win.title("GV-NAP")

        self.cLabelFrame = ttk.LabelFrame(self.win, text="Connection")
        self.cLabelFrame.grid(column=0, row=0, padx=5, pady=10, sticky="W")

        self.sLabelFrame = ttk.LabelFrame(self.win, text="Search")
        self.sLabelFrame.grid(column=0, row=8, pady=10, sticky='W')

        self.fLabelFrame = ttk.LabelFrame(self.win, text="FTP")
        self.fLabelFrame.grid(column=0, row=12, pady=10, sticky='W')

        ttk.Label(self.cLabelFrame, text="Server Hostname:").grid(column=0, row=0)

        # server hostname field
        self.shField = tk.Entry(self.cLabelFrame)
        self.shField.grid(column=1, row=0)

        # port number text field
        self.sField = tk.Entry(self.cLabelFrame)
        self.sField.grid(column=3, row=0)
        #
        #
        self.sPort = ttk.Label(self.cLabelFrame, text="Port:")
        self.sPort.grid(column=2, row=0)

        self.speed_var = tk.StringVar(self.win)
        #
        # #speed label
        self.sLabel = ttk.Label(self.cLabelFrame, text="Speed:")
        self.sLabel.grid(column=4, row=2)
        #
        # #sets default text for combo box
        self.speed_var.set("Ethernet")
        #
        # #speed combo box
        self.dbox = ttk.Combobox(self.cLabelFrame, width=12, textvariable=self.speed_var)
        self.dbox['values'] = ("Ethernet", "DSL", "Modem", "T1", "T2", "T3")
        self.dbox.grid(column=8, row=2)

        # Connect button
        self.connButton = ttk.Button(self.cLabelFrame, text="Connect")  # , command = get_speed())
        self.connButton.config(width=14)
        self.connButton.bind('<Button-1>', self.vconn)  # get_speed)
        self.connButton.grid(column=8, row=0)
        #
        self.uname = ttk.Label(self.cLabelFrame, text="Username:")
        self.uname.grid(column=0, row=2)
        #
        # #username text field
        self.uField = tk.Entry(self.cLabelFrame)
        self.uField.grid(column=1, row=2)
        #
        # hostname label
        self.hostname = ttk.Label(self.cLabelFrame, text="Hostname:")
        self.hostname.grid(column=2, row=2)

        #
        # hostname text field
        self.hField = tk.Entry(self.cLabelFrame)
        self.hField.grid(column=3, row=2)
        #

        #
        # #search section
        # ttk.Label(sLabelFrame, text="Search", relief=tk.SUNKEN).grid(column=0, row=40)
        #
        # #search label
        # ttk.Label(sLabelFrame, text="Keyword:").grid(column=0, row=0, sticky= "W")

        self.searchLabel = ttk.Label(self.sLabelFrame, text="Keyword:")
        self.searchLabel.grid(column=0, row=0, sticky='W')
        #
        # #search field
        self.searchField = tk.Entry(self.sLabelFrame)
        self.searchField.grid(column=1, row=0)
        #
        # #search button
        self.sButton = ttk.Button(self.sLabelFrame, text="search")
        self.sButton.grid(column=4, row=0)
        #
        # #FTP section
        # ttk.Label(win, text="FTP", relief=tk.SUNKEN).grid(column=0, row=80)
        #
        # #command label
        self.cmdLabel = ttk.Label(self.fLabelFrame, text="Enter Command:")
        self.cmdLabel.grid(column=0, row=0, sticky="W")
        #
        # #command field
        self.cmdField = tk.Entry(self.fLabelFrame)
        self.cmdField.grid(column=1, row=0, sticky="W")
        #
        # #Go button
        self.sButton = ttk.Button(self.fLabelFrame, text="Go")
        self.sButton.config(width=14)
        self.sButton.bind('<Button-1>', self.sendCmd)  # get_speed)
        self.sButton.grid(column=4, row=0)

        # Text area
        self.text = scrolledtext.ScrolledText(self.fLabelFrame, width=40, height=6)
        self.text.grid(column=0, row=3)

        #self.win.mainloop()


    def get_server_hostname(self):
        print("Server Hostname is: ", self.shField.get())
        return self.shField.get()

    def get_hostname(self):
        print('Hostname is', self.hField.get())
        return self.hField.get()

    def get_username(self):
        print('Username is', self.uField.get())
        return self.uField.get()

    def get_port(self):
        print('Port is: ', self.sField.get())
        return self.sField.get()

    def get_speed(self):
        print('Speed is: ', self.speed_var.get())
        return self.speed_var.get()


    # send cmd from Go button
    def sendCmd(self, value):
        cmd = self.cmdField.get()

        #uses username to remove record from users table
        if 'quit' in cmd:
            cmd += " " + self.get_username()
            self.controller.processCmd(cmd)
            return

        self.controller.processCmd(cmd)
        #sock = self.controller.sock
        #sock.sendall(cmd.encode("UTF-8"))





    # connect to a server
    def vconn(self, value):
        cmd = "connect "
        serverIP = self.get_server_hostname()
        port  = self.get_port()
        cmd += str(serverIP) + " " + str(port) + " "

        uInfo = ""
        uname = self.get_username()
        hname = self.get_hostname()
        speed = self.get_speed()
        uInfo += uname + " " + hname + " " + speed

        cmd += uInfo

        #print("Cmd is: ", cmd)
        print("User info is: ", uInfo)
        #cmd2 = "connect 127.0.0.1 8800"
        #pass data to controller get socket back
        #sock =
        sock = self.controller.connect(cmd)

        #central server check to send user info populating user table
        #connecting to central server should only happen once
        #This sends all info from GUI used in central
        if int(port) == 9000:
            sock.sendall(cmd.encode("UTF-8"))
            time.sleep(1)
            # auto upload of resource files username.txt
            cfile = 'store camaal.txt'
            self.controller.processCmd(cfile)






#controller
#================================
class Controller:
    #_clientModel =""
    #_serverModel =""
   # _view=""

    # def __init__(self, ftp_client, ftp_server):
    #     self._clientModel = ftp_client
    #     self._serverModel = ftp_server

    def __init__(self, frame):
        self.root = frame #tk.Tk()
        self.mc = ftp_client()
        #self.c = Controller()
        self.view = "" #View(self.root)
        #self.view = View(self.root)
        self.setView(View)

        #socket test to quit and remove entry from user table
        self.sock =""
        #self.init_model()


    # def __init__(self):
    #     self.init_model()

    def run(self):
        #self.root.title("Tkinter MVC example")
        self.view.__init__(self.root)
        self.root.mainloop()

    def init_model(self):
        self._clientModel = ftp_client()
        #self._serverModel = ftp_server.ftp_server


    # def controller(ftp_client, ftp_server):
    #     _clientModel = ftp_client
    #     _serverModel = ftp_server

    # process cmd after pressing Go button
    def processCmd(self, cmd):
        print("Go cmd: ", cmd)

        if 'quit' in cmd:
            self.sock.sendall(cmd.encode("UTF-8"))
            return

        self.mc.readcmd(cmd, self.sock)


    #connect to server: connect host port
    def connect(self, cmd):
        #self._clientModel.handle_connection(cmd)
        self.sock = self.mc.handle_connection(cmd)
        return self.sock

    def quit(self, cmd, sock):

        self.sock  = self.mc.readcmd(cmd, sock)

    def setView(self, view):
        self._view = view


if __name__ == '__main__':
    #mc = ftp_client()
    #ms = ftp_server()
    root = tk.Tk()

    c = Controller(root)

    v = View(root, c)

    c.setView(v)
    c.run()
    #v = view()