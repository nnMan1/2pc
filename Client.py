import socket
import thriftpy
from thriftpy.rpc import make_server
from thriftpy.rpc import client_context
import time
#from ClientInterface import ClientInterface
from tkinter import *
import logging
import threading
import time

from Network import Network

#import Interface
#from Network import Network

messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
from messages_thrift import ParticipantID, Coordinator

class Client:

    def __init__(self, animateMessage):
        #self.partcipantsFile = partcipantsFile
        self.__readParticipants()
        self.animateMessage = animateMessage
        
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

    def animate(self, node1, nodes, message):
        if nodes == []:
            nodes = [participant.name for participant in self.all_participants]
        self.animateMessage(node1, nodes, message)

    def runTransaction(self):
         with client_context(Coordinator, self.coordinator.ip, self.coordinator.port) as client:
             client.write()

    def runServer(self):
        server = make_server(messages_thrift.Client, self, '127.0.0.1', 6000)
        print("serving client ...")
        server.serve()

if __name__=="__main__":

    # client = Client('participants.conf')
    # client.startParticipantsServers()
    
    #root = Tk()
    handler = Client()

    x = threading.Thread(target=handler.runServer, args=())
    x.start()

    #root.after(1, handler.runServer)
    #ClientInterface(root ,handler.runTransaction)
    #handler.graph.sentMessage('shard1rparticipantparticipantepl', ['shard3repl', 'shard2repl'], 'prepare')
    #time.sleep(1)

    
