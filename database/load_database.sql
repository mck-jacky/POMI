CREATE TABLE Users (
    email           TEXT PRIMARY KEY,
    password_       TEXT NOT NULL,
    first_name      TEXT,
    last_name       TEXT,
    card_number     TEXT,
    cvv_num         TEXT,
    card_name       TEXT,
    exp_month       TEXT,
    exp_year        TEXT
    -- profile picture missing; might be added later
);

CREATE TABLE Events (
    id              INT PRIMARY KEY,
    creater         TEXT REFERENCES Users(email),
    title           TEXT,
    description_    TEXT,
    type_           TEXT,
    venue           TEXT,
    venue_type      TEXT,
    organizer       TEXT,
    time_start      TEXT,
    time_end        TEXT,
    tickets_available INT,
    tickets_left    INT,
    min_price       FLOAT,
    max_price       FLOAT,
    image_          TEXT,
    seat_plan       TEXT,
    ticket_price    FLOAT
);

CREATE TABLE Seats (
    row_            INT,
    seat_num        INT,
    event_          INT REFERENCES Events(id) ON DELETE CASCADE,
    user_           TEXT REFERENCES Users(email),
    PRIMARY KEY (row_, seat_num, event_)
);

CREATE TABLE Tickets (
    ticket_id       TEXT PRIMARY KEY,
    seat_num        INT,
    event_          INT REFERENCES Events(id) ON DELETE CASCADE,
    user_           TEXT REFERENCES Users(email)
);

CREATE TABLE Searches (
    id              SERIAL PRIMARY KEY,
    timestamp_      TEXT,
    user_           TEXT REFERENCES Users(email) ON DELETE CASCADE NOT NULL,
    search_term     TEXT NOT NULL
);

CREATE TABLE Reviews (
    thread_id       INT UNIQUE,
    timestamp_      TEXT,
    content         TEXT,
    event_          INT REFERENCES Events(id) ON DELETE CASCADE,
    owned_by        TEXT REFERENCES Users(email),
    host            TEXT,
    reply           TEXT,
    reply_timestamp TEXT,
    PRIMARY KEY (owned_by, event_)
);

CREATE TABLE Weather (
    id              INT REFERENCES Events(id) ON DELETE CASCADE,
    is_online       TEXT,
    tmp_mid         FLOAT,
    tmp_min         FLOAT,
    tmp_max         FLOAT,
    precipitation   FLOAT,
    wind_speed      FLOAT,
    PRIMARY KEY (id)
);

CREATE TABLE Historical_Events (
    id                      INT PRIMARY KEY,
    creator                 TEXT,
    type_                   TEXT,
    ticket_price            FLOAT,
    num_tickets_available   FLOAT,
    num_tickets_sold        FLOAT,
    host                    TEXT,
    is_online               TEXT,
    tmp_mid                 FLOAT,
    tmp_min                 FLOAT,
    tmp_max                 FLOAT,
    precipitation           FLOAT,
    wind_speed              FLOAT,
    actual_attendance       INT
);

CREATE TABLE Sales_Stats (
    event_id                INT REFERENCES Events(id) ON DELETE CASCADE,
    time_id                 INT,
    available_tickets       INT,
    tickets_sold            INT,
    num_tickets_left        INT,
    timestamp_              TEXT,
    prediction              INT,
    PRIMARY KEY (event_id, time_id)
);