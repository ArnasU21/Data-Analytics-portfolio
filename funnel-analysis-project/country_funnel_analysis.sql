
WITH top_countries AS (

    SELECT
        country,
        COUNT(DISTINCT user_pseudo_id) AS user_count,

        RANK() OVER (
            ORDER BY COUNT(DISTINCT user_pseudo_id) DESC
        ) AS country_rank

    FROM
        `tc-da-1.turing_data_analytics.raw_events`

    WHERE
        event_name = 'session_start'

    GROUP BY
        country

),

top_3_countries AS (

    SELECT
        country

    FROM
        top_countries

    WHERE
        country_rank <= 3

),

funnel_events AS (

    SELECT
        re.country,
        re.user_pseudo_id,
        re.event_name,

        CASE
            WHEN re.event_name = 'page_view'        THEN 1
            WHEN re.event_name = 'view_item'        THEN 2
            WHEN re.event_name = 'add_to_cart'      THEN 3
            WHEN re.event_name = 'begin_checkout'   THEN 4
            WHEN re.event_name = 'add_payment_info' THEN 5
            WHEN re.event_name = 'purchase'         THEN 6
        END AS event_order

    FROM
        `tc-da-1.turing_data_analytics.raw_events` AS re

        INNER JOIN top_3_countries AS tc
            ON re.country = tc.country

    WHERE
        re.event_name IN (
            'page_view',
            'view_item',
            'add_to_cart',
            'begin_checkout',
            'add_payment_info',
            'purchase'
        )

),

country_funnel_counts AS (

    SELECT
        country,
        event_order,
        event_name,
        COUNT(DISTINCT user_pseudo_id) AS user_count

    FROM
        funnel_events

    GROUP BY
        country,
        event_order,
        event_name

)

SELECT
    country,
    event_order,
    event_name,
    user_count

FROM
    country_funnel_counts

ORDER BY
    country,
    event_order;