import thriftpy
import argparse
import sys
import glob
import os
import time
import threading
import random
import time
from thriftpy.rpc import make_server
from thriftpy.rpc import client_context

messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
ParticipantID = messages_thrift.ParticipantID
Coordinator = messages_thrift.Coordinator
Status = messages_thrift.Status
VoteMessage = messages_thrift.VoteMessage
Vote = messages_thrift.Vote

#

class Participant:

    def __init__(self, particpiant, timeout, option, coordinator):
        self.participant = participant
        self.coordinator = coordinator
        self.file = open(self.participant.name + '.log', 'a+') 
        self.option = option
        self.isRecover = 1 #prvo provjerimo da li ima nedovrsenih transakcija
        print('Kreiran je jedan ucesnik transakcije')
    
    def recover(self):
        self.file = open(self.participant.name + '.log', 'r+') 
        last_line = ""
        for line in self.file:
            last_line = line

        last_line = last_line.split(" ")

        if( str(last_line[-1]) == "" or str(last_line[-1]) == "GLOBAL_COMMIT\n" or str(last_line[-1])=="GLOBAL_ABORT\n"):
            print("Participant >>> Do not need to recover")
            self.isRecover = 0
            return True


        if str(last_line[-1])=='VOTE_COMMIT\n':
            hasInfo = False
            self.id = last_line[0]
            print("Participant >>> Last message VOTE_COMMIT")
            while not hasInfo:
                try:
                    with  client_context(Coordinator, self.coordinator.ip, self.coordinator.port) as client:
                        state = client.last_recorded_state(last_line[0])
                        hasInfo = True
                        if state == Status.GLOBAL_ABORT:
                            self.doAbort()
                            self.isRecover = 0
                            break
                        
                        if state == Status.GLOBAL_COMMIT:
                            self.doCommit()
                            self.isRecover = 0
                            break
                except:
                    print('Recovering participant in progress')
    
        if str(last_line[-1])=='VOTE_ABORT\n':
            self.doAbort()
            self.isRecover = 0

    def last_recorded_state(self):
        self.file = open(self.participant.name + '.log', 'r+') 
        last_line = ""
        for line in self.file:
            line_split = line.split(" ")
            if len(line_split) >= 2 and line_split[0] == id:
                last_line = line

        last_line = line.split(' ')
        if last_line[-1] == 'GLOBAL_COMMIT\n':
            return Status.GLOBAL_COMMIT
        if last_line[-1] == 'GLOBAL_ABORT\n':
            return Status.GLOBAL_ABORT

    def __canCommit(self):
        return True

    def doCommit(self):
        self.file = open(self.participant.name + '.log', 'a+') 
        self.file.write(self.id + ' GLOBAL_COMMIT\n')
        self.file.flush()
        return Status.SUCCESSFUL

    def doAbort(self):
        self.file = open(self.participant.name + '.log', 'a+') 
        self.file.write(self.id + ' GLOBAL_ABORT\n')
        self.file.flush()
        return Status.SUCCESSFUL
        
    def prepare(self, id):

        self.file = open(self.participant.name + '.log', 'a+') 

        if self.option == 1:
            sys.exit("participant failure after voting")

        if self.__canCommit() and self.isRecover == 0:
            self.id = id
            self.file.write(id + ' VOTE_COMMIT\n')
            self.file.flush()
            return Status.VOTE_COMMIT
        else:
            self.file.write(id + ' VOTE_ABORT\n')
            self.file.flush()
            return Status.VOTE_ABORT
    
if __name__=="__main__":

    # parser = argparse.ArgumentParser(description='coordinator')
    # parser.add_argument('name',type=str,help='Name')
    # args = parser.parse_args()

    with open('participants.conf', 'r') as participant:
        for line in participant:
            line = line.strip()
            if len(line) == 0:
                continue

            (name,ip,port) = line.split(' ')
            # if name == args.name:
            if name == 'server1':
                participantID = ParticipantID()
                participantID.name = name
                participantID.ip = ip
                participantID.port = int(port)
                participant = participantID
            
            if name == 'coordinator':
                participantID = ParticipantID()
                participantID.name = name
                participantID.ip = ip
                participantID.port = int(port)
                coordinator = participantID
                
    handler = Participant(participant, 60, 0, coordinator)
    handler.recover()
    server = make_server(messages_thrift.Participant, handler, '127.0.0.1', participant.port)
    print("serving...")
    server.serve()