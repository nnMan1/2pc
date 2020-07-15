from tkinter import *
import threading
import thriftpy
from Network import Network
from Client import Client
import threading

messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
from messages_thrift import ParticipantID, Coordinator

class ClientInterface:

    def __init__(self, root, runCallback = None):
        super().__init__()
        self.runCallback = runCallback

        self.root = root

        self.network = Network(['server2', 'server1', 'coordinator'])
        self.network.draw()

        self.client = Client(self.network.sentMessage)
        x = threading.Thread(target=self.client.runServer, args=())
        x.start()
        
        root.title('Client interface')

        b2 = Button(root, text = 'Run Transaction', command = self.client.runTransaction)
        b2.grid(row = 2, column = 1, pady = 5, padx = 5, sticky='nsew')

        root.mainloop()

    def __readParticipants(self):

        self.all_participants = []

        with open('./conf/coordinator.conf', 'r') as participant:
            for line in participant:
                line = line.strip()
                if len(line) == 0:
                    continue

                (name,ip,port) = line.split(' ')
                if name == 'coordinator':
                    participantID = ParticipantID()
                    participantID.name = name
                    participantID.ip = ip
                    participantID.port = int(port)
                    self.coordinator = participantID

        # with open(args.ParticipantsFile, 'r') as participant:
        with open('conf/participants.conf', 'r') as participant:
            for line in participant:
                line = line.strip()
                if len(line) == 0:
                    continue

                (name,ip,port) = line.split(' ')
                participantID = ParticipantID()
                participantID.name = name
                participantID.ip = ip
                participantID.port = int(port)

                self.all_participants.append(participantID)


if __name__ == '__main__':

    root = Tk()
    ClientInterface(root)

