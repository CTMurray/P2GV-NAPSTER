import tkinter as tk #GUI
from tkinter import ttk, scrolledtext  # Labels

class view:


    def __init__(self):

        self.win = tk.Tk()
        self.win.title("GV-NAP")

        #Label Frames for the three section groups:
        #connection, search, FTP

        self.cLabelFrame = ttk.LabelFrame(self.win, text="Connection")
        self.cLabelFrame.grid(column=0, row=0, padx=5, pady=10, sticky="W")

        self.sLabelFrame = ttk.LabelFrame(self.win, text="Search")
        self.sLabelFrame.grid(column=0, row=8, pady=10, sticky='W')

        self.fLabelFrame = ttk.LabelFrame(self.win, text="FTP")
        self.fLabelFrame.grid(column=0, row=12, pady=10, sticky='W')

        ttk.Label(self.cLabelFrame, text="Server Hostname:").grid(column=0, row=0)

        self.hField = tk.Entry(self.cLabelFrame)
        self.hField.grid(column=1, row=0)

        # port number text field
        self.sField = tk.Entry(self.cLabelFrame)
        self.sField.grid(column=3, row=0)

        self.sPort = ttk.Label(self.cLabelFrame, text="Port:")
        self.sPort.grid(column=2, row=0)

        self.speed_var = tk.StringVar(self.win)

        # #speed label
        self.sLabel = ttk.Label(self.cLabelFrame, text="Speed:")
        self.sLabel.grid(column=4, row=2)

        # #sets default text for combo box
        self.speed_var.set("Ethernet")

        # #speed combo box
        self.dbox = ttk.Combobox(self.cLabelFrame, width=12, textvariable=self.speed_var)
        self.dbox['values'] = ("Ethernet", "DSL", "Modem", "T1", "T2", "T3")
        self.dbox.grid(column=8, row=2)

        # Connect button
        self.connButton = ttk.Button(self.cLabelFrame, text="Connect")  # , command = get_speed())
        self.connButton.config(width=14)

        # defines left click on the connect button
        # https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
        self.connButton.bind('<Button-1>', self.conn)  # get_speed)
        self.connButton.grid(column=8, row=0)

        #username label
        self.uname = ttk.Label(self.cLabelFrame, text="Username:")
        self.uname.grid(column=0, row=2)

        #username text field
        self.uField = tk.Entry(self.cLabelFrame)
        self.uField.grid(column=1, row=2)

        #server hostname label
        self.hostname = ttk.Label(self.cLabelFrame, text="Hostname:")
        self.hostname.grid(column=2, row=2)

        # #server hostname text field
        self.hField = tk.Entry(self.cLabelFrame)
        self.hField.grid(column=3, row=2)

        # #search section

        # #search label
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
        self.sButton.grid(column=4, row=0)

        # Text area
        self.text = scrolledtext.ScrolledText(self.fLabelFrame, width=40, height=6)
        self.text.grid(column=0, row=3)

        #loop that runs window
        self.win.mainloop()


    def get_server_hostname(self):
        print("Server Hostname is: ", self.hField.get())
        return self.hField.get()

    def get_hostname(self):
        print('Hostname is', self.hField.get())
        return self.hField.get()

    def get_username(self):
        print('Username is', self.uField.get())
        return self.uField.get()

    def get_port(self):
        print('Port is: ', self.sPort.get())
        return self.sPort.get()

    # test
    def get_speed(self):
        print('Speed is: ', self.speed_var.get())
        return self.speed_var.get()

    # experimenting with connect to a server feature
    def conn(self):
        cmd = "connect "
        serverIP = view.get_server_hostname()
        port  = view.get_port()
        cmd += str(serverIP) + " " + str(port)
        #pass data to controller
        self.controller.connect(cmd)


if __name__ == '__main__':
    view_instance = view()
    #view_instance.mainloop()
