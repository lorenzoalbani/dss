---------------------------------------------------------
-- 1. Dimensione Tempo
---------------------------------------------------------
CREATE TABLE Dim_Time (
    date_id INT PRIMARY KEY,
    full_date DATE,
    year INT,
    month INT,
    day INT,
    quarter INT,
    season VARCHAR(20)
);

---------------------------------------------------------
-- 2. Dimensione Artista
-- (La tua versione con correzione typo 'latidute' e description allargata)
---------------------------------------------------------
CREATE TABLE Dim_Artist (
    artist_id VARCHAR(50) PRIMARY KEY,
    name NVARCHAR(255),
    gender VARCHAR(10),
    birth_date DATE,
    birth_place NVARCHAR(100),
    nationality VARCHAR(100),
    description NVARCHAR(MAX), -- Ho messo MAX, 100 era troppo poco
    country NVARCHAR(100),
    region NVARCHAR(100),
    province NVARCHAR(100),
    latitude FLOAT,            -- Corretto da 'latidute'
    longitude FLOAT,
    active_start DATE,
    active_end DATE
);

---------------------------------------------------------
-- 3. Dimensione Album
---------------------------------------------------------
CREATE TABLE Dim_Album (
    album_id VARCHAR(50) PRIMARY KEY,
    title NVARCHAR(255),
    release_date DATE,
    album_type VARCHAR(50)
);

---------------------------------------------------------
-- 4. Dimensione Sound (AGGIORNATA)
-- Contiene metriche audio + MOOD (richiesto da te)
---------------------------------------------------------
CREATE TABLE Dim_Sound (
    sound_id INT PRIMARY KEY,
    
    -- Metriche tecniche dal JSON
    bpm FLOAT,
    rolloff FLOAT,
    flux FLOAT,
    rms FLOAT,
    flatness FLOAT,
    spectral_complexity FLOAT,
    pitch FLOAT,
    loudness FLOAT,
    
    -- Campo richiesto specifico
    mood VARCHAR(50) 
);

---------------------------------------------------------
-- 5. Dimensione Brano (AGGIORNATA COMPLETA)
-- Contiene info descrittive, metriche linguistiche e testi
---------------------------------------------------------
CREATE TABLE Dim_Track (
    track_id VARCHAR(50) PRIMARY KEY,
    title NVARCHAR(MAX),
    language VARCHAR(10),
    explicit BIT,
    
    -- Info posizionali nell'album
    disc_number INT,
    track_number INT,

    -- Metriche di durata e conteggi (dal tuo elenco)
    duration_ms FLOAT,
    swear_it INT,
    swear_en INT,

    -- Metriche Linguistiche (dal tuo elenco)
    n_sentences FLOAT,
    n_tokens FLOAT,
    char_per_tok FLOAT,
    avg_token_per_clause FLOAT,

    -- Contenuti testuali lunghi (dal tuo elenco)
    swear_it_words NVARCHAR(MAX), -- Lista parole parolacce IT
    swear_en_words NVARCHAR(MAX), -- Lista parole parolacce EN
    lyrics NVARCHAR(MAX)          -- Testo della canzone
);

---------------------------------------------------------
-- 6. Bridge Table (Partecipazioni Artisti)
---------------------------------------------------------
CREATE TABLE Bridge_Track_Artist (
    track_id VARCHAR(50),
    artist_id VARCHAR(50),
    role VARCHAR(20), -- 'Main' o 'Featured'
    PRIMARY KEY (track_id, artist_id),
    FOREIGN KEY (track_id) REFERENCES Dim_Track(track_id),
    FOREIGN KEY (artist_id) REFERENCES Dim_Artist(artist_id)
);

---------------------------------------------------------
-- 7. Fact Table (Streams)
---------------------------------------------------------

CREATE TABLE Fact_Streams (
    -- NUOVA COLONNA: Chiave surrogata autoincrementale
    fact_id INT IDENTITY(1,1) PRIMARY KEY, 
    
    track_id VARCHAR(50), -- Non è più PK, ma resta Foreign Key
    
    -- Chiavi Esterne
    album_id VARCHAR(50),
    date_id INT,
    sound_id INT,               
    main_artist_id VARCHAR(50), 
    
    -- Metriche
    streams_1month BIGINT,      
    popularity FLOAT,
    
    -- Vincoli (Foreign Keys)
    FOREIGN KEY (track_id) REFERENCES Dim_Track(track_id),
    FOREIGN KEY (album_id) REFERENCES Dim_Album(album_id),
    FOREIGN KEY (date_id) REFERENCES Dim_Time(date_id),
    FOREIGN KEY (sound_id) REFERENCES Dim_Sound(sound_id),
    FOREIGN KEY (main_artist_id) REFERENCES Dim_Artist(artist_id)
);