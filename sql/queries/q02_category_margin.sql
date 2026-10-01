SELECT
    category,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(100.0 * SUM(profit) / SUM(revenue), 2) AS margin_pct,
    ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 2) AS revenue_share_pct,
    ROUND(100.0 * AVG(discount_pct), 2) AS avg_discount_pct,
    RANK() OVER (ORDER BY SUM(profit) DESC) AS profit_rank
FROM v_order_lines
GROUP BY category
ORDER BY SUM(profit) DESC;
