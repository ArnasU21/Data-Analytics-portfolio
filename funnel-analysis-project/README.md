# Funnel Analysis Project

## Business Problem
An e-commerce company is experiencing low conversion rates and wants to understand where users drop off during the purchase journey.
Although traffic levels are high, only a small percentage of users complete a purchase. The business suspects that friction within the user journey — from product discovery to checkout — is limiting revenue growth.
The objective of this analysis is to evaluate user behavior across key funnel stages (page view → product view → add to cart → checkout → purchase), identify critical drop-off points, and uncover differences in performance across key markets (Canada, India, and the United States).
The findings will help the business optimize user experience, improve conversion rates, and make more effective marketing and product decisions.

## Tools Used
- SQL  
- Excel  

SQL was used as the primary data transformation layer, while Excel was used for visualization and final presentation of insights.

## 📊 Dashboard Preview

![image alt](https://github.com/ArnasU21/Data-Analytics-portfolio/blob/ed62d62f6aaebd078cc4b1ed2f37269614ab45c7/funnel-analysis-project/funnel_dashboard.png)

## 🔄 **Funnel Definition & Validation**

The funnel stages were defined based on a typical e-commerce user journey, where each event represents a key step toward completing a purchase.

- **page_view**  
  Represents the initial entry point where users land on the website.

- **view_item**  
  Indicates active engagement, where users explore specific products.

- **add_to_cart**  
  Shows clear purchase intent, as users select items they are interested in buying.

- **begin_checkout**  
  Marks the transition from browsing to the purchasing process.

- **add_payment_info**  
  Reflects high purchase intent, where users are close to completing the transaction.

- **purchase**  
  Final step representing successful conversion and revenue generation.

### 🧠 Validation

The selected stages form a logical and sequential progression from user entry to final conversion, aligning with standard e-commerce funnel frameworks.

Each step reflects an increasing level of user intent, enabling clear identification of drop-off points and performance bottlenecks across the funnel.

All events are ordered chronologically and consistently tracked across users, ensuring accurate funnel progression and comparability across different segments (e.g., countries).

## 📈 Key Insights

### 1. Significant early-stage drop-off limits overall conversion potential  
The largest reduction in users occurs between **page_view and view_item (~25–26%)**, indicating that a substantial portion of traffic does not progress beyond initial browsing.

This suggests that:
- Landing pages may not be sufficiently engaging or relevant
- Users may not quickly find products of interest
- Traffic quality (e.g., from marketing campaigns) may be misaligned with user intent

👉 **Impact:** Early-stage inefficiencies significantly reduce the pool of users entering the core purchase funnel, limiting total revenue potential.

---

### 2. Product engagement represents a critical bottleneck in the funnel  
The transition from **view_item to add_to_cart (~9%)** shows a notable decline, indicating that users who view products are not consistently converting into purchase intent.

This may point to:
- Suboptimal product page design (e.g., unclear value proposition, poor UX)
- Pricing or product-market fit issues
- Lack of trust signals (reviews, ratings, delivery information)

👉 **Impact:** Improving product engagement could unlock a disproportionately large increase in downstream conversions.

---

### 3. Strong mid-to-late funnel performance indicates high purchase intent among engaged users  
Drop-offs from **begin_checkout to purchase (~1–3%)** are relatively low compared to earlier stages.

This suggests that:
- Checkout flow is generally efficient
- Users entering checkout demonstrate strong intent to complete the purchase
- There are limited technical or UX barriers in the final steps

👉 **Impact:** The primary opportunity lies in increasing the number of users reaching checkout rather than optimizing the checkout process itself.

---

### 4. Overall conversion rate remains low, highlighting significant optimization potential  
The total conversion from **page_view to purchase (~1–2%)** indicates that only a small fraction of users complete the full journey.

👉 **Impact:** Even marginal improvements in early-stage conversion rates could lead to substantial revenue growth due to compounding effects across the funnel.

---

### 5. Geographic differences reveal opportunities for targeted optimization  
Funnel performance varies across **Canada, India, and the United States**, with some regions showing stronger progression through later stages.

- The **United States** demonstrates relatively stronger conversion efficiency
- **Canada** shows higher early-stage drop-offs
- **India** maintains moderate performance across stages

👉 **Impact:** Tailored strategies by region (e.g., localized UX, pricing, or marketing) could improve overall performance and maximize return on investment.

## 💡 Recommendations

### 1. Improve early-stage engagement to reduce initial drop-off  
Given the significant drop between **page_view and view_item**, efforts should focus on improving the effectiveness of landing and entry pages.

Recommended actions:
- Optimize landing page design for clarity and relevance
- Align marketing campaigns with user intent to attract higher-quality traffic
- Improve navigation and search functionality to help users quickly find relevant products

👉 **Expected outcome:** Increased progression into the funnel, expanding the pool of users with potential to convert.

---

### 2. Enhance product page experience to increase purchase intent  
The drop-off between **view_item and add_to_cart** suggests that product pages are not sufficiently converting interest into action.

Recommended actions:
- Improve product descriptions, images, and value propositions
- Introduce trust signals (customer reviews, ratings, guarantees)
- Test pricing strategies and promotional offers
- Conduct A/B testing on product page layouts and call-to-action placement

👉 **Expected outcome:** Higher add-to-cart rates, directly improving downstream conversion.

---

### 3. Maintain and monitor checkout performance while minimizing friction  
The relatively strong performance in later funnel stages indicates that the checkout process is effective but should still be monitored.

Recommended actions:
- Ensure checkout remains simple, fast, and mobile-friendly
- Offer multiple payment options to accommodate user preferences
- Continuously monitor for technical issues or drop-offs

👉 **Expected outcome:** Sustained high conversion rates among high-intent users.

---

### 4. Focus on scaling high-performing segments  
Given the variation in funnel performance across regions, the business should prioritize investment in top-performing markets while improving weaker ones.

Recommended actions:
- Increase marketing spend in high-converting regions (e.g., United States)
- Analyze successful patterns (UX, pricing, campaigns) and replicate them in other regions
- Localize user experience (currency, language, offers) for underperforming markets

👉 **Expected outcome:** Improved overall efficiency of marketing spend and higher return on investment.

---

### 5. Implement continuous funnel optimization and experimentation  
To sustainably improve performance, the business should adopt a data-driven optimization approach.

Recommended actions:
- Establish regular funnel performance tracking and reporting
- Run controlled experiments (A/B testing) on key funnel stages
- Set KPIs for each stage (e.g., add-to-cart rate, checkout completion rate)

👉 **Expected outcome:** Ongoing improvements in conversion rates and long-term revenue growth.

## Files
- SQL queries
- Excel dashboard
- Dashboard screenshots
