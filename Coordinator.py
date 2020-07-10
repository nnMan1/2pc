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
Vote = messages_thrift.Vote

class Coordinator:
    def __init__(self, timeout, option):
        self.participants = []
        self.file = open("Coor.log", "a+")
        self.timeout = timeout
        self.option = option   #mozemo da definisemo kad ce da padne koordinator
        self.startTime = time.time()
        self.endTime = time.time()
        self.participant = participant
        self.votedCommit = set()

    def prepare(self):
        for participant in self.participants:
            if participant.name != 'coordinator':
                try:
                    with client_context(messages_thrift.Participant, participant.ip, participant.port) as client:
                        vote = client.prepare()
                except:
                    print('error preparing participant', participant)
              


    def reciveVote(self, vote_message):
        print('Vote recived')
        print(vote_message)
        if vote_message.vote == Vote.COMMIT:
            print(vote_message)
            self.votedCommit.insert(vote_message.participant)
        else:
            for participant in self.participants:
                try:
                    with client_context(messages_thrift.Participant, participant.ip, participant.port) as client:
                        client.doAbort()
                except:
                    print('error preparing participant', participant)

    
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
    
    def __last_recorded_state(self):
        return 'Abort'

    def canCommit():
        return 'canCommit'

    def doCommit():
        return 'commit'

    def doAbort():
        return 'abort'

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