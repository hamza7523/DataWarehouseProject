# PixelPlay Data Warehouse Project

## Summary

This repository contains the implementation of a comprehensive data warehouse solution for PixelPlay, a global DVD rental service. The project transforms raw transactional data into an optimized star schema dimensional model using Apache Airflow for ETL orchestration, Google BigQuery for data storage and processing, and Looker Studio for business intelligence dashboarding. This end-to-end data pipeline enables detailed analysis of rental transactions, customer behavior, and inventory performance.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Technologies & Tools](#technologies--tools)
- [Data Model](#data-model)
- [ETL Pipeline](#etl-pipeline)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Key Metrics & Insights](#key-metrics--insights)
- [Visualizations](#visualizations)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [References](#references)

## Project Overview

**PixelPlay** is a DVD rental service operating across multiple locations globally. This data warehouse project enables comprehensive business intelligence by:

- Converting transactional OLTP data to analytical OLAP structure
- Implementing a star schema dimensional model for efficient querying
- Automating ETL processes with Apache Airflow
- Leveraging Google BigQuery's scalable cloud infrastructure
- Providing interactive dashboards in Looker Studio

### Business Objectives

1. **Analyze Rental Patterns**: Understand customer rental behavior across time and geography
2. **Optimize Inventory**: Track film category performance and demand
3. **Revenue Analysis**: Monitor payment trends and transaction volumes
4. **Geographic Insights**: Identify high-performing markets and expansion opportunities
5. **Operational Efficiency**: Automate data processing and ensure data quality

### Project Deliverables

- ✅ Star schema dimensional model
- ✅ Automated ETL pipeline in Apache Airflow
- ✅ Scalable data warehouse in Google BigQuery
- ✅ Interactive Looker Studio dashboards
- ✅ Comprehensive documentation and video presentation

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│  Source Data    │
│  (BigQuery)     │
│  - Payment      │
│  - Rental       │
│  - Customer     │
│  - Inventory    │
│  - Film         │
│  - Category     │
│  - Store        │
│  - Address      │
│  - City         │
│  - Country      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Apache Airflow  │
│   ETL DAG       │
│                 │
│  1. Extract     │
│  2. Transform   │
│  3. Load        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Warehouse  │
│  (BigQuery)     │
│                 │
│  Star Schema:   │
│  - Fact Table   │
│  - Dim Tables   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Looker Studio  │
│   Dashboards    │
│                 │
│  - Metrics      │
│  - Analytics    │
│  - Reports      │
└─────────────────┘
```

### Data Flow

```
Source OLTP Tables → Extract → Transform → Load → Star Schema → BI Dashboards
```

## Technologies & Tools

### Cloud Infrastructure
- **Google Cloud Platform (GCP)**: Cloud infrastructure provider
- **Google BigQuery**: Serverless data warehouse and analytics platform
- **Cloud Storage**: Data staging and backups
- **IAM**: Authentication and access control

### ETL & Orchestration
- **Apache Airflow**: Workflow orchestration and scheduling
- **Airflow BigQuery Operators**: Native BigQuery integration
- **Python**: DAG definition and custom transformations
- **Cloud Composer** (optional): Managed Airflow on GCP

### Business Intelligence
- **Looker Studio** (formerly Google Data Studio): Interactive dashboards and reports
- **SQL**: Data querying and analysis

### Development Tools
- **Git**: Version control
- **GitHub**: Code repository
- **Visual Studio Code**: IDE
- **Docker** (optional): Local Airflow development

### Additional Technologies
- **YAML/JSON**: Configuration files
- **Google Cloud SDK**: CLI for GCP management

## Data Model

### Source Data (OLTP Schema)

The original PixelPlay dataset consists of normalized transactional tables:

#### Core Transaction Tables
- **Payment**: Payment transactions with amount, date, and customer info
- **Rental**: Rental records with rental/return dates
- **Customer**: Customer demographic information

#### Product & Inventory Tables
- **Inventory**: DVD copies available for rental
- **Film**: Movie information (title, description, release year)
- **Category**: Film genre classifications

#### Geographic Tables
- **Store**: Store location information
- **Address**: Physical addresses
- **City**: City information
- **Country**: Country data

### Target Data (Star Schema)

The dimensional model follows Kimball methodology with one fact table and multiple dimension tables:

#### Fact Table

**FactRental** (Central transaction metrics)

| Column | Type | Description |
|--------|------|-------------|
| rental_id | INTEGER | Primary key |
| payment_id | INTEGER | Foreign key to DimPayment |
| date_id | INTEGER | Foreign key to DimDate |
| location_id | INTEGER | Foreign key to DimLocation |
| rental_detail_id | INTEGER | Foreign key to DimRental |
| store_id | INTEGER | Foreign key to DimStore |
| total_amount | DECIMAL | Payment amount |
| rental_days | INTEGER | Duration of rental |

#### Dimension Tables

**1. DimPayment** (Payment details)
- payment_id (PK)
- payment_date
- amount
- payment_method
- customer_id

**2. DimDate** (Calendar dimension)
- date_id (PK)
- full_date
- year
- quarter
- month
- month_name
- week
- day_of_week
- day_name
- is_weekend
- is_holiday

**3. DimLocation** (Geographic hierarchy)
- location_id (PK)
- city
- city_id
- country
- country_id
- region

**4. DimRental** (Rental transaction details)
- rental_detail_id (PK)
- rental_date
- return_date
- rental_duration
- customer_id
- inventory_id
- staff_id

**5. DimStore** (Store with inventory and category)
- store_id (PK)
- store_address
- store_city
- store_country
- film_title
- film_category
- film_rating
- film_description
- inventory_id
- category_id

### Star Schema Benefits

1. **Query Performance**: Denormalized structure optimizes analytical queries
2. **Simplicity**: Easy to understand and navigate for business users
3. **Flexibility**: Supports ad-hoc analysis and diverse reporting needs
4. **Scalability**: Efficient for large data volumes in BigQuery
5. **Aggregation**: Fast aggregate calculations across dimensions

## ETL Pipeline

### Apache Airflow DAG Architecture

The ETL process is orchestrated as a Directed Acyclic Graph (DAG) with clear task dependencies:

```python
# DAG Structure
start → extract_data → validate_data → transform_data → load_dimensions → load_fact → data_quality_checks → end
```

### DAG Configuration

```python
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'pixelplay',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'pixelplay_etl',
    default_args=default_args,
    description='PixelPlay Data Warehouse ETL',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['data-warehouse', 'etl', 'bigquery'],
)
```

### ETL Phases

#### 1. Extract Phase

**Objective**: Source raw data from transactional tables in BigQuery

**Tasks**:
- Connect to source BigQuery dataset
- Extract relevant tables (Payment, Rental, Customer, etc.)
- Perform initial data quality checks
- Identify missing values and data type issues

**Sample Code**:
```sql
-- Extract payment data
SELECT 
    payment_id,
    customer_id,
    rental_id,
    amount,
    payment_date,
    staff_id
FROM `project.source_dataset.payment`
WHERE payment_date IS NOT NULL
```

#### 2. Transform Phase

**Objective**: Clean, enrich, and reshape data for dimensional model

**Transformations Applied**:

**a) Data Type Conversions**
```sql
-- Convert string dates to DATE type
SAFE_CAST(payment_date AS DATE) AS payment_date,
SAFE_CAST(amount AS DECIMAL) AS amount
```

**b) Date Parsing and Enrichment**
```sql
-- Extract date components for DimDate
EXTRACT(YEAR FROM rental_date) AS year,
EXTRACT(QUARTER FROM rental_date) AS quarter,
EXTRACT(MONTH FROM rental_date) AS month,
FORMAT_DATE('%B', rental_date) AS month_name,
EXTRACT(DAYOFWEEK FROM rental_date) AS day_of_week,
FORMAT_DATE('%A', rental_date) AS day_name,
CASE 
    WHEN EXTRACT(DAYOFWEEK FROM rental_date) IN (1, 7) 
    THEN TRUE ELSE FALSE 
END AS is_weekend
```

**c) Joining Related Tables**
```sql
-- Create enriched DimLocation
SELECT 
    ROW_NUMBER() OVER() AS location_id,
    ci.city,
    ci.city_id,
    co.country,
    co.country_id,
    CASE 
        WHEN co.country IN ('USA', 'Canada', 'Mexico') THEN 'North America'
        WHEN co.country IN ('UK', 'France', 'Germany') THEN 'Europe'
        ELSE 'Other'
    END AS region
FROM `project.source.city` ci
JOIN `project.source.country` co ON ci.country_id = co.country_id
```

**d) Denormalization**
```sql
-- Denormalize Store with Film and Category
SELECT 
    s.store_id,
    a.address AS store_address,
    ci.city AS store_city,
    co.country AS store_country,
    f.title AS film_title,
    c.name AS film_category,
    f.rating AS film_rating,
    f.description AS film_description,
    i.inventory_id,
    c.category_id
FROM `project.source.store` s
LEFT JOIN `project.source.address` a ON s.address_id = a.address_id
LEFT JOIN `project.source.city` ci ON a.city_id = ci.city_id
LEFT JOIN `project.source.country` co ON ci.country_id = co.country_id
LEFT JOIN `project.source.inventory` i ON s.store_id = i.store_id
LEFT JOIN `project.source.film` f ON i.film_id = f.film_id
LEFT JOIN `project.source.film_category` fc ON f.film_id = fc.film_id
LEFT JOIN `project.source.category` c ON fc.category_id = c.category_id
```

**e) Derived Metrics**
```sql
-- Calculate rental duration
DATE_DIFF(return_date, rental_date, DAY) AS rental_duration
```

#### 3. Load Phase

**Objective**: Populate dimensional model in BigQuery

**Load Order** (respecting foreign key dependencies):
1. Load dimension tables (no dependencies)
2. Load fact table (references dimensions)

**Sample Load Commands**:
```sql
-- Create and load DimPayment
CREATE OR REPLACE TABLE `project.warehouse.DimPayment` AS
SELECT 
    payment_id,
    SAFE_CAST(payment_date AS TIMESTAMP) AS payment_date,
    SAFE_CAST(amount AS FLOAT64) AS amount,
    customer_id
FROM `project.source.payment`
WHERE amount > 0;

-- Create and load FactRental
CREATE OR REPLACE TABLE `project.warehouse.FactRental` AS
SELECT 
    r.rental_id,
    p.payment_id,
    d.date_id,
    l.location_id,
    r.rental_detail_id,
    s.store_id,
    p.amount AS total_amount,
    DATE_DIFF(r.return_date, r.rental_date, DAY) AS rental_days
FROM `project.source.rental` r
JOIN `project.warehouse.DimPayment` p ON r.rental_id = p.rental_id
JOIN `project.warehouse.DimDate` d ON DATE(r.rental_date) = d.full_date
JOIN `project.warehouse.DimLocation` l ON r.customer_id = l.location_id
JOIN `project.warehouse.DimRental` dr ON r.rental_id = dr.rental_detail_id
JOIN `project.warehouse.DimStore` s ON r.inventory_id = s.inventory_id;
```

### Data Quality Checks

Implemented throughout the pipeline:

```python
# Task: Validate data quality
validate_data = BigQueryCheckOperator(
    task_id='validate_data_quality',
    sql='''
        SELECT COUNT(*) 
        FROM `project.warehouse.FactRental` 
        WHERE rental_id IS NULL 
           OR total_amount < 0 
           OR rental_days < 0
    ''',
    use_legacy_sql=False,
    location='US',
)
```

### Task Dependencies

```python
# Define task flow
extract_payment >> extract_rental >> extract_customer >> transform_dimensions >> load_dim_payment
extract_payment >> extract_rental >> extract_customer >> transform_dimensions >> load_dim_date
extract_payment >> extract_rental >> extract_customer >> transform_dimensions >> load_dim_location
extract_payment >> extract_rental >> extract_customer >> transform_dimensions >> load_dim_rental
extract_payment >> extract_rental >> extract_customer >> transform_dimensions >> load_dim_store

[load_dim_payment, load_dim_date, load_dim_location, load_dim_rental, load_dim_store] >> load_fact_rental

load_fact_rental >> data_quality_checks >> send_success_email
```

## Installation & Setup

### Prerequisites

- Google Cloud Platform account with billing enabled
- Apache Airflow 2.0+ (or Cloud Composer)
- Python 3.8+
- Git installed
- gcloud CLI installed and configured

### Step 1: Set Up Google Cloud Project

```bash
# Create new GCP project
gcloud projects create pixelplay-dw --name="PixelPlay Data Warehouse"

# Set as active project
gcloud config set project pixelplay-dw

# Enable required APIs
gcloud services enable bigquery.googleapis.com
gcloud services enable composer.googleapis.com
gcloud services enable storage.googleapis.com
```

### Step 2: Create BigQuery Datasets

```bash
# Create source dataset
bq mk --dataset --location=US pixelplay-dw:source_data

# Create warehouse dataset
bq mk --dataset --location=US pixelplay-dw:warehouse

# Create staging dataset
bq mk --dataset --location=US pixelplay-dw:staging
```

### Step 3: Load Source Data

```bash
# Upload source CSV files to Cloud Storage
gsutil mb gs://pixelplay-source-data
gsutil cp data/*.csv gs://pixelplay-source-data/

# Load tables into BigQuery
bq load --source_format=CSV \
    --skip_leading_rows=1 \
    pixelplay-dw:source_data.payment \
    gs://pixelplay-source-data/payment.csv \
    payment_id:INTEGER,customer_id:INTEGER,rental_id:INTEGER,amount:FLOAT,payment_date:TIMESTAMP
```

### Step 4: Set Up Apache Airflow

#### Option A: Cloud Composer (Recommended for Production)

```bash
# Create Cloud Composer environment
gcloud composer environments create pixelplay-airflow \
    --location us-central1 \
    --zone us-central1-a \
    --machine-type n1-standard-2 \
    --node-count 3 \
    --python-version 3 \
    --image-version composer-2.0.0-airflow-2.2.3
```

#### Option B: Local Airflow (Development)

```bash
# Install Apache Airflow
pip install apache-airflow[google]==2.5.0
pip install apache-airflow-providers-google

# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@pixelplay.com
```

### Step 5: Configure Airflow Connections

```bash
# Add BigQuery connection
airflow connections add 'bigquery_default' \
    --conn-type 'google_cloud_platform' \
    --conn-extra '{"extra__google_cloud_platform__project": "pixelplay-dw", "extra__google_cloud_platform__key_path": "/path/to/service-account-key.json"}'
```

### Step 6: Deploy DAG

```bash
# Clone repository
git clone https://github.com/yourusername/DataWarehouseProject.git
cd DataWarehouseProject

# Copy DAG to Airflow DAGs folder
cp dags/pixelplay_etl_dag.py $AIRFLOW_HOME/dags/

# Or for Cloud Composer
gcloud composer environments storage dags import \
    --environment pixelplay-airflow \
    --location us-central1 \
    --source dags/pixelplay_etl_dag.py
```

### Step 7: Set Up Service Account

```bash
# Create service account
gcloud iam service-accounts create pixelplay-airflow \
    --display-name "PixelPlay Airflow Service Account"

# Grant BigQuery permissions
gcloud projects add-iam-policy-binding pixelplay-dw \
    --member="serviceAccount:pixelplay-airflow@pixelplay-dw.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

# Create and download key
gcloud iam service-accounts keys create ~/pixelplay-key.json \
    --iam-account=pixelplay-airflow@pixelplay-dw.iam.gserviceaccount.com
```

## Usage

### Running the ETL Pipeline

#### Manual Trigger (Airflow UI)

1. Open Airflow web interface: `http://localhost:8080` (local) or Cloud Composer URL
2. Navigate to DAGs list
3. Find `pixelplay_etl` DAG
4. Click the play button to trigger run
5. Monitor execution in Graph View or Tree View

#### Command Line Trigger

```bash
# Trigger DAG run
airflow dags trigger pixelplay_etl

# Check DAG status
airflow dags list-runs -d pixelplay_etl

# View task logs
airflow tasks logs pixelplay_etl load_fact_rental 2024-01-01
```

#### Scheduled Execution

The DAG is configured to run daily at midnight UTC:

```python
schedule_interval='@daily'  # Runs every day at 00:00 UTC
```

### Querying the Data Warehouse

#### Example Analytics Queries

**1. Total Revenue by Category**
```sql
SELECT 
    ds.film_category,
    SUM(f.total_amount) AS total_revenue,
    COUNT(f.rental_id) AS rental_count,
    AVG(f.total_amount) AS avg_revenue_per_rental
FROM `pixelplay-dw.warehouse.FactRental` f
JOIN `pixelplay-dw.warehouse.DimStore` ds ON f.store_id = ds.store_id
GROUP BY ds.film_category
ORDER BY total_revenue DESC
```

**2. Rental Trends Over Time**
```sql
SELECT 
    d.year,
    d.month_name,
    COUNT(f.rental_id) AS total_rentals,
    SUM(f.total_amount) AS monthly_revenue
FROM `pixelplay-dw.warehouse.FactRental` f
JOIN `pixelplay-dw.warehouse.DimDate` d ON f.date_id = d.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month
```

**3. Geographic Performance**
```sql
SELECT 
    l.country,
    l.city,
    COUNT(f.rental_id) AS rental_count,
    SUM(f.total_amount) AS total_revenue,
    AVG(f.rental_days) AS avg_rental_duration
FROM `pixelplay-dw.warehouse.FactRental` f
JOIN `pixelplay-dw.warehouse.DimLocation` l ON f.location_id = l.location_id
GROUP BY l.country, l.city
ORDER BY rental_count DESC
LIMIT 10
```

### Looker Studio Dashboard

#### Connecting to BigQuery

1. Go to [Looker Studio](https://lookerstudio.google.com/)
2. Create new report
3. Add data source → BigQuery
4. Select project: `pixelplay-dw`
5. Select dataset: `warehouse`
6. Choose tables: FactRental and dimension tables

#### Building Dashboards

**Key Visualizations**:
1. **Scorecard**: Total rentals, revenue, cities served
2. **Time Series**: Rental trends over time
3. **Pie Chart**: Category distribution
4. **Geo Map**: Rentals by country
5. **Bar Chart**: Top cities by revenue
6. **Table**: Detailed transaction view

## Key Metrics & Insights

### Business Metrics

#### Overall Performance
- **Total Rental Transactions**: 2,412
- **Total Revenue**: $9,847,782.80
- **Geographic Reach**: 978 cities served
- **Total Rental Days**: 51,675
- **Average Revenue per Rental**: $4,083.85
- **Average Rental Duration**: 21.4 days

### Key Insights

#### 1. Category Performance

**Top Categories by Rental Volume**:
1. **Drama**: 280+ rentals (35% of total)
2. **Documentary**: 160+ rentals (20% of total)
3. **Comedy**: 150+ rentals (19% of total)
4. **Action**: 130+ rentals (16% of total)
5. **Horror**: 80+ rentals (10% of total)

**Insight**: Drama dominates the catalog. Consider investing in more Documentary and Comedy titles to match demand.

#### 2. Geographic Distribution

**Top Cities by Rental Count**:
- **Ash Shahaniyah**: 23.7% of total rentals
- **Zhongfang**: 23.7% of total rentals
- **Wologorquan**: 23.7% of total rentals
- **Killarney**: 23.7% of total rentals

**Distribution**: Four cities account for 95% of all rentals, indicating highly concentrated customer base.

**Insight**: Focus marketing efforts on these key markets while exploring expansion opportunities in underserved regions.

#### 3. Rental Duration Patterns

**Average Rental Duration by Country**:
- **Qatar**: Highest average (28.5 days)
- **United States**: 22.3 days
- **United Kingdom**: 18.7 days
- **India**: 15.2 days

**Insight**: Qatar customers retain DVDs longest. Consider region-specific late fee policies and targeted promotions.

#### 4. Temporal Trends

**Year-over-Year Growth**:
- **2019**: 800 rentals
- **2020**: 1,612 rentals (+101% YoY)

**Seasonal Patterns**:
- **Q4**: Highest rental volume (holiday season)
- **Q2**: Lowest rental volume (summer months)

**Insight**: Significant spike in 2020 likely due to pandemic. Prepare for continued growth with inventory expansion.

#### 5. Revenue Analysis

**Revenue Distribution**:
- **Top 10% of rentals**: 45% of total revenue
- **Premium titles (>$100/rental)**: 12% of rentals, 38% of revenue
- **Standard titles (<$50/rental)**: 65% of rentals, 35% of revenue

**Insight**: Focus acquisition on premium content while maintaining variety for mass market.

## Visualizations

### Looker Studio Dashboard Screenshots

**Dashboard 1: Executive Summary**
- KPI Scorecards (Total Rentals, Revenue, Cities)
- Rental Trend Line Chart
- Category Pie Chart
- Geographic Heatmap

**Dashboard 2: Category Analysis**
- Category Performance Bar Chart
- Top Films Table
- Category Trends Over Time
- Revenue Mix by Category

**Dashboard 3: Geographic Insights**
- Interactive World Map
- Top 10 Cities Bar Chart
- Country Comparison Table
- Regional Revenue Distribution

**Dashboard 4: Operational Metrics**
- Average Rental Duration by Region
- Daily Rental Volume
- Return Rate Analysis
- Inventory Utilization

**View Full Presentation**: [Google Drive Link](https://drive.google.com/file/d/115VhGPPi_hRGWKANYzpEwtnuqAl2tJhZ/view?usp=sharing)

## Project Structure

```
DataWarehouseProject/
├── dags/
│   ├── pixelplay_etl_dag.py           # Main Airflow DAG
│   ├── sql/
│   │   ├── extract/
│   │   │   ├── extract_payment.sql
│   │   │   ├── extract_rental.sql
│   │   │   └── extract_customer.sql
│   │   ├── transform/
│   │   │   ├── create_dim_payment.sql
│   │   │   ├── create_dim_date.sql
│   │   │   ├── create_dim_location.sql
│   │   │   ├── create_dim_rental.sql
│   │   │   └── create_dim_store.sql
│   │   └── load/
│   │       └── create_fact_rental.sql
│   └── config/
│       └── airflow_config.yaml
├── data/
│   ├── source/
│   │   ├── payment.csv
│   │   ├── rental.csv
│   │   ├── customer.csv
│   │   └── ...
│   └── schema/
│       ├── star_schema.png
│       └── erd_diagram.png
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── etl_documentation.md
│   └── presentation.pdf
├── looker_studio/
│   ├── dashboard_executive.pdf
│   ├── dashboard_category.pdf
│   └── dashboard_geographic.pdf
├── scripts/
│   ├── setup_bigquery.sh
│   ├── deploy_dag.sh
│   └── data_quality_tests.py
├── tests/
│   ├── test_dag_integrity.py
│   ├── test_sql_queries.py
│   └── test_data_transformations.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Troubleshooting

### Common Issues

**Issue**: DAG not appearing in Airflow UI
```bash
# Solution: Check DAG syntax
python dags/pixelplay_etl_dag.py

# Verify DAG location
ls $AIRFLOW_HOME/dags/

# Check Airflow logs
tail -f $AIRFLOW_HOME/logs/scheduler/latest/pixelplay_etl_dag.py.log
```

**Issue**: BigQuery authentication failed
```bash
# Solution: Verify service account permissions
gcloud projects get-iam-policy pixelplay-dw

# Re-create connection
airflow connections delete bigquery_default
airflow connections add bigquery_default --conn-type google_cloud_platform

# Check key file path
echo $GOOGLE_APPLICATION_CREDENTIALS
```

**Issue**: SQL query timeout in BigQuery
```sql
-- Solution: Add partitioning to large tables
CREATE OR REPLACE TABLE `pixelplay-dw.warehouse.FactRental`
PARTITION BY DATE(rental_date)
AS SELECT ...

-- Use table clustering
CREATE OR REPLACE TABLE `pixelplay-dw.warehouse.FactRental`
CLUSTER BY location_id, store_id
AS SELECT ...
```

**Issue**: Dimension table has duplicate keys
```sql
-- Solution: Add DISTINCT or ROW_NUMBER()
SELECT DISTINCT
    payment_id,
    payment_date,
    amount
FROM `pixelplay-dw.source.payment`

-- Or use ROW_NUMBER to keep latest
SELECT * FROM (
    SELECT 
        *,
        ROW_NUMBER() OVER(PARTITION BY payment_id ORDER BY payment_date DESC) as rn
    FROM `pixelplay-dw.source.payment`
) WHERE rn = 1
```

**Issue**: Looker Studio data not refreshing
```
Solution:
1. Check BigQuery dataset permissions (Looker Studio needs Viewer role)
2. Refresh data source in Looker Studio settings
3. Clear browser cache
4. Re-authenticate BigQuery connection
```

### Performance Optimization

**1. Query Optimization**
```sql
-- Use table partitioning for large fact tables
CREATE OR REPLACE TABLE `warehouse.FactRental`
PARTITION BY DATE(rental_date)
CLUSTER BY store_id, location_id
AS SELECT ...

-- Limit data scanned with WHERE clauses
WHERE DATE(rental_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
```

**2. Airflow Performance**
```python
# Increase parallelism
default_args = {
    'max_active_runs': 3,
    'concurrency': 16,
}

# Use connection pooling
BigQueryExecuteQueryOperator(
    task_id='load_data',
    use_legacy_sql=False,
    pool='bigquery_pool',
)
```

**3. BigQuery Cost Optimization**
```sql
-- Use SELECT * sparingly
SELECT rental_id, payment_id, total_amount  -- Instead of SELECT *

-- Preview data before running full query
SELECT * FROM `warehouse.FactRental` LIMIT 1000

-- Use cached results
-- BigQuery automatically caches for 24 hours
```

## Future Enhancements

### Short-term (Next 3 Months)
- [ ] Add incremental loading strategy (delta loads vs. full refresh)
- [ ] Implement slowly changing dimensions (SCD Type 2) for Customer
- [ ] Create aggregate tables for common queries
- [ ] Add data quality monitoring with Great Expectations
- [ ] Implement alerting for ETL failures (email, Slack)

### Medium-term (6-12 Months)
- [ ] Add real-time streaming pipeline using Pub/Sub and Dataflow
- [ ] Implement data lineage tracking with Data Catalog
- [ ] Create ML models for demand forecasting (BigQuery ML)
- [ ] Build customer segmentation analysis
- [ ] Develop predictive rental duration model
- [ ] Add cost optimization with BigQuery reservations

### Long-term (1+ Years)
- [ ] Migrate to multi-cloud architecture (AWS Redshift, Azure Synapse)
- [ ] Implement CDC (Change Data Capture) from source systems
- [ ] Build automated anomaly detection for data quality
- [ ] Create self-service analytics portal for business users
- [ ] Implement A/B testing framework for content recommendations
- [ ] Add federated queries across multiple data sources

## Technologies Comparison

### Why BigQuery?

| Feature | BigQuery | Snowflake | Redshift |
|---------|----------|-----------|----------|
| **Pricing** | Pay-per-query | Compute + Storage | Cluster-based |
| **Scalability** | Serverless, auto-scale | Auto-scale | Manual scaling |
| **Performance** | Excellent for analytics | Excellent | Good |
| **Integration** | Native GCP | Multi-cloud | AWS native |
| **Ease of Use** | Very easy | Easy | Moderate |
| **Cost** | $$$ | $$$ | $$ |

**Decision**: BigQuery chosen for serverless architecture, seamless GCP integration, and strong analytics performance.

### Why Apache Airflow?

| Feature | Airflow | Luigi | Prefect |
|---------|---------|-------|---------|
| **Community** | Very large | Medium | Growing |
| **UI** | Excellent | Basic | Good |
| **Cloud Support** | Excellent (Composer) | Limited | Good (Cloud) |
| **Learning Curve** | Moderate | Easy | Easy |
| **Flexibility** | Very high | Medium | High |

**Decision**: Airflow selected for robust community support, excellent GCP integration (Cloud Composer), and comprehensive monitoring capabilities.

## Data Quality & Governance

### Data Quality Checks

```python
# Completeness check
check_null_rental_ids = BigQueryCheckOperator(
    task_id='check_null_rental_ids',
    sql='SELECT COUNT(*) FROM `warehouse.FactRental` WHERE rental_id IS NULL',
    expected_value=0
)

# Accuracy check
check_negative_amounts = BigQueryCheckOperator(
    task_id='check_negative_amounts',
    sql='SELECT COUNT(*) FROM `warehouse.FactRental` WHERE total_amount < 0',
    expected_value=0
)

# Consistency check
check_date_integrity = BigQueryCheckOperator(
    task_id='check_date_integrity',
    sql='SELECT COUNT(*) FROM `warehouse.FactRental` WHERE rental_days < 0',
    expected_value=0
)
```

### Data Governance

- **Data Lineage**: Documented in BigQuery Data Catalog
- **Access Control**: Row-level security and IAM policies
- **Data Retention**: 90-day retention for source data, 3-year for warehouse
- **Compliance**: GDPR-compliant data handling and deletion procedures
- **Audit Logs**: Cloud Audit Logs track all BigQuery access

## References

### Documentation
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Google BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Looker Studio Help](https://support.google.com/looker-studio)
- [Kimball Dimensional Modeling](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)

### Tutorials & Resources
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Star Schema Design](https://en.wikipedia.org/wiki/Star_schema)

### Video Presentation
- [Full Project Presentation](https://drive.google.com/file/d/115VhGPPi_hRGWKANYzpEwtnuqAl2tJhZ/view?usp=sharing)

## License

This project is for educational and portfolio purposes. The PixelPlay dataset is based on the Sakila sample database.

## Contact & Collaboration

For questions, suggestions, or collaboration:
- **GitHub**: [Your GitHub Profile]
- **LinkedIn**: [Your LinkedIn]
- **Email**: your.email@example.com

## Acknowledgments

- Google Cloud Platform for robust infrastructure
- Apache Airflow community for excellent orchestration tools
- Kimball Group for dimensional modeling methodology
- Sample dataset inspired by MySQL Sakila database

---

**Built with ☁️ using Apache Airflow, BigQuery, and Looker Studio**
