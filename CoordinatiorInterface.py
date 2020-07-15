from tkinter import *
import threading
import thriftpy
from Network import Network
from Coordinator import Coordinator
import threading
import participants

messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
from messages_thrift import ParticipantID

class CoordinatorInterface:

    def __init__(self, root, runCallback = None):
        super().__init__()
        self.runCallback = runCallback

        self.root = root
        self.coordinator = Coordinator(participants.getCoordinator())
        self.coordinator.participants = participants.getAllParticipants()
        x = threading.Thread(target=self.coordinator.runServer, args=())
        x.start()
        
        root.title('Client interface')

        b2 = Button(root, text = 'Run Transaction', command = self.coordinator.write)
        b2.grid(row = 2, column = 1, pady = 5, padx = 5, sticky='nsew')

        root.mainloop()

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
    CoordinatorInterface(root)

