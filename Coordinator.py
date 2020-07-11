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
from messages_thrift import ParticipantID, Vote, Status, Participant

class Coordinator:
    def __init__(self, timeout, option):
        self.participants = []
        self.file = open("Coor.log", "a+")
        self.timeout = timeout
        self.option = option   #mozemo da definisemo kad ce da padne koordinator
        self.startTime = time.time()
        self.endTime = time.time()
        self.participant = participant

    def prepare(self):
        for participant in self.participants:
            if participant.name != 'coordinator':

                vote = Status.VOTE_ABORT
                try:
                    with client_context(Participant, participant.ip, participant.port) as client:
                        self.file.write(" VOTE_REQUEST\n")
                        self.file.flush()
                        self.startTime = time.time()
                        vote = client.prepare()
                        self.endTime = time.time()
                        if vote == Status.VOTE_ABORT or self.endTime - self.startTime > self.timeout:
                            self.doAbort()
                            return
                except:
                    self.doAbort
                    print('error preparing participant', participant)
        
        self.doCommit()

    def transactionStatus(self):
        print("Coordinator >>> Send the final decision to the requested participant")
        retStatus = StatusReport()
        last_line = ""
        self.file = open('Coor.log', 'r+')
        for line in self.file:
            last_line = line
        para = last_line.split(" ")
        if str(para[-1]) =="GLOBAL_COMMIT\n":
            retStatus.status = Status.GLOBAL_COMMIT
            return retStatus
        if str(para[-1]) =="GLOBAL_ABORT\n":
            retStatus.status = Status.GLOBAL_ABORT
            return retStatus
                  
    def recover(self):
        self.file = open('Coor.log', 'r+')
        last_line = ""
        for line in self.file:
            last_line = line

        last_line = last_line.split(" ")

        if( str(last_line[-1]) == "" or str(last_line[-1]) == "GLOBAL_COMMIT\n" or str(last_line[-1])=="GLOBAL_ABORT\n"):
            print("Coordinator >>> Do not need to recover")
            self.isRecover = 0
            return True
    
    #def __last_recorded_state(self):
        

    def canCommit(self):
        return 'canCommit'

    def doCommit(self):
        for participant in self.participants:
            if participant.name != 'coordinator':
                try:
                    with client_context(messages_thrift.Participant, participant.ip, participant.port) as client:
                        status = client.doCommit()
                except:
                    print('error commiting participant', participant)

        self.file.write('GLOBAL_COMMIT\n')
        self.file.flush()

    def doAbort(self):
        
        for participant in self.participants:
            if participant.name != 'coordinator':
                try:
                    with client_context(messages_thrift.Participant, participant.ip, participant.port) as client:
                        status = client.doAbort()
                        if status == Status.SUCCESSFUL:
                            break
                except:
                    print('error preparing participant', participant)

        self.file.write('GLOBAL_ABORT\n')
        self.file.flush()

if __name__ == '__main__':
    #python3 Coordinator.py 20 participants.txt 60 0
    # parser = argparse.ArgumentParser(description='coordinator')
    # parser.add_argument('Port',type=int,help='Port')
    # parser.add_argument('ParticipantsFile',type=str,help='All Participants')
    # parser.add_argument('timeout',type=int,help='Timeout for Coordinator')
    # parser.add_argument('option',type=int,help='Option to crash Coordinator')
    # args = parser.parse_args()

    args = {'timeout': 20, 'ParticipantsFile': 'participants.conf', 'option': 0}
    all_participants = []

    # with open(args.ParticipantsFile, 'r') as participant:
    with open(args['ParticipantsFile'], 'r') as participant:
        for line in participant:
            line = line.strip()
            if len(line) == 0:
                continue

            (name,ip,port) = line.split(' ')
            participantID = ParticipantID()
            participantID.name = name
            participantID.ip = ip
            participantID.port = int(port)

            all_participants.append(participantID)

    # handler = Coordinator(args.timeout, args.option)
    handler = Coordinator(args['timeout'], args['option'])
    handler.participants =  all_participants
    handler.recover()
    handler.prepare()

    # with client_context(messages_thrift.Participant,'10.42.0.1', 7001) as client:
    #     client.recover()

    server = make_server(messages_thrift.Participant, handler, '127.0.0.1', 7003)
    print("serving...")
    server.serve()