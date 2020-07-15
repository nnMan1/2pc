enum Status {
  FAILED = 0;
  SUCCESSFUL = 1;
  VOTE_REQUEST = 2;
  VOTE_COMMIT = 3;
  VOTE_ABORT = 4;
  GLOBAL_COMMIT = 5;
  GLOBAL_ABORT = 6;
  COMMIT = 7;
  ABORT = 8;
}

struct ParticipantID {
  1:string name;
  2:i32 port;
}

enum Vote {
  ABORT = 0
  COMMIT = 1
}

struct VoteMessage {
  1: ParticipantID particpant,
  2: Vote vote
}

service Participant {
  
    void recover(),
    
    void __last_recorded_state(),

    void canCommit(),

    Status doCommit(1: string id),

    Status doAbort(1: string id),

    Status prepare(1: string id),

    Status write(1: string id)
}

service Coordinator {
  
    void recover(),
    
    Status last_recorded_state(1: string id),

    void canCommit(),

    void doCommit(),

    void doAbort(),

    void prepare(),

    void write(),
}

service Client {
    void animate(1:string node1, 2:list<string> node2, 3: string message)
}