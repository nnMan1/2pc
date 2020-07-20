from tkinter import *
import threading
import thriftpy
from Network import Network
from thriftpy.rpc import make_server
from thriftpy.rpc import client_context
from tkinter.ttk import Combobox
import threading
import participants
import Thread


messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
from messages_thrift import ParticipantID, Coordinator

class CoordinatorInterface:

    def __init__(self, root, coordinator, participants):
        super().__init__()
        self.participants = participants
        self.root = root
        self.coordinator = coordinator
        #self.coordinator.recover()
        self.readServer = self.participants[0].name

        root.title('Client interface')

        self.addElements()

        root.mainloop()

    def addElements(self):
        frame = LabelFrame(self.root, text='Coordinator config')
        frame.grid(row = 0, column = 0, padx=10, pady=5)

        readServer = StringVar(frame)
        readServer.set(self.participants[0].name) 
        fail_coordinator_value = self.participants[0].name

        Label(frame, text='Fail coordinator time:', padx = 5).grid(row=0, column=0)

        def selected_read_server(event):
            self.readServer = fail_dropdown.get()

        fail_dropdown = Combobox(frame, state="readonly", values = [participant.name for participant in self.participants], width = 17)
        fail_dropdown.current(0)
        fail_dropdown.bind("<<ComboboxSelected>>", selected_read_server)
        fail_dropdown.grid(row=0, column = 1, pady = 5, padx = 5)

        Label(frame, text='Vote:', padx = 5).grid(row=1, column=0,sticky='w', padx = 5)

        self.action = StringVar()
        self.action.set("READ") # initialize

        commit = Radiobutton(frame, text="READ", variable=self.action, value='READ').grid(row = 1, column = 1, sticky = 'e')
        commit = Radiobutton(frame, text="WRITE", variable=self.action, value='WRITE').grid(row = 1, column = 1, sticky = 'w')

        # b1 =  Button(frame, text = 'Run', command = self.runAction)
        # b1.grid(row = 2, column = 1, pady = 5, padx = 5, sticky='nsew')

        Label(frame, text="Document name:", padx = 5).grid(row = 3, column = 0, sticky='w', padx = 5)
        self.docName = Entry(frame)
        self.docName.grid(row = 3, column = 1, sticky='nswe', padx = 5, pady = 5)

        Button(frame, text = 'Run ', command = self.runAction).grid(row = 4, column = 1, pady = 5, padx = 5, sticky='nsew')
        
        self.docContent = Text(frame, height = 10, width = 40)
        self.docContent.grid(row  = 5, column = 0, columnspan = 2, padx = 10, pady = 5)
    
    def runAction(self):
        if self.action.get() == 'WRITE':
            try:
                with  client_context(Coordinator, self.coordinator.ip, self.coordinator.port) as client:
                    client.write(self.docName.get(), self.docContent.get("1.0",END))
            except:
                self.docContent.delete(1.0, END)
                self.docContent.insert(INSERT, 'ERROR WRITING CONTENT')
                print('Cant process write query')
        else:
            try:
                with  client_context(Coordinator, self.coordinator.ip, self.coordinator.port) as client:
                    self.docContent.delete(1.0, END)
                    self.docContent.insert(INSERT, client.read(self.docName.get(), self.readServer))
            except:
                self.docContent.delete(1.0, END)
                self.docContent.insert(INSERT, 'ERROR READING CONTENT')
                print('Cant process read query')

    def __readParticipants(self):
        self.all_participants = participants.getAllParticipants()
        self.coordinator = participants.getCoordinator()

if __name__ == '__main__':
    root = Tk()
    CoordinatorInterface(root, participants.getCoordinator(), participants.getAllParticipants())
    

