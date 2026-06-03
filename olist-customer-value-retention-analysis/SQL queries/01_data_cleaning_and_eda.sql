-- =========================================================
-- 01_data_cleaning_and_eda_postgresql.sql
-- Project: Olist E-Commerce Advanced SQL Customer Analytics
-- Focus: Cohort retention, customer lifetime value, and RFM analysis
-- Purpose: Validate table sizes, key uniqueness, customer ID logic,
--          customer/order relationships, order status, date coverage,
--          monthly volume, and payment duplication risk.
-- Database: PostgreSQL
-- =========================================================


-- 1. Row counts by table
-- Purpose: confirm that all imported tables loaded successfully.
-- Expected result: row counts should match the imported Olist CSV files.
-- Finding: all 9 Olist tables imported successfully; row counts range from 71 category translation rows to 1,000,163 geolocation rows.
--------------------------------------------------------------------------------------------------------------------------------------

SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_payments', COUNT(*) FROM order_payments
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'order_reviews', COUNT(*) FROM order_reviews
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sellers', COUNT(*) FROM sellers
UNION ALL
SELECT 'geolocation', COUNT(*) FROM geolocation
UNION ALL
SELECT 'product_category_translation', COUNT(*) FROM product_category_translation
ORDER BY
    row_count;


-- 2. Primary key validation: orders table
-- Purpose: confirm that order_id uniquely identifies each row in the orders table.
-- Expected result: duplicate_order_id_rows should be 0.
-- Finding: 99,441 rows, 99,441 distinct order_ids, 0 duplicate order_id rows.
--------------------------------------------------------------------------------

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_id) AS distinct_order_ids,
    COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_order_id_rows
FROM orders;


-- 3. Primary key validation: customers table
-- Purpose: confirm that customer_id uniquely identifies each row in the customers table.
-- Expected result: duplicate_customer_id_rows should be 0.
-- Finding: 99,441 rows, 99,441 distinct customer_ids, 0 duplicate customer_id rows.
-------------------------------------------------------------------------------------

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT customer_id) AS distinct_customer_ids,
    COUNT(*) - COUNT(DISTINCT customer_id) AS duplicate_customer_id_rows
FROM customers;


-- 4. Customer ID logic: repeat customer check
-- Purpose: distinguish order-level customer_id from customer_unique_id.
-- Business use: customer_unique_id should be used for cohort retention, LTV, and RFM analysis.
-- Finding: 99,441 customer rows, 96,096 unique real customers, 3,345 repeat customer rows.
------------------------------------------------------------------------------------------------

SELECT
    COUNT(*) AS total_customer_rows,
    COUNT(DISTINCT customer_unique_id) AS unique_real_customers,
    COUNT(*) - COUNT(DISTINCT customer_unique_id) AS repeat_customer_rows
FROM customers;


-- 5. Relationship validation: orders to customers
-- Purpose: confirm that every order has a matching customer record.
-- Join choice: LEFT JOIN keeps all rows from orders and exposes missing customer matches.
-- Expected result: orders_without_customer should be 0.
-- Finding: 99,441 total orders, 99,441 matched customer records, 0 orders without a matching customer.
---------------------------------------------------------------------------------------------------------

SELECT
    COUNT(*) AS total_orders,
    COUNT(customers.customer_id) AS matched_customer_records,
    COUNT(*) - COUNT(customers.customer_id) AS orders_without_customer
FROM orders
LEFT JOIN customers
    ON orders.customer_id = customers.customer_id;


-- 6. Relationship validation: payments to orders
-- Purpose: confirm that every payment record belongs to a valid order.
-- Join choice: LEFT JOIN keeps all rows from payments and exposes missing order matches.
-- Expected result: payments_without_order should be 0.
-- Finding: 103,886 total payment records, 103,886 matched order records, 0 payments without a matching order.
------------------------------------------------------------------------------------------------------------

SELECT
    COUNT(*) AS total_payment_records,
    COUNT(orders.order_id) AS matched_order_records,
    COUNT(*) - COUNT(orders.order_id) AS payments_without_order
FROM order_payments AS payments
LEFT JOIN orders
    ON payments.order_id = orders.order_id;


