# Olist Customer Value & Retention Analysis

Advanced SQL and Power BI portfolio project analyzing customer value, revenue behavior, cohort performance, and customer segmentation using the Brazilian E-Commerce Public Dataset by Olist.

## Project Overview

This project analyzes Olist's Brazilian e-commerce marketplace data to understand how customers generate revenue over time, how strong repeat-purchase behavior is, and which customer groups drive the most business value.

The analysis goes beyond basic sales reporting. It focuses on customer-level analytics using SQL, cohort analysis, revenue-based customer lifetime value, RFM-style segmentation, and an executive Power BI dashboard.

## Business Objective

The main business question:

**How much value do customers generate after their first purchase, and which customer segments should Olist prioritize for retention and growth?**

Supporting questions:

- Which customer identifier should be used for customer-level analysis?
- How much revenue comes from delivered orders?
- Do customers return after their first purchase?
- Which segments generate the most revenue?
- Which states and product categories drive marketplace performance?
- What retention opportunities exist based on customer behavior?

## Tools Used

- PostgreSQL
- pgAdmin
- Power BI
- Excel
- SQL
- Kaggle Olist dataset

## Dataset

Dataset: Brazilian E-Commerce Public Dataset by Olist

The dataset contains approximately 100,000 orders from Brazilian marketplaces between 2016 and 2018. It includes customers, orders, payments, products, sellers, reviews, and location data.

Raw tables used:

- customers
- orders
- order_items
- order_payments
- order_reviews
- products
- sellers
- geolocation
- product_category_translation

## Project Workflow

### 1. Data Cleaning and EDA

The first step was validating the raw data before building customer analytics.

Key checks included:

- Table row counts
- Primary key uniqueness
- Customer ID logic
- Order-to-customer relationship checks
- Payment-to-order relationship checks
- Order status distribution
- Date range validation
- Monthly order volume
- Payment duplication risk

Important discovery:

`customer_id` is order-level, while `customer_unique_id` represents the real customer. Therefore, all cohort, LTV, and segmentation analysis uses `customer_unique_id`.

### 2. Cohort Revenue Analysis

Customers were grouped by the month of their first delivered purchase.

The cohort analysis measures:

- Monthly average revenue per original cohort customer
- Cumulative average revenue per original cohort customer
- Forecasted cumulative customer revenue

This was built in SQL and visualized in Excel as cohort heatmaps.

### 3. Customer Lifetime Value

Customer lifetime value was calculated as revenue-based LTV:

**Revenue LTV = total delivered-order payment value per customer**

This is revenue LTV, not profit LTV, because the dataset does not include cost or margin data.

### 4. Customer Segmentation

Customers were segmented using RFM-style logic adapted to the Olist dataset.

Segments:

- High Value Customers
- Repeat Buyers
- Recent One-Time Buyers
- Dormant One-Time Buyers
- Low Value One-Time Buyers

Because most Olist customers only purchase once, frequency scoring was adjusted using business logic instead of relying only on NTILE scoring.

### 5. Power BI Dashboard

The Power BI dashboard summarizes the business story through:

- Revenue KPIs
- Monthly revenue trend
- Revenue by state
- Revenue by product category
- Monthly orders and revenue trend
- Customer segment revenue
- Customer count by segment
- Average LTV by segment
- Segment value vs recency

## Key Metrics

| Metric | Value |
|---|---:|
| Total Revenue | R$15.38M |
| Delivered Orders | 96K |
| Unique Customers | 93K |
| Average Order Value | R$159.81 |
| Average Revenue LTV | R$165.15 |
| Median Revenue LTV | R$107.78 |
| Max Revenue LTV | R$13.66K |
| Repeat Buyer Segment % | 1.35% |

## Key Findings

### 1. Olist is heavily driven by first purchases

Most customer value is generated in Month 0, meaning customers generate most of their revenue at the time of their first purchase.

Incremental revenue after the first purchase is low, which suggests weak repeat-purchase behavior.

### 2. Repeat buyers are rare

The repeat buyer segment represents only about 1.35% of customers in the segmentation model.

This shows that Olist behaves more like an acquisition-driven marketplace than a strong retention-driven business.

### 3. High-value customers dominate revenue

High Value Customers represent about 20% of customers but generate more than 50% of revenue.

This makes them the most important customer group for revenue protection and retention strategy.

### 4. Most customers are one-time buyers

Recent One-Time Buyers and Dormant One-Time Buyers together make up the largest share of customers.

This means Olist has a major opportunity to improve second-purchase conversion.

### 5. Revenue is geographically concentrated

Sao Paulo is the largest revenue-generating state, followed by Rio de Janeiro and Minas Gerais.

This concentration suggests that regional marketing, logistics, and seller strategy should be especially focused on high-revenue states.

### 6. Product category revenue is concentrated

Top categories such as health_beauty, watches_gifts, bed_bath_table, sports_leisure, and computers_accessories generate a large share of revenue.

These categories are strong candidates for deeper margin, repeat-purchase, and promotional analysis.

## Recommendations

### 1. Build a second-purchase strategy

Because repeat behavior is weak, Olist should focus on converting first-time buyers into second-time buyers.

Recommended actions:

- Post-purchase email campaigns
- Personalized product recommendations
- Category-specific discount offers
- Reorder reminders for repeatable categories
- Loyalty incentives after first delivery

### 2. Protect high-value customers

High Value Customers generate the majority of revenue, so they should receive priority attention.

Recommended actions:

- VIP retention campaigns
- Faster support handling
- Exclusive offers
- Early access to promotions
- Monitoring for churn risk

### 3. Segment one-time buyers by recency

Recent one-time buyers and dormant one-time buyers should not be treated the same.

Recommended actions:

- Recent One-Time Buyers: target with quick second-purchase incentives
- Dormant One-Time Buyers: use reactivation campaigns with stronger offers
- Low Value One-Time Buyers: use low-cost automated campaigns

### 4. Focus growth efforts on high-performing states

Sao Paulo, Rio de Janeiro, and Minas Gerais are the strongest revenue markets.

Recommended actions:

- Prioritize logistics improvements in top states
- Run state-level marketing campaigns
- Analyze delivery performance by state
- Expand seller partnerships in high-demand regions

### 5. Use cohort tracking as a retention KPI

Cohort revenue shows that post-first-purchase value grows slowly.

Recommended actions:

- Track Month 1 and Month 2 repeat revenue
- Monitor cumulative revenue per cohort
- Compare new cohorts after retention campaigns
- Use cohort analysis to measure whether customer quality is improving

## Main Business Conclusion

Olist's customer base is large, but customer retention is weak. Revenue is mostly generated through first purchases, while repeat purchasing contributes relatively little.

The biggest business opportunity is not only acquiring more customers, but increasing the number of customers who make a second purchase.

A successful retention strategy focused on high-value customers and recent one-time buyers could improve long-term customer value and reduce dependence on constant new customer acquisition.

## Repository Structure

```text
olist-customer-value-retention-analysis/
|-- README.md
|-- sql/
|   |-- 01_data_cleaning_and_eda.sql
|   |-- 02_customer_cohort_retention.sql
|   |-- 03_customer_lifetime_value.sql
|   |-- 04_customer_segmentation_rfm.sql
|   `-- 05_powerbi_dashboard_queries.sql
|-- docs/
|   |-- data_dictionary.md
|   `-- dashboard_build_notes.md
|-- reports/
|   |-- powerbi/
|   |   `-- olist_customer_value_dashboard.pbix
|   `-- excel/
|       `-- olist_ltv_cohort_analysis.xlsx
`-- data/
    `-- raw/
