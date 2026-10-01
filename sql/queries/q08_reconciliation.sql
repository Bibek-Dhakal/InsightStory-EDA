SELECT
    ROUND(SUM(oi.quantity * p.unit_price * (1 - oi.discount_pct)), 2) AS revenue_raw
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.status = 'completed';
