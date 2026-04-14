SELECT * FROM sales;

SELECT DISTINCT customer_id, region
FROM sales
ORDER BY region;

SELECT a.order_id, b.customer_name
FROM orders a
JOIN customers b;

SELECT product_id, SUM(amount) AS revenue
FROM sales
GROUP BY product_id;
