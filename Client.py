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


    

    
if __name__=="__main__":

    client = Client('participants.conf')
    client.startParticipantsServers()
