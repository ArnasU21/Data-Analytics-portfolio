-- 1. Customer segmentation using RFM and revenue LTV
-- Purpose: segment customers by revenue value, repeat behavior, and recency.
-- Business rule: use customer_unique_id as the real customer identifier.
-- Revenue rule: aggregate payment_value at order level before joining to avoid payment-record duplication.
-- Order rule: use delivered orders only.
-- Join choice: INNER JOIN customers keeps valid customer orders; LEFT JOIN payments keeps delivered orders even if payment data is missing.
-- Missing payment rule: missing order revenue is treated as 0.
-- Analysis window: 2017-01-01 through 2018-08-31.
-- Frequency scoring rule: use business rules instead of NTILE because most Olist customers have only one delivered order.
-- Metric: revenue LTV, not profit LTV, because cost/margin data is not available.
-- Finding: add result after running.
------------------------------------------------------------------------------------------------------------------------------------------------

WITH payments_by_order AS (
    SELECT
        order_id,
        SUM(payment_value) AS order_revenue
    FROM order_payments
    GROUP BY
        order_id
),

clean_delivered_orders AS (
    SELECT
        customers.customer_unique_id,
        orders.order_id,
        orders.order_purchase_timestamp::DATE AS order_date,
        COALESCE(payments_by_order.order_revenue, 0) AS order_revenue
    FROM orders
    INNER JOIN customers
        ON orders.customer_id = customers.customer_id
    LEFT JOIN payments_by_order
        ON orders.order_id = payments_by_order.order_id
    WHERE orders.order_status = 'delivered'
      AND orders.order_purchase_timestamp >= DATE '2017-01-01'
      AND orders.order_purchase_timestamp < DATE '2018-09-01'
),

customer_metrics AS (
    SELECT
        customer_unique_id,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        DATE '2018-09-01' - MAX(order_date) AS recency_days,
        COUNT(DISTINCT order_id) AS delivered_order_count,
        ROUND(SUM(order_revenue), 2) AS revenue_ltv
    FROM clean_delivered_orders
    GROUP BY
        customer_unique_id
),

scored_customers AS (
    SELECT
        customer_unique_id,
        first_order_date,
        last_order_date,
        recency_days,
        delivered_order_count,
        revenue_ltv,
        NTILE(5) OVER (
            ORDER BY recency_days DESC
        ) AS recency_score,
        CASE
            WHEN delivered_order_count = 1 THEN 1
            WHEN delivered_order_count = 2 THEN 3
            ELSE 5
        END AS frequency_score,
        NTILE(5) OVER (
            ORDER BY revenue_ltv
        ) AS monetary_score
    FROM customer_metrics
),

customer_segments AS (
    SELECT
        customer_unique_id,
        first_order_date,
        last_order_date,
        recency_days,
        delivered_order_count,
        revenue_ltv,
        recency_score,
        frequency_score,
        monetary_score,
        CASE
            WHEN monetary_score = 5 THEN 'High Value Customers'
            WHEN delivered_order_count > 1 THEN 'Repeat Buyers'
            WHEN recency_score >= 4
                 AND delivered_order_count = 1 THEN 'Recent One-Time Buyers'
            WHEN recency_score <= 2
                 AND delivered_order_count = 1 THEN 'Dormant One-Time Buyers'
            ELSE 'Low Value One-Time Buyers'
        END AS customer_segment
    FROM scored_customers
)

SELECT
    customer_unique_id,
    first_order_date,
    last_order_date,
    recency_days,
    delivered_order_count,
    revenue_ltv,
    recency_score,
    frequency_score,
    monetary_score,
    customer_segment
FROM customer_segments
ORDER BY
    revenue_ltv DESC;


-- 2. Customer segment summary
-- Purpose: summarize segment size, revenue value, and order behavior for each customer segment.
-- Business rule: use the same segmentation logic as the customer-level segmentation table.
-- Metric: revenue LTV, not profit LTV, because cost/margin data is not available.
-- Finding: add result after running.
------------------------------------------------------------------------------------------------------------------------------------------------

WITH payments_by_order AS (
    SELECT
        order_id,
        SUM(payment_value) AS order_revenue
    FROM order_payments
    GROUP BY
        order_id
),

clean_delivered_orders AS (
    SELECT
        customers.customer_unique_id,
        orders.order_id,
        orders.order_purchase_timestamp::DATE AS order_date,
        COALESCE(payments_by_order.order_revenue, 0) AS order_revenue
    FROM orders
    INNER JOIN customers
        ON orders.customer_id = customers.customer_id
    LEFT JOIN payments_by_order
        ON orders.order_id = payments_by_order.order_id
    WHERE orders.order_status = 'delivered'
      AND orders.order_purchase_timestamp >= DATE '2017-01-01'
      AND orders.order_purchase_timestamp < DATE '2018-09-01'
),

customer_metrics AS (
    SELECT
        customer_unique_id,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        DATE '2018-09-01' - MAX(order_date) AS recency_days,
        COUNT(DISTINCT order_id) AS delivered_order_count,
        ROUND(SUM(order_revenue), 2) AS revenue_ltv
    FROM clean_delivered_orders
    GROUP BY
        customer_unique_id
),

scored_customers AS (
    SELECT
        customer_unique_id,
        first_order_date,
        last_order_date,
        recency_days,
        delivered_order_count,
        revenue_ltv,
        NTILE(5) OVER (
            ORDER BY recency_days DESC
        ) AS recency_score,
        CASE
            WHEN delivered_order_count = 1 THEN 1
            WHEN delivered_order_count = 2 THEN 3
            ELSE 5
        END AS frequency_score,
        NTILE(5) OVER (
            ORDER BY revenue_ltv
        ) AS monetary_score
    FROM customer_metrics
),

customer_segments AS (
    SELECT
        customer_unique_id,
        first_order_date,
        last_order_date,
        recency_days,
        delivered_order_count,
        revenue_ltv,
        recency_score,
        frequency_score,
        monetary_score,
        CASE
            WHEN monetary_score = 5 THEN 'High Value Customers'
            WHEN delivered_order_count > 1 THEN 'Repeat Buyers'
            WHEN recency_score >= 4
                 AND delivered_order_count = 1 THEN 'Recent One-Time Buyers'
            WHEN recency_score <= 2
                 AND delivered_order_count = 1 THEN 'Dormant One-Time Buyers'
            ELSE 'Low Value One-Time Buyers'
        END AS customer_segment
    FROM scored_customers
)

SELECT
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_customers,
    ROUND(SUM(revenue_ltv), 2) AS total_revenue_ltv,
    ROUND(100.0 * SUM(revenue_ltv) / SUM(SUM(revenue_ltv)) OVER (), 2) AS pct_of_revenue_ltv,
    ROUND(AVG(revenue_ltv), 2) AS avg_revenue_ltv,
    ROUND(AVG(delivered_order_count), 2) AS avg_delivered_orders,
    MIN(recency_days) AS min_recency_days,
    MAX(recency_days) AS max_recency_days
FROM customer_segments
GROUP BY
    customer_segment
ORDER BY
    total_revenue_ltv DESC;
    