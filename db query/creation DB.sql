--Drop tables if they exist, reverse dependency order to avoid Foreign Key errors.
DROP TABLE IF EXISTS Fact_Streams;
DROP TABLE IF EXISTS Bridge_Track_Artist;
DROP TABLE IF EXISTS Dim_Track;
DROP TABLE IF EXISTS Dim_Sound;
DROP TABLE IF EXISTS Dim_Album;
DROP TABLE IF EXISTS Dim_Artist;
DROP TABLE IF EXISTS Dim_Time;
DROP TABLE IF EXISTS Dim_Youtube;

-- CREATION

-- Dim. Time
CREATE TABLE Dim_Time (
    date_id INT PRIMARY KEY,
    full_date DATE,
    year INT,
    month INT,
    day INT,
    quarter INT,
    season VARCHAR(20)
);

-- Dim. Artist
CREATE TABLE Dim_Artist (
    artist_id INT PRIMARY KEY,
    name NVARCHAR(255),
    gender VARCHAR(10),
    birth_date DATE,
    birth_place NVARCHAR(100),
    nationality VARCHAR(100),
    description NVARCHAR(MAX),
    country NVARCHAR(100),
    region NVARCHAR(100),
    province NVARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    active_start DATE,
    active_end DATE
);

--Dim Album
CREATE TABLE Dim_Album (
    album_id VARCHAR(50) PRIMARY KEY,
    title NVARCHAR(255),
    release_date DATE,
    album_type VARCHAR(50)
);

-- Dim. Sound
CREATE TABLE Dim_Sound (
    sound_id INT PRIMARY KEY,
    bpm FLOAT,
    rolloff FLOAT,
    flux FLOAT,
    rms FLOAT,
    flatness FLOAT,
    spectral_complexity FLOAT,
    pitch FLOAT,
    loudness FLOAT,
    mood VARCHAR(50) 
);

--Dim. Tracks
CREATE TABLE Dim_Track (
    track_id VARCHAR(50) PRIMARY KEY,
    title NVARCHAR(MAX),
    language VARCHAR(10),
    explicit BIT,
    disc_number INT,
    track_number INT,
    duration_ms FLOAT,
    swear_it INT,
    swear_en INT,
    n_sentences FLOAT,
    n_tokens FLOAT,
    char_per_tok FLOAT,
    avg_token_per_clause FLOAT,
    swear_it_words NVARCHAR(MAX),
    swear_en_words NVARCHAR(MAX),
    lyrics NVARCHAR(MAX)
);

-- Bride Table Track-Artists
CREATE TABLE Bridge_Track_Artist (
    track_id VARCHAR(50),
    artist_id INT,
    role VARCHAR(20),
    PRIMARY KEY (track_id, artist_id),
    FOREIGN KEY (track_id) REFERENCES Dim_Track(track_id),
    FOREIGN KEY (artist_id) REFERENCES Dim_Artist(artist_id)
);

--Dim Youtube
CREATE TABLE Dim_Youtube (
    virality_id INT PRIMARY KEY,
    virality_tier VARCHAR(50)
);

--Fact table
CREATE TABLE Fact_Streams (
    fact_id INT IDENTITY(1,1) PRIMARY KEY, 
    track_id VARCHAR(50),
    album_id VARCHAR(50),
    date_id INT,
    youtube_id INT,
    sound_id INT,               
    main_artist_id INT, 
    streams_1month BIGINT,      
    popularity FLOAT,
    
    FOREIGN KEY (track_id) REFERENCES Dim_Track(track_id),
    FOREIGN KEY (album_id) REFERENCES Dim_Album(album_id),
    FOREIGN KEY (date_id) REFERENCES Dim_Time(date_id),
    FOREIGN KEY (sound_id) REFERENCES Dim_Sound(sound_id),
    FOREIGN KEY (main_artist_id) REFERENCES Dim_Artist(artist_id),
    FOREIGN KEY (youtube_id) REFERENCES Dim_Youtube(virality_id)
);