-- 7. Order status distribution
-- Purpose: understand order lifecycle statuses and decide which orders should be included in revenue analysis.
-- Expected result: most orders should be delivered.
-- Finding: delivered orders make up 96,478 of 99,441 orders, or 97.02%; future revenue analysis should focus on delivered orders.
----------------------------------------------------------------------------------------------------------------------------------

SELECT
    order_status,
    COUNT(*) AS order_count,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS pct_of_orders
FROM orders
GROUP BY
    order_status
ORDER BY
    order_count DESC;


-- 8. Dataset date range
-- Purpose: identify time coverage before cohort retention, LTV, and RFM analysis.
-- Expected result: dataset should cover enough months to support time-based customer analysis.
-- Finding: orders span from 2016-09-04 to 2018-10-17 across 25 active order months.
-------------------------------------------------------------------------------------

SELECT
    MIN(order_purchase_timestamp::DATE) AS first_order_date,
    MAX(order_purchase_timestamp::DATE) AS last_order_date,
    COUNT(DISTINCT DATE_TRUNC('month', order_purchase_timestamp)) AS active_order_months
FROM orders;


-- 9. Monthly order volume
-- Purpose: inspect order volume by month and identify partial or sparse months before cohort analysis.
-- Expected result: first and last months may have unusually low volume because they are partial months.
-- Finding: early and final monthly order volume is sparse; stable monthly volume runs mainly from 2017-01 through 2018-08.
----------------------------------------------------------------------------------------------------------------------------

SELECT
    TO_CHAR(DATE_TRUNC('month', order_purchase_timestamp), 'YYYY-MM') AS order_month,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'delivered'
    ) AS delivered_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE order_status = 'delivered'
        ) / COUNT(*),
        2
    ) AS delivered_order_pct
FROM orders
GROUP BY
    DATE_TRUNC('month', order_purchase_timestamp)
ORDER BY
    DATE_TRUNC('month', order_purchase_timestamp);


-- 9a. Monthly order volume outlier validation
-- Purpose: validate sparse early and final months using a calendar month spine.
-- Expected result: 2016-11 should appear with 0 orders; early and final edge months should have very low order counts.
-- Finding: 2016-11 has 0 orders; 2016-09, 2016-12, 2018-09, and 2018-10 are sparse edge months.
------------------------------------------------------------------------------------------------------------------------

WITH month_spine AS (
    SELECT
        GENERATE_SERIES(
            DATE '2016-09-01',
            DATE '2018-10-01',
            INTERVAL '1 month'
        )::DATE AS calendar_month
),

monthly_orders AS (
    SELECT
        DATE_TRUNC('month', order_purchase_timestamp)::DATE AS order_month,
        COUNT(*) AS total_orders,
        COUNT(*) FILTER (
            WHERE order_status = 'delivered'
        ) AS delivered_orders
    FROM orders
    GROUP BY
        DATE_TRUNC('month', order_purchase_timestamp)::DATE
)

SELECT
    TO_CHAR(month_spine.calendar_month, 'YYYY-MM') AS calendar_month,
    COALESCE(monthly_orders.total_orders, 0) AS total_orders,
    COALESCE(monthly_orders.delivered_orders, 0) AS delivered_orders
FROM month_spine
LEFT JOIN monthly_orders
    ON month_spine.calendar_month = monthly_orders.order_month
ORDER BY
    month_spine.calendar_month;


-- 10. Payment records per order
-- Purpose: check whether orders can have zero, one, or multiple payment records before using payments for LTV and monetary analysis.
-- Join choice: LEFT JOIN keeps all orders and exposes orders with no payment record.
-- Expected result: most orders should have one payment record, but some may have multiple records and very few should have none.
-- Finding: 1 order has no payment record; 96,479 orders have one payment record; 2,961 orders have multiple payment records.
--------------------------------------------------------------------------------------------------------------------------------

WITH payment_records_per_order AS (
    SELECT
        orders.order_id,
        orders.order_status,
        COUNT(payments.order_id) AS payment_record_count
    FROM orders
    LEFT JOIN order_payments AS payments
        ON orders.order_id = payments.order_id
    GROUP BY
        orders.order_id,
        orders.order_status
)

SELECT
    payment_record_count,
    COUNT(*) AS order_count,
    COUNT(*) FILTER (
        WHERE order_status = 'delivered'
    ) AS delivered_order_count,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS pct_of_all_orders
FROM payment_records_per_order
GROUP BY
    payment_record_count
ORDER BY
    payment_record_count;