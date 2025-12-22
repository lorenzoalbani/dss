DELETE FROM Fact_Streams_SSIS;
DELETE FROM Bridge_Track_Artist_SSIS;
DELETE FROM Dim_Track_SSIS;
DELETE FROM Dim_Artist_SSIS;
DELETE FROM Dim_Album_SSIS;
DELETE FROM Dim_Sound_SSIS;
DELETE FROM Dim_Time_SSIS;

-- Assicuriamoci che la tabella sorgente sia NVARCHAR(255)
ALTER TABLE Dim_Album 
ALTER COLUMN title NVARCHAR(4000);

-- Assicuriamoci che la tabella destinazione sia IDENTICA
ALTER TABLE Dim_Album_SSIS 
ALTER COLUMN title NVARCHAR(4000);