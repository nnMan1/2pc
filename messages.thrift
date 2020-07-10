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

service Participant {
  
    void recover(),
    
    void __last_recorded_state(),

    void canCommit(),

    void doCommit(),

    void doAbort(),
}