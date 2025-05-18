# DataWarehouseProject
DataWarehouse Project on Apache Airflow and BigQuery, with BI Dashboarding on LookerStudio. 
Drive link for you to see full video based presentation:

https://drive.google.com/file/d/115VhGPPi_hRGWKANYzpEwtnuqAl2tJhZ/view?usp=sharing




PixelPlay Data Warehouse Project
This repository contains the implementation of a comprehensive data warehouse solution for PixelPlay using a star schema model, Apache Airflow for ETL orchestration, and Google BigQuery for data storage and analysis. The project transforms raw DVD rental transaction data into an optimized analytical model for business intelligence.
Project Overview
PixelPlay is a DVD rental service with operations across multiple locations globally. This data warehouse project enables detailed analysis of rental transactions, customer behavior, and inventory performance through a structured dimensional model.
Show Image
Complete Project Flow
1. Source Data Analysis
The project begins with analyzing the original PixelPlay dataset, which consists of several transactional tables:

Payment: Contains payment transactions with amount, date, and customer information
Rental: Records rental transactions with rental/return dates
Customer: Customer demographic information
Inventory: Tracks DVD copies available for rental
Film: Movie information including title, description, and release year
Category: Film genre classifications
Store: Store location information
Address/City/Country: Geographic hierarchy information

2. Dimensional Modeling
After analyzing the source data, we designed a star schema model optimized for analytical queries:

Fact Table: Central transaction metrics with foreign keys to dimensions
Dimension Tables:

DimPayment: Payment transaction details and amounts
DimDate: Calendar dimension for time-based analysis
DimLocation: Geographic hierarchy combining City and Country tables
DimRental: Rental transaction details with rental/return dates
DimStore: Consolidated store information with inventory and category details



This dimensional approach allows for flexible slice-and-dice analysis across multiple business perspectives.
3. ETL Pipeline Implementation in Apache Airflow
The core of the project is a robust ETL pipeline implemented as a Directed Acyclic Graph (DAG) in Apache Airflow:
Source Data → Extract → Transform → Load → Dimensional Model → Analysis
Extract Phase

Raw data is sourced from the original PixelPlay transactional tables in BigQuery
Data quality checks identify missing values and data type issues

Transform Phase

Data type conversions (strings to dates, text to numeric values)
Date parsing and formatting (extracting date components)
Joining related tables to create enriched dimensions
Denormalization of hierarchical data
Calculation of derived metrics (rental duration, aggregates)

Load Phase

Optimized dimension tables are created first
Fact table is populated by joining dimension tables
Foreign key relationships are established

4. Apache Airflow DAG Architecture
The DAG orchestrates the entire ETL process with clearly defined task dependencies:
                            ┌─────────────────┐
                            │                 │
                            │  Source Tables  │
                            │                 │
                            └────────┬────────┘
                                     │
                                     ▼
              ┌───────────────────────────────────────────────┐
              │                                               │
 ┌────────────┴────────────┐   ┌────────────┐   ┌─────────────┴─────────────┐
 │                         │   │            │   │                           │
 ▼                         ▼   ▼            ▼   ▼                           ▼
┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌────────────┐  ┌────────────┐
│             │  │              │  │             │  │            │  │            │
│DimPayment   │  │DimDate       │  │DimLocation  │  │DimRental   │  │DimStore    │
│             │  │              │  │             │  │            │  │            │
└──────┬──────┘  └───────┬──────┘  └──────┬──────┘  └─────┬──────┘  └──────┬─────┘
       │                 │                │               │                │
       │                 │                │               │                │
       └────────────────┬┴────────────────┴───────────────┴────────────────┘
                        │
                        ▼
                  ┌────────────┐
                  │            │
                  │FACTS_TABLE │
                  │            │
                  └─────┬──────┘
                        │
                        ▼
                 ┌─────────────┐
                 │             │
                 │BI Dashboard │
                 │             │
                 └─────────────┘
