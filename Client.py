import socket
from Coordinator import Coordinator
from Participant import Participant
import thriftpy
from thriftpy.rpc import make_server
from thriftpy.rpc import client_context

messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
from messages_thrift import ParticipantID

class Client:

    def __init__(self, partcipantsFile, timeout = 20):
        self.partcipantsFile = partcipantsFile
        self.__readParticipantsFile()
        self.coordinator = Coordinator(timeout)
        self.coordinator.participant = self.partcipants
        print('Client created')
        

    def __readParticipantsFile(self):

        self.partcipants = []
        
        with open(self.partcipantsFile, 'r') as participants:
            for line in participants:
                line = line.strip()
                if len(line) == 0:
                    continue

                (name,ip,port) = line.split(' ')
                participantID = ParticipantID()
                participantID.name = name
                participantID.ip = ip
                participantID.port = int(port)
                self.partcipants.append(participantID)

        print(self.partcipants)


    def startParticipantsServers(self):

        server = make_server(messages_thrift.Coordinator, self.coordinator, '127.0.0.1', 6000)
        self.coordinator.recover()
        print("serving coordinator...")
        server.serve()

        for paricipant in self.partcipants:
            handler  = Participant(paricipant, self.timeout, self.coordinator)
            handler.recover()
            print("serving {}...".format(paricipant))
            participant = make_server(messages_thrift.Participant, handler, '127.0.0.1', participant.port)
            server.serve()


    
if __name__=="__main__":

    client = Client('participants.conf')
    client.startParticipantsServers()
