-- Monthly revenue cohort matrix
-- Purpose: measure average revenue generated per original cohort customer over time.
-- Business rule: cohort_month is based on each customer's first delivered purchase month.
-- Revenue rule: payment_value is aggregated at order level before joining to avoid payment-record duplication.
-- Metric: average revenue per original cohort customer, similar to the reference cohort table.
-- Display rule: cohort_month is shown as YYYY-MM, without a day.
-- Output rule: 0 means observed month with no revenue; NULL means the month is not observable yet.
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

clean_revenue_orders AS (
    SELECT
        customers.customer_unique_id,
        orders.order_id,
        DATE_TRUNC('month', orders.order_purchase_timestamp)::DATE AS order_month,
        payments_by_order.order_revenue
    FROM orders
    INNER JOIN customers
        ON orders.customer_id = customers.customer_id
    INNER JOIN payments_by_order
        ON orders.order_id = payments_by_order.order_id
    WHERE orders.order_status = 'delivered'
      AND orders.order_purchase_timestamp >= DATE '2017-01-01'
      AND orders.order_purchase_timestamp < DATE '2018-09-01'
),

customer_cohorts AS (
    SELECT
        customer_unique_id,
        MIN(order_month) AS cohort_month
    FROM clean_revenue_orders
    GROUP BY
        customer_unique_id
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(*) AS cohort_customers
    FROM customer_cohorts
    GROUP BY
        cohort_month
),

customer_revenue_by_month AS (
    SELECT
        customer_cohorts.customer_unique_id,
        customer_cohorts.cohort_month,
        clean_revenue_orders.order_month,
        (
            (
                EXTRACT(YEAR FROM clean_revenue_orders.order_month)::INTEGER
                - EXTRACT(YEAR FROM customer_cohorts.cohort_month)::INTEGER
            ) * 12
            +
            (
                EXTRACT(MONTH FROM clean_revenue_orders.order_month)::INTEGER
                - EXTRACT(MONTH FROM customer_cohorts.cohort_month)::INTEGER
            )
        ) AS months_since_first_purchase,
        clean_revenue_orders.order_revenue
    FROM customer_cohorts
    INNER JOIN clean_revenue_orders
        ON customer_cohorts.customer_unique_id = clean_revenue_orders.customer_unique_id
),

monthly_cohort_revenue AS (
    SELECT
        cohort_month,
        months_since_first_purchase,
        SUM(order_revenue) AS total_revenue
    FROM customer_revenue_by_month
    WHERE months_since_first_purchase BETWEEN 0 AND 19
    GROUP BY
        cohort_month,
        months_since_first_purchase
),

month_index AS (
    SELECT
        GENERATE_SERIES(0, 19) AS months_since_first_purchase
),

cohort_month_grid AS (
    SELECT
        cohort_sizes.cohort_month,
        cohort_sizes.cohort_customers,
        month_index.months_since_first_purchase,
        (
            cohort_sizes.cohort_month
            + (month_index.months_since_first_purchase || ' months')::INTERVAL
        )::DATE AS revenue_month
    FROM cohort_sizes
    CROSS JOIN month_index
),

cohort_average_revenue AS (
    SELECT
        cohort_month_grid.cohort_month,
        cohort_month_grid.cohort_customers,
        cohort_month_grid.months_since_first_purchase,
        CASE
            WHEN cohort_month_grid.revenue_month >= DATE '2018-09-01' THEN NULL
            ELSE ROUND(
                COALESCE(monthly_cohort_revenue.total_revenue, 0)
                / cohort_month_grid.cohort_customers,
                5
            )
        END AS avg_revenue_per_customer
    FROM cohort_month_grid
    LEFT JOIN monthly_cohort_revenue
        ON cohort_month_grid.cohort_month = monthly_cohort_revenue.cohort_month
       AND cohort_month_grid.months_since_first_purchase = monthly_cohort_revenue.months_since_first_purchase
)

SELECT
    TO_CHAR(cohort_month, 'YYYY-MM') AS cohort_month,
    cohort_customers,
    MAX(CASE WHEN months_since_first_purchase = 0 THEN avg_revenue_per_customer END) AS month_0_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 1 THEN avg_revenue_per_customer END) AS month_1_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 2 THEN avg_revenue_per_customer END) AS month_2_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 3 THEN avg_revenue_per_customer END) AS month_3_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 4 THEN avg_revenue_per_customer END) AS month_4_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 5 THEN avg_revenue_per_customer END) AS month_5_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 6 THEN avg_revenue_per_customer END) AS month_6_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 7 THEN avg_revenue_per_customer END) AS month_7_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 8 THEN avg_revenue_per_customer END) AS month_8_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 9 THEN avg_revenue_per_customer END) AS month_9_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 10 THEN avg_revenue_per_customer END) AS month_10_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 11 THEN avg_revenue_per_customer END) AS month_11_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 12 THEN avg_revenue_per_customer END) AS month_12_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 13 THEN avg_revenue_per_customer END) AS month_13_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 14 THEN avg_revenue_per_customer END) AS month_14_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 15 THEN avg_revenue_per_customer END) AS month_15_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 16 THEN avg_revenue_per_customer END) AS month_16_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 17 THEN avg_revenue_per_customer END) AS month_17_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 18 THEN avg_revenue_per_customer END) AS month_18_avg_revenue,
    MAX(CASE WHEN months_since_first_purchase = 19 THEN avg_revenue_per_customer END) AS month_19_avg_revenue
FROM cohort_average_revenue
GROUP BY
    cohort_month,
    cohort_customers
ORDER BY
    cohort_month;