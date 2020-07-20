from tkinter import *
import threading
import thriftpy
from Network import Network
from Coordinator import Coordinator
from tkinter.ttk import Combobox
import threading
import participants
import Thread


messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
from messages_thrift import ParticipantID

class CoordinatorInterface:

    def __init__(self, root, failOptions):
        super().__init__()
        self.failOptions = failOptions
        self.root = root
        self.coordinator = Coordinator(participants.getCoordinator())
        self.coordinator.participants = participants.getAllParticipants()
        self.coordinator.recover()
               
        root.title('Client interface')

        self.addElements()

        root.mainloop()

    def addElements(self):
        frame = LabelFrame(self.root, text='Coordinator config')
        frame.grid(row = 0, column = 0, padx=10, pady=5)

        fail_coordinator = StringVar(frame)
        fail_coordinator.set(self.failOptions[0]) 
        fail_coordinator_value = self.failOptions[0]

        Label(frame, text='Fail coordinator time:', padx = 5).grid(row=0, column=0)

        def selected_coordinator_fail(event):
            self.changeTerminationTime(fail_dropdown.get())

        fail_dropdown = Combobox(frame, state="readonly", values = self.failOptions, width = 17)
        fail_dropdown.current(0)
        fail_dropdown.bind("<<ComboboxSelected>>", selected_coordinator_fail)
        fail_dropdown.grid(row=0, column = 1, pady = 5, padx = 5)

        Label(frame, text='Vote:', padx = 5).grid(row=1, column=0,sticky='w', padx = 5)

        v_coordinator = StringVar()
        v_coordinator.set("COMMIT") # initialize

        commit = Radiobutton(frame, text="COMMIT", variable=v_coordinator, value='COMMIT').grid(row = 1, column = 1, sticky = 'e')
        commit = Radiobutton(frame, text="ABORT", variable=v_coordinator, value='ABORT').grid(row = 1, column = 1, sticky = 'w')

        b1 =  Button(frame, text = 'Run Transaction', command = self.coordinator.write)
        b1.grid(row = 2, column = 1, pady = 5, padx = 5, sticky='nsew')


        Button(frame, text = 'Run ' + self.coordinator.coordinator.name, command = self.startServer).grid(row = 3, column = 1, pady = 5, padx = 5, sticky='nsew')
        #Button(frame, text = 'Stop Server', command = self.stopServer).grid(row = 4, column = 1, pady = 5, padx = 5, sticky='nsew')

        text1 = Text(frame, height = 10, width = 40).grid(row  = 5, column = 0, columnspan = 2, padx = 5, pady = 5)
    
    def changeTerminationTime(self, value):
        if value == 'NEVER':
            self.coordinator.option = 4 
        elif value == 'INITIAL':
            self.coordinator.option = 1
        elif value == 'READY':
            self.coordinator.option = 2
        elif value == 'COMMIT/ABORT':
            self.coordinator.option = 3

        print(self.coordinator.option)

        print('Termination time changed')

    def __readParticipants(self):
        self.all_participants = participants.getAllParticipants()
        self.coordinator = participants.getCoordinator()

    def startServer(self):
        self.x = Thread.Thread(target= self.coordinator.runServer, args=())
        self.x.daemon = True
        self.x.start()
        print('server started')

if __name__ == '__main__':
    root = Tk()
    CoordinatorInterface(root, ['NEVER', 'INITIAL', 'READY', 'COMMIT/ABORT'])
    

