
WITH funnel_events AS (

    SELECT
        user_pseudo_id,
        event_name,

        CASE
            WHEN event_name = 'page_view'        THEN 1
            WHEN event_name = 'view_item'        THEN 2
            WHEN event_name = 'add_to_cart'      THEN 3
            WHEN event_name = 'begin_checkout'   THEN 4
            WHEN event_name = 'add_payment_info' THEN 5
            WHEN event_name = 'purchase'         THEN 6
        END AS event_order

    FROM
        `tc-da-1.turing_data_analytics.raw_events`

    WHERE
        event_name IN (
            'page_view',
            'view_item',
            'add_to_cart',
            'begin_checkout',
            'add_payment_info',
            'purchase'
        )

),

funnel_counts AS (

    SELECT
        event_order,
        event_name,
        COUNT(DISTINCT user_pseudo_id) AS user_count

    FROM
        funnel_events

    GROUP BY
        event_order,
        event_name

)

SELECT
    event_order,
    event_name,
    user_count

FROM
    funnel_counts

ORDER BY
    event_order;