5. SQL Transformation Implementation
Each task in the DAG uses BigQueryExecuteQueryOperator to execute specific SQL transformations:
DimPayment Creation
sqlCREATE OR REPLACE TABLE dwhproject-460111.PixelPlay.DimPayment AS
SELECT 
  payment_id,
  customer_id,
  SAFE_CAST(SUBSTR(payment_date, 1, 10) AS DATE) AS payment_date,
  SAFE_CAST(amount AS FLOAT64) AS amount
FROM dwhproject-460111.PixelPlay.Payment
WHERE payment_date IS NOT NULL
DimDate Creation
sqlCREATE OR REPLACE TABLE dwhproject-460111.PixelPlay.DimDate AS
WITH dates AS (
  SELECT DATE_ADD(DATE '2010-01-01', INTERVAL n DAY) AS date
  FROM UNNEST(GENERATE_ARRAY(0, 6209)) AS n
)
SELECT
  FORMAT_DATE('%Y%m%d', date) AS date_id,
  date,
  EXTRACT(YEAR FROM date) AS year,
  EXTRACT(MONTH FROM date) AS month,
  CONCAT('Q', EXTRACT(QUARTER FROM date)) AS quarters,
  'varchar' AS varchar
FROM dates
FACTS_TABLE Creation (Key Integration)
sqlCREATE OR REPLACE TABLE dwhproject-460111.PixelPlay.FACTS_TABLE AS
WITH enriched AS (
  SELECT
    p.payment_id                AS transaction_id,
    r.rental_id,
    DATE(p.payment_date)        AS transaction_date,
    DATE_TRUNC(DATE(p.payment_date), YEAR) AS transaction_year,
    DATE_TRUNC(DATE(p.payment_date), MONTH) AS transaction_month,
    c.category_id,
    c.name                      AS category_name,
    l.city,
    l.country,
    p.customer_id,
    p.amount                    AS payment_amount,
    DATE_DIFF(r.return_date, r.rental_date, DAY) AS rental_duration
  FROM dwhproject-460111.PixelPlay.DimPayment  p
  JOIN dwhproject-460111.PixelPlay.DimRental   r
    ON r.customer_id = p.customer_id
   AND DATE(r.rental_date)   = DATE(p.payment_date)
  JOIN dwhproject-460111.PixelPlay.Inventory   i ON r.inventory_id = i.inventory_id
  JOIN dwhproject-460111.PixelPlay.Store       s ON i.store_id     = s.store_id
  JOIN dwhproject-460111.PixelPlay.Address     a ON s.address_id   = a.address_id
  JOIN dwhproject-460111.PixelPlay.DimLocation l ON a.city_id      = l.city_id
  JOIN dwhproject-460111.PixelPlay.Film_Category fc ON i.film_id    = fc.film_id
  JOIN dwhproject-460111.PixelPlay.Category    c  ON fc.category_id = c.category_id
)
SELECT
  transaction_id,
  rental_id,
  transaction_date,
  transaction_year,
  transaction_month,
  category_id,
  category_name,
  city,
  country,
  customer_id,
  payment_amount,
  rental_duration
FROM enriched
6. BigQuery Integration
The DAG connects to BigQuery using Google Cloud provider operators to execute the transformations. Key integration aspects:

Authenticates with GCP using service account credentials
Uses BigQuery's native SQL capabilities for efficient transformations
Leverages BigQuery's columnar storage for analytical query optimization
Implements SAFE_CAST operations to handle potential data quality issues

7. Data Analysis & Visualization
The final step connects the dimensional model to Looker Studio for business intelligence:
Key Metrics Analyzed

Transaction Volume: 2,412 total rental transactions
Geographic Reach: 978 cities served
Revenue: $9,847,782.80 total payment amount
Rental Duration: 51,675 total rental days

Key Insights

Category Performance: Drama (280+ rentals) is the most popular category, followed by Documentary (160+) and Comedy (150+)
Geographic Distribution: Four cities (Ash Shahaniyah, Zhongfang, Wologorquan, and Killarney) each account for 23.7% of rentals
Rental Duration Trends: Qatar shows the highest average rental duration
Temporal Patterns: Significant increase in rental activity in 2020 compared to previous years
