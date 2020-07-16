import thriftpy
from tkinter import *
from tkinter.ttk import Combobox
import networkx as nx
import matplotlib.pyplot as plt
from grave import plot_network
from grave.style import use_attributes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.image as mpimg
import numpy as np
from Participant import Participant
import participants
import argparse
#import threading
import Thread

messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
ParticipantID = messages_thrift.ParticipantID


class ParticiantInterface:

    def __init__(self, root, participant, coordinator, failOptions):
        self.root = root
        root.title('2PC protocol')
        self.failOptions = failOptions
        self.participantID = particant
        self.coordinatorID = coordinator
        self.participant = Participant(self.participantID, self.coordinatorID)

    def addElements(self):
        frame = LabelFrame(self.root, text='Coordinator config')
        frame.grid(row = 0, column = 0, padx=10, pady=5)

        fail_coordinator = StringVar(frame)
        fail_coordinator.set(self.failOptions[0]) 
        fail_coordinator_value = self.failOptions[0]

        Label(frame, text='Fail participant time:', padx = 5).grid(row=0, column=0)

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

        b1 = Button(frame, text = 'Apply')
        b1.grid(row = 2, column = 1, pady = 5, padx = 5, sticky='nsew')


        Button(frame, text = 'Run ' + self.participantID.name, command = self.startServer).grid(row = 3, column = 1, pady = 5, padx = 5, sticky='nsew')
        Button(frame, text = 'Stop Server', command = self.stopServer).grid(row = 4, column = 1, pady = 5, padx = 5, sticky='nsew')

        text1 = Text(frame, height = 10, width = 40).grid(row  = 5, column = 0, columnspan = 2, padx = 5, pady = 5)
    
    def stopServer(self):
        self.participant.stopServing()
        self.x.terminate()
        print('server stpped')

    def startServer(self):
        self.x = Thread.Thread(target= self.participant.runServer, args=())
        self.x.daemon = True
        self.x.start()
        print('server started')

    def changeTerminationTime(self, value):
        if value == 'NEVER':
            self.participant.option = 4 
        elif value == 'INITIAL':
            self.participant.option = 1
        elif value == 'READY':
            self.participant.option = 2
        elif value == 'COMMIT/ABORT':
            self.participant.option = 3

        print(self.participant.option)

        print('Termination time changed')


parser = argparse.ArgumentParser(description='participant')
parser.add_argument('name',type=str,help='Name')
args = parser.parse_args()

root = Tk()

# args.name = 'server1'

coordinator = participants.getCoordinator()
particant = participants.getParticipant(args.name)

interface = ParticiantInterface(root, particant, coordinator,['NEVER', 'INITIAL', 'READY', 'COMMIT/ABORT'])
interface.addElements()

root.mainloop()