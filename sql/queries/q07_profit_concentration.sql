WITH cust AS (
    SELECT customer_id, SUM(profit) AS profit
    FROM v_order_lines
    GROUP BY customer_id
),
ranked AS (
    SELECT customer_id, profit, NTILE(10) OVER (ORDER BY profit DESC) AS decile
    FROM cust
)
SELECT
    decile,
    COUNT(*) AS customers,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(100.0 * SUM(profit) / SUM(SUM(profit)) OVER (), 2) AS profit_share_pct,
    ROUND(100.0 * SUM(SUM(profit)) OVER (ORDER BY decile) / SUM(SUM(profit)) OVER (), 2) AS cumulative_profit_pct
FROM ranked
GROUP BY decile
ORDER BY decile;