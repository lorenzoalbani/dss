-- Elimina le tabelle nell'ordine inverso alle dipendenze
DROP TABLE IF EXISTS Fact_Streams;
DROP TABLE IF EXISTS Bridge_Track_Artist;
DROP TABLE IF EXISTS Dim_Track; -- Questa ora conterrà le swear
DROP TABLE IF EXISTS Dim_Sound; -- La nuova tabella
DROP TABLE IF EXISTS Dim_Album;
DROP TABLE IF EXISTS Dim_Artist;
DROP TABLE IF EXISTS Dim_Time;