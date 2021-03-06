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
import sqlite3

import clientMessage

messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
ParticipantID = messages_thrift.ParticipantID
Coordinator = messages_thrift.Coordinator
Status = messages_thrift.Status
VoteMessage = messages_thrift.VoteMessage
Vote = messages_thrift.Vote

import participants

class Participant:

    def __init__(self, participant, coordinator, timeout = 20, option = 4):

        self.lock = threading.Lock()
        self.participant = participant
        self.coordinator = coordinator
        self.file = open(self.participant.name + '.log', 'a+') 
        self.option = option
        self.isRecover = 1 #prvo provjerimo da li ima nedovrsenih transakcija
        self.server = make_server(messages_thrift.Participant, self, self.participant.ip, self.participant.port)
        try:
            self.conn = sqlite3.connect(self.participant.name + '.db')
            self.cur = self.conn.cursor()
            if(os.path.isfile( self.participant.name + '.db') == True):
                self.file.flush()
                self.cur.execute('CREATE TABLE IF NOT EXISTS Info(filename TEXT PRIMARY KEY, content TEXT)')
                self.cur.execute('CREATE TABLE IF NOT EXISTS Backup(filename TEXT PRIMARY KEY, content TEXT)')
                self.conn.commit()
                self.conn.close()
        except:
            print("Error connectiong to database")
            sys.exit(1)

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
            self.isRecover = 0
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
        if last_line[-1] == 'VOTE_COMMIT\n':
            return Status.VOTE_COMMIT
        if last_line[-1] == 'VOTE_ABORT\n':
            return Status.VOTE_ABORT
        if last_line[-1] == 'GLOBAL_ABORT\n':
            return Status.GLOBAL_ABORT
        
        return Status.NO_INFO

    def transactionDocumentName(self, id):
        self.file = open(self.participant.name + '.log', 'r+') 
        last_line = ""
        for line in self.file:
            line_split = line.split(" ")
            if len(line_split) >= 2 and line_split[0] == id:
                return line_split[1]
        
        return ''

    def canCommit(self, id):
        self.file = open(self.participant.name + '.log', 'r+') 
        vote = ''
        for line in self.file:
            line = line.split(' ')
            if line[0] == id and line[-1] in ['INIT\n', 'VOTE_COMMIT\n', 'VOTE_ABORT\n', 'GLOBAL_COMMIT\n', 'GLOBAL_ABORT\n']:
                vote = line[-1]

        if vote in ['VOTE_COMMIT\n', 'GLOBAL_COMMIT\n', 'INIT\n']:
            return True
        
        if vote == ['VOTE_ABORT\n', 'GLOBAL_ABORT\n']:
            return False

        return False 

    def doCommit(self, id):     

        if self.option <= 3:
            print('participant failure after commit')
            self.stopServing()
            return

        filename = self.transactionDocumentName(id)

        self.file = open(self.participant.name + '.log', 'a+') 

        try:
            self.conn = sqlite3.connect(self.participant.name + '.db')
            self.cur = self.conn.cursor()
            self.cur.execute('INSERT OR REPLACE INTO Info SELECT * FROM Backup WHERE filename = (?)', (filename,))
            self.conn.commit()
        except Exception as e:
            print(e.args)
            return Status.FAILED

        
        self.file.write(id + ' ' + filename +  ' GLOBAL_COMMIT\n')

        clientMessage.sentMessage(self.participant.name, [self.coordinator.name], 'COMMIT_ACK')
        self.file.flush()
        return Status.SUCCESSFUL

    def doAbort(self, id):

        if self.option <= 3:
            print('participant failure after commit')
            self.stopServing()
            return

        filename = self.transactionDocumentName(id)

        self.file = open(self.participant.name + '.log', 'a+') 

        try:
            self.conn = sqlite3.connect(self.participant.name + '.db')
            self.cur = self.conn.cursor()
            self.cur.execute('DELETE FROM Backup WHERE filename = (?)', (filename,))
            self.conn.commit()
        except Exception as e:
            print(e.args)
            return Status.FAILED


        self.file = open(self.participant.name + '.log', 'a+') 
        self.file.write(id + ' ' + filename + ' GLOBAL_ABORT\n')

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
    
    def isDataLocked(self, doc_name):
        isLocked = False
        self.file = open(self.participant.name + '.log', 'r+') 
        last_line = ""
        id = ''
        for line in self.file:
            line_split = line.split(" ")
            #id docName log
            if len(line_split) >= 3 and line_split[1] == doc_name:
                if line_split[-1] == 'INIT\n':
                    isLocked = True
                    id = line_split[0]
                
                if line_split[0] == id  and line_split[-1] in ['GLOBAL_COMMIT', 'GLOBAL_ABORT']:
                    isLocked = False
                            
        return isLocked

    def write(self, id, doc_name, doc_content):

        #command
        print(self.option)
        if self.option == 1:
            print('participant failiure in initial')
            self.stopServing()
            return

        if self.isRecover == 0:
            self.lock.acquire()
            try:
                if self.isDataLocked(doc_name):
                    return  Status.FAILED
                else:
                    self.file = open(self.participant.name + '.log', 'a+') 
                    self.file.write(id + ' '+ doc_name + ' INIT\n')
                    self.file.flush()
            finally:
                self.lock.release()
            
            self.id = id

            try:
                self.conn = sqlite3.connect(self.participant.name + '.db')
                self.cur = self.conn.cursor()
                self.cur.execute('INSERT OR REPLACE INTO Backup VALUES(?, ?)', (doc_name, doc_content))
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                raise e
            finally:
                self.conn.close()

            return Status.SUCCESSFUL
        
        return Status.FAILED

    def read(self, doc_name):
        try:
            self.conn = sqlite3.connect(self.participant.name + '.db')
            self.cur = self.conn.cursor()
            self.cur.execute('SELECT content FROM Info WHERE filename = ?', (doc_name,))
            cont = str(self.cur.fetchone()[0])
            if cont == None:
                cont = ""
            self.conn.commit()
            return cont
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.conn.close()

    def runServer(self):
        print("serving {}...".format(self.participant))
        self.servereStopped = False
        self.server.serve()

    def stopServing(self):
        #self.server.close()
        #raise SystemExit
        os._exit(0)
        #sys.exit("participant failure after voting")



if __name__=="__main__":

    parser = argparse.ArgumentParser(description='coordinator')
    parser.add_argument('name',type=str,help='Name')
    parser.add_argument('option', type=int)
    args = parser.parse_args()
    # args.name = 'server1'
    # args.option = 4

    coordinator = participants.getCoordinator()
    participant = participants.getParticipant(args.name)
                        
    handler = Participant(participant, coordinator, option = args.option)
    handler.runServer()
    #print(handler.read('doc1'))
    