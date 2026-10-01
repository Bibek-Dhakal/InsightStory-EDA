SELECT
    c.channel,
    COUNT(*) AS customers,
    SUM(CASE WHEN r.recency_days > {{churn_days}} THEN 1 ELSE 0 END) AS churned,
    ROUND(100.0 * SUM(CASE WHEN r.recency_days > {{churn_days}} THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN r.frequency = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS one_time_pct,
    ROUND(AVG(r.monetary), 2) AS avg_revenue_per_customer
FROM v_rfm r
JOIN customers c ON c.customer_id = r.customer_id
GROUP BY c.channel
ORDER BY churn_rate_pct DESC;