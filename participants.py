import thriftpy
messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
ParticipantID = messages_thrift.ParticipantID

def getParticipant(name_in):
    with open('./conf/participants.conf', 'r') as participant:
        for line in participant:
            line = line.strip()
            if len(line) == 0:
                continue

            (name,ip,port) = line.split(' ')
            if name == name_in:
                participantID = ParticipantID()
                participantID.name = name
                participantID.ip = ip
                participantID.port = int(port)
                participant = participantID

    return participant

def getCoordinator():
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

    return coordinator

def getAllParticipants():
    
    all_participants = []
    with open('conf/participants.conf', 'r') as participants:
            for line in participants:
                line = line.strip()
                if len(line) == 0:
                    continue

                (name,ip,port) = line.split(' ')
                participantID = ParticipantID()
                participantID.name = name
                participantID.ip = ip
                participantID.port = int(port)

                all_participants.append(participantID)

    return all_participants