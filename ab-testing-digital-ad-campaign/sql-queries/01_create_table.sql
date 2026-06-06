DROP TABLE IF EXISTS marketing_ab_test;

CREATE TABLE marketing_ab_test (
    row_index INTEGER,
    user_id INTEGER,
    test_group VARCHAR(10),
    converted BOOLEAN,
    total_ads INTEGER,
    most_ads_day VARCHAR(20),
    most_ads_hour INTEGER
);