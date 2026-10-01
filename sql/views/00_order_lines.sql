CREATE OR REPLACE VIEW v_order_lines AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    c.region,
    c.channel,
    p.product_id,
    p.category,
    oi.quantity,
    oi.discount_pct,
    oi.quantity * p.unit_price * (1 - oi.discount_pct) AS revenue,
    oi.quantity * p.unit_cost AS cost,
    oi.quantity * p.unit_price * (1 - oi.discount_pct) - oi.quantity * p.unit_cost AS profit
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status = 'completed';
