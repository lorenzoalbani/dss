# 🎵 Music Data Warehouse & Analytics Platform

> A comprehensive Decision Support System project implementing a complete data pipeline from raw music data to interactive business intelligence dashboards.

## 📋 Project Overview

This project implements an **end-to-end data warehousing and business intelligence solution** for music streaming analytics. Starting from raw JSON and XML data sources, the pipeline encompasses data enrichment through web scraping, advanced ETL processes, OLAP cube design, and interactive Power BI dashboards.

The system analyzes music streaming patterns, artist metadata, audio features, and lyrics characteristics to provide actionable insights for decision-making in the music industry.

## 🎯 Key Features

### Advanced Data Enrichment
- **YouTube Integration**: Web scraping to enrich tracks with virality metrics and social engagement data
- **Mood Analysis**: Automated classification of tracks based on audio features (BPM, spectral complexity, pitch, loudness)
- **Lyrics Intelligence**: Text analysis including profanity detection, token counting, and sentence structure metrics
- **Geographic Data**: Artist location mapping with latitude/longitude coordinates and regional information

### Intelligent Data Architecture
- **Star Schema Design**: Optimized dimensional model with fact and dimension tables
- **Bridge Tables**: Support for many-to-many relationships (e.g., track collaborations with multiple artists)
- **Temporal Dimensions**: Complete time hierarchy (year, quarter, season, month, day) for time-series analysis
- **Audio Features**: Dedicated sound dimension with melodic attributes (rolloff, flux, RMS, flatness, spectral complexity)

### Enterprise-Grade ETL
- **Hybrid Approach**: Python-based preprocessing and custom ETL processors combined with SQL Server Integration Services
- **6 SSIS Packages**: Production-ready data transformation workflows
- **Data Quality**: Missing value imputation using multiple strategies (clustering, statistical methods, external sources)

### OLAP & Multidimensional Analysis
- **SQL Server Analysis Services Cube**: Pre-aggregated data for fast analytical queries
- **MDX Queries**: Complex multidimensional expressions for sophisticated business questions
- **Drill-down Capabilities**: Navigate from high-level summaries to detailed records

## 🛠️ Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Data Analysis** | Python, Pandas, Jupyter Notebook, Scikit-learn |
| **Web Scraping** | Python (YouTube data extraction) |
| **Database** | Microsoft SQL Server |
| **ETL** | SQL Server Integration Services (SSIS), Custom Python ETL processors |
| **OLAP** | SQL Server Analysis Services (SSAS) |
| **Query Language** | T-SQL, MDX (Multidimensional Expressions) |
| **Visualization** | Power BI Desktop |

## 📊 Data Schema

### Fact Table
- **Fact_Streams**: Central fact table containing streaming metrics
  - Measures: `streams_1month`, `popularity`
  - Foreign keys to all dimension tables

### Dimension Tables
1. **Dim_Time**: Temporal dimension with date hierarchies
2. **Dim_Artist**: Artist metadata including birth info, nationality, geographic coordinates, and career timeline
3. **Dim_Album**: Album details with release dates and types
4. **Dim_Track**: Track information including duration, explicit flag, and complete lyrics
5. **Dim_Sound**: Audio features and melodic characteristics
6. **Dim_Youtube**: Virality classification tiers
7. **Bridge_Track_Artist**: Many-to-many relationship handling for collaborations

## 🚀 Project Workflow

```
1. Exploratory Data Analysis (EDA)
   └─ Initial data profiling and quality assessment

2. Data Preprocessing & Enrichment
   ├─ YouTube scraping for virality metrics
   ├─ Missing value imputation strategies
   ├─ Mood classification using audio features
   └─ Clustering analysis for data segmentation

3. Database Design & Implementation
   ├─ Dimensional modeling (Star schema)
   ├─ SQL Server database creation
   └─ Relationship and constraint definition

4. ETL Pipeline Development
   ├─ Python-based data transformation
   ├─ CSV staging layer generation
   ├─ SSIS package development (6 packages)
   └─ Data warehouse population

5. OLAP Cube Design
   ├─ Cube structure definition in SSAS
   ├─ Measure and dimension configuration
   └─ Aggregation optimization

6. Analytical Queries
   ├─ MDX query development
   ├─ Business intelligence metrics calculation
   └─ Result validation and export

7. Dashboard Development
   ├─ Power BI data model connection
   ├─ Interactive visualization design
   └─ Three comprehensive dashboards
```

## 📁 Repository Structure

```
dss/
├── artists.xml                    # Artist metadata (XML format)
├── tracks.json                    # Track data with audio features (35MB)
├── LDS Project 2025-2026.pdf     # Project specifications
│
└── Assignments/
    ├── task 1/                    # EDA with Jupyter Notebook
    ├── task 2/                    # Data preprocessing & YouTube scraping
    ├── task 3/                    # Clustering analysis
    ├── task 4/                    # Database schema SQL scripts
    ├── task 5/                    # Custom Python ETL processor + mood analysis
    ├── task 6/                    # Database loader utilities
    ├── task 7/                    # SSIS table preparation
    ├── task 8-13/                 # SQL query results (CSV exports)
    ├── SSIS_Project_Group3/       # Complete SSIS solution (6 packages)
    ├── task 14/                   # OLAP cube (SSAS project)
    ├── task 15-19/                # MDX queries with Excel exports
    ├── task_20_21_22.pbix         # Power BI dashboard file
    └── PBI screenshots/           # Dashboard visualizations (3 images)
```

## 🎨 Dashboard Highlights

The Power BI implementation includes **three interactive dashboards** providing:

1. **Streaming Overview**: Top tracks, artists, and temporal trends
2. **Audio Analytics**: Mood distribution, sound feature analysis, and correlation matrices
3. **Geographic Insights**: Artist distribution by country/region with map visualizations

## 🔍 Interesting Technical Implementations

### Machine Learning Integration
- **K-means clustering** applied to audio features for automatic genre/mood segmentation
- Used cluster results to impute missing melodic features with statistically similar tracks

### Semantic Lyrics Analysis
- Profanity detection in multiple languages (Italian & English)
- Token-level analysis: `char_per_tok`, `avg_token_per_clause`
- Sentence structure metrics for complexity assessment

### Virality Scoring
- Custom tiering system based on YouTube engagement metrics
- Integrated as a dimension for streaming performance correlation

### Temporal Intelligence
- Season-aware analysis (Spring, Summer, Fall, Winter)
- Quarter-based business reporting
- Flexible date hierarchies for drill-down operations

## 📈 Use Cases

This data warehouse supports various analytical scenarios:

- **A&R Strategy**: Identify emerging artists based on streaming growth and virality
- **Playlist Optimization**: Analyze mood and audio feature patterns in successful playlists
- **Market Analysis**: Geographic distribution of artist popularity and genre preferences
- **Content Strategy**: Correlation between lyrics characteristics and audience engagement
- **Performance Forecasting**: Time-series analysis of streaming trends

## 👥 Project Info

**Course**: Decision Support Systems / Large Data Storage (LDS)  
**Academic Year**: 2025-2026  
**Group**: Group 3

## 📄 License

This project is part of academic coursework at Sapienza University of Rome.

---

*Built with ❤️ using the Microsoft Data Platform stack*
