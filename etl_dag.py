from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator
from datetime import datetime

with DAG(
    dag_id='star_schema_etl',
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    # ========================
    # Dimension Tables
    # ========================

    create_dim_payment = BigQueryExecuteQueryOperator(
       task_id='create_dim_payment',
       sql="""
       CREATE OR REPLACE TABLE `dwhproject-460111.PixelPlay.DimPayment` AS
       SELECT 
         payment_id,
         customer_id,
         SAFE_CAST(SUBSTR(payment_date, 1, 10) AS DATE) AS payment_date,  -- Extract first 10 chars (yyyy-mm-dd)
         SAFE_CAST(amount AS FLOAT64) AS amount
       FROM `dwhproject-460111.PixelPlay.Payment`
       WHERE 
         payment_date IS NOT NULL
       """,
       use_legacy_sql=False
    )

    create_dim_date = BigQueryExecuteQueryOperator(
        task_id='create_dim_date',
        sql="""
        CREATE OR REPLACE TABLE `dwhproject-460111.PixelPlay.DimDate` AS
        WITH dates AS (
          SELECT DATE_ADD(DATE '2010-01-01', INTERVAL n DAY) AS date
          FROM UNNEST(GENERATE_ARRAY(0, 6209)) AS n  -- Extended to 2030
        )
        SELECT
          FORMAT_DATE('%Y%m%d', date) AS date_id,
          date,
          EXTRACT(YEAR FROM date) AS year,
          EXTRACT(MONTH FROM date) AS month,
          CONCAT('Q', EXTRACT(QUARTER FROM date)) AS quarters,
          'varchar' AS varchar  -- Added to match schema
        FROM dates;
        """,
        use_legacy_sql=False
    )

    create_dim_location = BigQueryExecuteQueryOperator(
      task_id='create_dim_location',
      sql="""
      CREATE OR REPLACE TABLE `dwhproject-460111.PixelPlay.DimLocation` AS
    SELECT
      c.city_id,
      c.city,
      co.country
    FROM `dwhproject-460111.PixelPlay.City`       c
    LEFT JOIN `dwhproject-460111.PixelPlay.Country` co
      ON c.country_id = co.country_id
    """,
    use_legacy_sql=False
   )

    create_dim_rental = BigQueryExecuteQueryOperator(
        task_id='create_dim_rental',
        sql="""
        CREATE OR REPLACE TABLE `dwhproject-460111.PixelPlay.DimRental` AS
        SELECT
          rental_id,
          customer_id,
          inventory_id,
          SAFE_CAST(SUBSTR(rental_date, 1, 10) AS DATE) AS rental_date,  -- Extract first 10 chars (yyyy-mm-dd)
          SAFE_CAST(SUBSTR(return_date, 1, 10) AS DATE) AS return_date  -- Extract first 10 chars (yyyy-mm-dd)
        FROM `dwhproject-460111.PixelPlay.Rental`;
        """,
        use_legacy_sql=False
    )

    create_dim_store = BigQueryExecuteQueryOperator(
        task_id='create_dim_store',
        sql="""
        CREATE OR REPLACE TABLE `dwhproject-460111.PixelPlay.DimStore` AS
        SELECT
          s.store_id,
          s.address_id,
          i.inventory_id,                -- Added to match schema
          fc.film_id,                     -- Added to match schema
          r.rental_id,                   -- Added to match schema
          r.customer_id,                 -- Added to match schema
          c.category_id,                 -- Added to match schema
          c.name AS category_name   -- Added to match schema
        FROM `dwhproject-460111.PixelPlay.Store` s
        JOIN `dwhproject-460111.PixelPlay.Inventory` i ON s.store_id = i.store_id
        JOIN `dwhproject-460111.PixelPlay.Rental` r ON i.inventory_id = r.inventory_id
        JOIN `dwhproject-460111.PixelPlay.Film_Category` fc ON i.film_id = fc.film_id
        JOIN `dwhproject-460111.PixelPlay.Category` c ON fc.category_id = c.category_id;
        """,
        use_legacy_sql=False
    )

    create_fact_table = BigQueryExecuteQueryOperator(
      task_id='create_fact_table',
      sql="""
    CREATE OR REPLACE TABLE `dwhproject-460111.PixelPlay.FACTS_TABLE` AS
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
      FROM `dwhproject-460111.PixelPlay.DimPayment`  p
      JOIN `dwhproject-460111.PixelPlay.DimRental`   r
        ON r.customer_id = p.customer_id
       AND DATE(r.rental_date)   = DATE(p.payment_date)

      JOIN `dwhproject-460111.PixelPlay.Inventory`   i ON r.inventory_id = i.inventory_id
      JOIN `dwhproject-460111.PixelPlay.Store`       s ON i.store_id     = s.store_id

      -- two-step geography join
      JOIN `dwhproject-460111.PixelPlay.Address`     a ON s.address_id   = a.address_id
      JOIN `dwhproject-460111.PixelPlay.DimLocation` l ON a.city_id      = l.city_id

      JOIN `dwhproject-460111.PixelPlay.Film_Category` fc ON i.film_id    = fc.film_id
      JOIN `dwhproject-460111.PixelPlay.Category`       c  ON fc.category_id = c.category_id
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
    """,
    use_legacy_sql=False,
)




    # ========================
    # Task Dependencies
    # ========================
    
    [create_dim_payment, create_dim_date, create_dim_location, 
     create_dim_rental, create_dim_store] >> create_fact_table