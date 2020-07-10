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
        print('Kreiran je jedan ucesnik transakcije')
    
    def recover(self):
        print('recovered')
    
    def __last_recorded_state(self):
        return 'Abort'

    def canCommit(self):
        return True

    def doCommit():
        return 'commit'

    def doAbort():
        return 'abort'

    def prepare(self):
        print('preparing participant', self.participant)
        print(self.cordinator)
        logFile = open(self.participant.name + '.log', 'a+') 
        if self.canCommit():
            logFile.write('VOTE_COMMTI\n')
            return Status.VOTE_COMMIT
        else:
            logFile.write('VOTE_ABORT\n')
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