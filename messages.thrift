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

    void doCommit(),

    void doAbort(),

    Status prepare()
}

service Coordinator {
  
    void recover(),
    
    void __last_recorded_state(),

    void canCommit(),

    void doCommit(),

    void doAbort(),

    void prepare(),

    void reciveVote(1: VoteMessage voteMessage)
}