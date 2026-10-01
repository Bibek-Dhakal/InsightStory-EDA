-- Point-in-time churn: at each month end, the share of customers (who had ordered by then)
-- whose latest order is older than the churn window.
WITH order_days AS (
    SELECT DISTINCT customer_id, order_date
    FROM v_order_lines
),
month_ends AS (
    SELECT DISTINCT
        LEAST(LAST_DAY(CAST(DATE_TRUNC('month', order_date) AS DATE)), DATE '{{as_of_date}}') AS month_end
    FROM order_days
),
eligible AS (
    -- Warm-up: nobody can be lapsed until one churn window has passed since the first order.
    SELECT month_end
    FROM month_ends
    WHERE month_end >= (SELECT MIN(order_date) FROM order_days) + {{churn_days}}
),
state AS (
    SELECT
        e.month_end,
        o.customer_id,
        MAX(o.order_date) AS last_order_date
    FROM eligible e
    JOIN order_days o ON o.order_date <= e.month_end
    GROUP BY e.month_end, o.customer_id
),
monthly AS (
    SELECT
        month_end,
        COUNT(*) AS customers_seen,
        SUM(CASE WHEN DATE_DIFF('day', last_order_date, month_end) > {{churn_days}} THEN 1 ELSE 0 END) AS churned
    FROM state
    GROUP BY month_end
)
SELECT
    month_end,
    customers_seen,
    churned,
    ROUND(100.0 * churned / customers_seen, 2) AS churn_rate_pct,
    ROUND(
        100.0 * churned / customers_seen
        - 100.0 * LAG(churned) OVER (ORDER BY month_end) / LAG(customers_seen) OVER (ORDER BY month_end),
        2
    ) AS change_pp,
    ROUND(
        AVG(100.0 * churned / customers_seen) OVER (ORDER BY month_end ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),
        2
    ) AS churn_3m_avg_pct
FROM monthly
ORDER BY month_end;