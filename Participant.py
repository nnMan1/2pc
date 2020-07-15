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

import clientMessage

messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
ParticipantID = messages_thrift.ParticipantID
Coordinator = messages_thrift.Coordinator
Status = messages_thrift.Status
VoteMessage = messages_thrift.VoteMessage
Vote = messages_thrift.Vote

#

class Participant:

    def __init__(self, participant, coordinator, timeout = 20, option = 4):
        self.participant = participant
        self.coordinator = coordinator
        self.file = open(self.participant.name + '.log', 'a+') 
        self.option = option
        self.isRecover = 1 #prvo provjerimo da li ima nedovrsenih transakcija
        self.server = make_server(messages_thrift.Participant, self, self.participant.ip, self.participant.port)
        print('Kreiran je jedan ucesnik transakcije')
        self. servereStopped = True
        self.recover()

    def recover(self):
        self.file = open(self.participant.name + '.log', 'r+') 
        last_line = ""
        for line in self.file:
            last_line = line

        last_line = last_line.split(" ")

        if( str(last_line[-1]) == "" or str(last_line[-1]) == "GLOBAL_COMMIT\n" or str(last_line[-1])=="GLOBAL_ABORT\n"):
            print("Participant >>> Do not need to recover")
            self.isRecover = 0
            return

        self.id = last_line[0]

        if str(last_line[-1])=='VOTE_COMMIT\n':
            # hasInfo = False
            # self.id = last_line[0]
            # print("Participant >>> Last message VOTE_COMMIT")
            # while not hasInfo:
            #     time.sleep(1)
            #     try:
            #         with  client_context(Coordinator, self.coordinator.ip, self.coordinator.port) as client:
            #             state = client.last_recorded_state(last_line[0])
            #             hasInfo = True
            #             if state == Status.GLOBAL_ABORT:
            #                 self.doAbort(last_line[0])
            #                 self.isRecover = 0
            #                 break
                        
            #             if state == Status.GLOBAL_COMMIT:
            #                 self.doCommit(last_line[0])
            #                 self.isRecover = 0
            #                 break
            #     except:
            #         print('Recovering participant in progress')
            return
    
        if str(last_line[-1])=='VOTE_ABORT\n':
            self.doAbort(self.id)
            self.isRecover = 0
            return

        if str(last_line[-1]=='INIT\n'):
            self.doAbort(self.id)
            self.isRecover = 0
            return

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

    def canCommit(self, id):
        self.file = open(self.participant.name + '.log', 'r+') 
        vote = ''
        for line in self.file:
            line = line.split(' ')
            if line[0] == id and line[-1] in ['VOTE_COMMIT\n', 'VOTE_ABORT\n', 'GLOBAL_COMMIT\n', 'GLOBAL_ABORT\n']:
                vote = line[-1]

        if vote in ['VOTE_COMMIT\n', 'GLOBAL_COMMIT\n']:
            return True
        
        if vote == ['VOTE_ABORT\n', 'GLOBAL_ABORT\n']:
            return False

        return True

    def doCommit(self, id):        
        self.file = open(self.participant.name + '.log', 'a+') 
        self.file.write(id + ' GLOBAL_COMMIT\n')

        if self.option <= 3:
            print('participant failure after commit')
            self.stopServing()
            return

        clientMessage.sentMessage(self.participant.name, [self.coordinator.name], 'COMMIT_ACK')
        self.file.flush()
        return Status.SUCCESSFUL

    def doAbort(self, id):
        self.file = open(self.participant.name + '.log', 'a+') 
        self.file.write(id + ' GLOBAL_ABORT\n')

        if self.option <= 3:
            print('participant failure after commit')
            self.stopServing()
            return

        clientMessage.sentMessage(self.participant.name, [self.coordinator.name], 'ABORT_ACK')
        self.file.flush()
        return Status.SUCCESSFUL
        
    def prepare(self, id):

        self.file = open(self.participant.name + '.log', 'a+') 

        if self.option <= 2:
            print('participant failure after voting')
            self.stopServing()
            return

        if self.canCommit(id) and self.isRecover == 0:
            self.id = id
            self.file.write(id + ' VOTE_COMMIT\n')
            clientMessage.sentMessage(self.participant.name, [self.coordinator.name], 'VOTE_COMMIT')
            self.file.flush()
            return Status.VOTE_COMMIT
        else:
            self.file.write(id + ' VOTE_ABORT\n')
            self.file.flush()
            clientMessage.sentMessage(self.participant.name, [self.coordinator.name], 'VOTE_ABORT')
            return Status.VOTE_ABORT
    
    def write(self, id):
        self.file = open(self.participant.name + '.log', 'a+') 

        #command
        print(self.option)
        if self.option == 1:
            print('participant failiure in initial')
            self.stopServing()
            return

        if self.isRecover == 0:
            self.id = id
            self.file.write(id + ' INIT\n')
            self.file.flush()
            return Status.VOTE_COMMIT
        
        return Status.FAILED

    def runServer(self):
        print("serving {}...".format(self.participant))
        self.servereStopped = False
        self.server.serve()

    def stopServing(self):
        #self.server.close()
        sys.exit("participant failure after voting")


if __name__=="__main__":

    parser = argparse.ArgumentParser(description='coordinator')
    #parser.add_argument('name',type=str,help='Name')
    args = parser.parse_args()
    args.name = 'server1'

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

    with open('./conf/participants.conf', 'r') as participant:
        for line in participant:
            line = line.strip()
            if len(line) == 0:
                continue

            (name,ip,port) = line.split(' ')
            if name == args.name:
                participantID = ParticipantID()
                participantID.name = name
                participantID.ip = ip
                participantID.port = int(port)
                participant = participantID
                
                
    handler = Participant(participant, coordinator, option = 1)
    handler.runServer()
    