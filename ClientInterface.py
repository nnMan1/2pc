from tkinter import *
import threading
import thriftpy
from Network import Network
from Client import Client
import threading
from queue import Queue

messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
from messages_thrift import ParticipantID, Coordinator

q = Queue()

class ClientInterface:

    def __init__(self):
        super().__init__()

        self.network = Network(['server2', 'server1', 'coordinator'])
        self.network.draw()

        self.client = Client(self.put)
        x = threading.Thread(target=self.client.runServer, args=())
        x.start()        

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

    def put(self, name1, names, message):
        q.put((name1, names, message))

if __name__ == '__main__':

    interface = ClientInterface()

    while True:  # a lightweight "event loop"
        ans = q.get()
        print(ans)
        if ans[1] == "TurnOff":
            interface.network.turnOffNode(ans[0])
        elif ans[1] == "TurnOn":
            interface.network.turnOnNode(ans[0])
        else:    
            interface.network.sentMessage(ans[0], ans[1], ans[2])

        q.task_done()

