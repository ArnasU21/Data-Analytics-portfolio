-- Checks total rows
SELECT COUNT(*) AS total_rows
FROM marketing_ab_test;


-- Checks experiment group sizes
SELECT
    test_group,
    COUNT(*) AS users
FROM marketing_ab_test
GROUP BY test_group
ORDER BY test_group;


-- Main A/B test conversion summary
SELECT
    test_group,
    COUNT(*) AS total_users,
    SUM(converted::int) AS conversions,
    ROUND(AVG(converted::int) * 100, 2) AS conversion_rate_pct
FROM marketing_ab_test
GROUP BY test_group
ORDER BY test_group;


-- Absolute and relative lift
WITH group_metrics AS (
    SELECT
        test_group,
        COUNT(*) AS total_users,
        SUM(converted::int) AS conversions,
        AVG(converted::int) AS conversion_rate
    FROM marketing_ab_test
    GROUP BY test_group
),
pivoted AS (
    SELECT
        MAX(CASE WHEN test_group = 'ad' THEN conversion_rate END) AS ad_conversion_rate,
        MAX(CASE WHEN test_group = 'psa' THEN conversion_rate END) AS psa_conversion_rate
    FROM group_metrics
)
SELECT
    ROUND(ad_conversion_rate * 100, 2) AS ad_conversion_rate_pct,
    ROUND(psa_conversion_rate * 100, 2) AS psa_conversion_rate_pct,
    ROUND((ad_conversion_rate - psa_conversion_rate) * 100, 2) AS absolute_lift_pct_points,
    ROUND(((ad_conversion_rate - psa_conversion_rate) / psa_conversion_rate) * 100, 2) AS relative_lift_pct
FROM pivoted;


-- Conversion rate by most active ad day
SELECT
    most_ads_day,
    test_group,
    COUNT(*) AS total_users,
    SUM(converted::int) AS conversions,
    ROUND(AVG(converted::int) * 100, 2) AS conversion_rate_pct
FROM marketing_ab_test
GROUP BY most_ads_day, test_group
ORDER BY most_ads_day, test_group;


-- Conversion rate by most active ad hour
SELECT
    most_ads_hour,
    test_group,
    COUNT(*) AS total_users,
    SUM(converted::int) AS conversions,
    ROUND(AVG(converted::int) * 100, 2) AS conversion_rate_pct
FROM marketing_ab_test
GROUP BY most_ads_hour, test_group
ORDER BY most_ads_hour, test_group;


-- Conversion rate by ad exposure bucket
SELECT
    CASE
        WHEN total_ads BETWEEN 0 AND 10 THEN '0-10 ads'
        WHEN total_ads BETWEEN 11 AND 50 THEN '11-50 ads'
        WHEN total_ads BETWEEN 51 AND 100 THEN '51-100 ads'
        WHEN total_ads BETWEEN 101 AND 200 THEN '101-200 ads'
        ELSE '201+ ads'
    END AS ad_exposure_bucket,
    test_group,
    COUNT(*) AS total_users,
    SUM(converted::int) AS conversions,
    ROUND(AVG(converted::int) * 100, 2) AS conversion_rate_pct
FROM marketing_ab_test
GROUP BY ad_exposure_bucket, test_group
ORDER BY ad_exposure_bucket, test_group;