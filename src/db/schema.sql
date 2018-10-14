CREATE TABLE IF NOT EXISTS User (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    email     STRING  UNIQUE,
    password  STRING  NOT NULL,
    firstName STRING,
    lastName  STRING
);

CREATE TABLE IF NOT EXISTS OneOffFiles (
    id              INTEGER  PRIMARY KEY AUTOINCREMENT,
    userId          INTEGER  REFERENCES User (id) ON DELETE CASCADE
                                                    ON UPDATE CASCADE,
    uid             STRING   NOT NULL
                                UNIQUE,
    filename                 NOT NULL,
    expire          DATETIME,
    collected       BOOLEAN  DEFAULT (0) 
                                NOT NULL,
    collectedUserId INTEGER  REFERENCES User (id),
    password        STRING,
    requireLogin    BOOLEAN  NOT NULL
                                DEFAULT (0) 
);