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
Status = messages_thrift.Status
VoteMessage = messages_thrift.VoteMessage
Vote = messages_thrift.Vote

class Participant:

    def __init__(self, particpiant, timeout, option, coordinator):
        self.participant = participant
        self.cordinator = coordinator
        self.file = open(self.participant.name + '.log', 'a+') 
        print('Kreiran je jedan ucesnik transakcije')
    
    def recover(self):
        print('recovered')
    
    def __last_recorded_state(self):
        return 'Abort'

    def __canCommit(self):
        return True

    def doCommit(self):
        self.file.write('GLOBAL_COMMIT\n')
        self.file.flush()
        return Status.SUCCESSFUL

    def doAbort(self):
        self.file.write('GLOBAL_ABORT\n')
        self.file.flush()
        return Status.SUCCESSFUL
        

    def prepare(self):
        if self.__canCommit():
            self.file.write('VOTE_COMMIT\n')
            self.file.flush()
            return Status.VOTE_COMMIT
        else:
            self.file.write('VOTE_ABORT\n')
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
    server = make_server(messages_thrift.Participant, handler, '127.0.0.1', participant.port)
    print("serving...")
    server.serve()