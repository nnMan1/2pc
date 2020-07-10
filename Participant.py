import thriftpy
from thriftpy.rpc import make_server


messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
ParticipantID = messages_thrift.ParticipantID

class Participant:

    def __init__(self):
        print('Kreiran je jedan ucesnik transakcije')
    
    def recover(self):
        print('recovered')
    
    def __last_recorded_state(self):
        return 'Abort'

    def canCommit():
        return 'commited'

    def doCommit():
        return 'commit'

    def doAbort():
        return 'abort'

    
if __name__=="__main__":

    handler = Participant()
    server = make_server(messages_thrift.Participant, handler, '10.42.0.1', 7001)
    print("serving...")
    server.serve()