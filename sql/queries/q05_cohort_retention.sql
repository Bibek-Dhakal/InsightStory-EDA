WITH first_orders AS (
    SELECT customer_id, DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM v_order_lines
    GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT customer_id, DATE_TRUNC('month', order_date) AS activity_month
    FROM v_order_lines
),
cohort_activity AS (
    SELECT
        f.cohort_month,
        DATE_DIFF('month', f.cohort_month, a.activity_month) AS month_index,
        COUNT(DISTINCT a.customer_id) AS active_customers
    FROM first_orders f
    JOIN activity a ON a.customer_id = f.customer_id
    GROUP BY f.cohort_month, month_index
)
SELECT
    cohort_month,
    month_index,
    active_customers,
    ROUND(
        100.0 * active_customers
        / FIRST_VALUE(active_customers) OVER (PARTITION BY cohort_month ORDER BY month_index),
        2
    ) AS retention_pct
FROM cohort_activity
WHERE month_index BETWEEN 0 AND 12
ORDER BY cohort_month, month_index;