-- 1. Customer lifetime value
-- Purpose: calculate revenue-based customer lifetime value for each real customer.
-- Business rule: use customer_unique_id as the real customer identifier.
-- Revenue rule: aggregate payment_value at order level before joining to avoid payment-record duplication.
-- Order rule: use delivered orders only.
-- Join choice: INNER JOIN customers keeps valid customer orders; LEFT JOIN payments keeps delivered orders even if payment data is missing.
-- Missing payment rule: missing order revenue is treated as 0 and can be audited separately.
-- Analysis window: 2017-01-01 through 2018-08-31.
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
        DATE_TRUNC('month', orders.order_purchase_timestamp)::DATE AS order_month,
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

customer_ltv AS (
    SELECT
        customer_unique_id,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        COUNT(DISTINCT order_id) AS delivered_order_count,
        ROUND(SUM(order_revenue), 2) AS revenue_ltv
    FROM clean_delivered_orders
    GROUP BY
        customer_unique_id
)

SELECT
    customer_unique_id,
    first_order_date,
    last_order_date,
    delivered_order_count,
    revenue_ltv
FROM customer_ltv
ORDER BY
    revenue_ltv DESC;


-- 2. Customer lifetime value summary
-- Purpose: summarize customer-level revenue LTV into portfolio-ready business metrics.
-- Business rule: use customer_unique_id as the real customer identifier.
-- Revenue rule: revenue_ltv is total delivered-order revenue per customer.
-- Repeat rule: repeat customers have more than one delivered order.
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

customer_ltv AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS delivered_order_count,
        ROUND(SUM(order_revenue), 2) AS revenue_ltv
    FROM clean_delivered_orders
    GROUP BY
        customer_unique_id
)

SELECT
    COUNT(*) AS total_customers,
    ROUND(AVG(revenue_ltv), 2) AS avg_revenue_ltv,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY revenue_ltv)::NUMERIC, 2) AS median_revenue_ltv,
    ROUND(MAX(revenue_ltv), 2) AS max_revenue_ltv,
    COUNT(*) FILTER (WHERE delivered_order_count > 1) AS repeat_customers,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE delivered_order_count > 1) / COUNT(*),
        2
    ) AS repeat_customer_pct,
    ROUND(
        AVG(revenue_ltv) FILTER (WHERE delivered_order_count = 1),
        2
    ) AS avg_one_time_customer_ltv,
    ROUND(
        AVG(revenue_ltv) FILTER (WHERE delivered_order_count > 1),
        2
    ) AS avg_repeat_customer_ltv
FROM customer_ltv;
