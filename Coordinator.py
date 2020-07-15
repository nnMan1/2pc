import thriftpy
import argparse
import sys
import glob
import os
import time
import threading
import random
import time
import uuid
from thriftpy.rpc import make_server
from thriftpy.rpc import client_context

import clientMessage

messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
from messages_thrift import ParticipantID, Vote, Status, Participant

class Coordinator:

    def __init__(self, timeout = 20, option=0):
        self.participants = []
        self.file = open("Coor.log", "a+")
        self.timeout = timeout
        self.option = option   #mozemo da definisemo kad ce da padne koordinator
        self.startTime = time.time()
        self.endTime = time.time()
        #self.participant = participant

    def prepare(self):

        self.file = open("Coor.log", "a+")

        for participant in self.participants:
            if participant.name != 'coordinator':

                vote = Status.VOTE_ABORT
                try:
                    with client_context(Participant, participant.ip, participant.port) as client:
                        self.file.write(self.id + " VOTE_REQUEST\n")
                        self.file.flush()
                        self.startTime = time.time()
                        vote = client.prepare(self.id)
                        self.endTime = time.time()
                        if vote == Status.VOTE_ABORT or self.endTime - self.startTime > self.timeout:
                            self.doAbort()
                            return
                except:
                    self.doAbort()
                    print('error preparing participant', participant)
                    return
        
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
        last_line = ""
        for line in self.file:
            last_line = line

        last_line = last_line.split(" ")

        if( str(last_line[-1]) == "" or str(last_line[-1]) == "GLOBAL_COMMIT\n" or str(last_line[-1])=="GLOBAL_ABORT\n"):
            print("Coordinator >>> Do not need to recover")
            self.isRecover = 0
            return True

    def last_recorded_state(self, id):
        self.file = open('Coor.log', 'r+') 
        last_line = ""
        for line in self.file:
            line_split = line.split(" ")
            if len(line_split) >= 2 and line_split[0] == id:
                last_line = line

        last_line = last_line.split(' ')
        if last_line[-1] == 'GLOBAL_COMMIT\n':
            return Status.GLOBAL_COMMIT
        if last_line[-1] == 'GLOBAL_ABORT\n':
            return Status.GLOBAL_ABORT

    def canCommit(self):
        return 'canCommit'

    def doCommit(self):

        self.file = open("Coor.log", "a+")

        clientMessage.sentMessage('coordinator', [], 'GLOBAL_COMMIT')

        for participant in self.participants:
            if participant.name != 'coordinator':
                commited = False
                while not commited:
                    try:
                        with client_context(messages_thrift.Participant, participant.ip, participant.port) as client:
                            status = client.doCommit(self.id)
                            if status == Status.SUCCESSFUL:
                                commited = True
                    except:
                        print('error aborting participant', participant)

        self.file.write(self.id + ' GLOBAL_COMMIT\n')
        self.file.flush()

    def doAbort(self):

        self.file = open("Coor.log", "a+")

        for participant in self.participants:
            if participant.name != 'coordinator':
                try:
                    with client_context(messages_thrift.Participant, participant.ip, participant.port) as client:
                        status = client.doAbort(self.id)
                        if status == Status.SUCCESSFUL:
                            break
                except:
                    print('error aborting participant', participant)

        self.file.write(self.id + ' GLOBAL_ABORT\n')
        self.file.flush()

        clientMessage.sentMessage('coordinator', [], 'GLOBAL_ABORT')

    def write(self):

        clientMessage.sentMessage('coordinator', [] ,'init')
        self.id = str(uuid.uuid4())        
        self.file = open("Coor.log", "a+")
        self.file.write(self.id + ' INIT\n')
        self.file.flush()

        for participant in self.participants:
            try:
                with client_context(Participant, participant.ip, participant.port) as client:
                    client.write(self.id)
            except:
                print('error writing to participant')
            
        self.prepare()

if __name__ == '__main__':
    #python3 Coordinator.py 20 participants.txt 60 0
    # parser = argparse.ArgumentParser(description='coordinator')
    # parser.add_argument('Port',type=int,help='Port')
    # parser.add_argument('ParticipantsFile',type=str,help='All Participants')
    # parser.add_argument('timeout',type=int,help='Timeout for Coordinator')
    # parser.add_argument('option',type=int,help='Option to crash Coordinator')
    # args = parser.parse_args()

    all_participants = []

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
                coordinator = participantID

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

            all_participants.append(participantID)

    # handler = Coordinator(args.timeout, args.option)
    handler = Coordinator()
    handler.participants =  all_participants

    handler.recover()
    #handler.write()
   
    # with client_context(messages_thrift.Participant,'10.42.0.1', 7001) as client:
    #     client.recover()

    server = make_server(messages_thrift.Coordinator, handler, '127.0.0.1', 7000)
    print("serving...")
    server.serve()