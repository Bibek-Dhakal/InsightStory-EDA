-- Recency score 5 = most recent buyers; Frequency / Monetary score 5 = highest.
CREATE OR REPLACE VIEW v_rfm AS
WITH base AS (
    SELECT
        customer_id,
        DATE_DIFF('day', MAX(order_date), DATE '{{as_of_date}}') AS recency_days,
        COUNT(DISTINCT order_id) AS frequency,
        ROUND(SUM(revenue), 2) AS monetary,
        ROUND(SUM(profit), 2) AS profit
    FROM v_order_lines
    GROUP BY customer_id
),
scored AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC, monetary ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM base
)
SELECT
    *,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New / Promising'
        WHEN r_score = 3 THEN 'Needs Attention'
        ELSE 'Hibernating'
    END AS segment
FROM scored;