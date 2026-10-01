SELECT
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_id) AS active_customers,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(100.0 * SUM(profit) / SUM(revenue), 2) AS margin_pct,
    ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS aov
FROM v_order_lines;