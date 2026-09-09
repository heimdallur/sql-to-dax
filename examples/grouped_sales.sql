SELECT region, SUM(revenue) AS total_revenue
FROM sales
WHERE year = 2026
GROUP BY region
ORDER BY total_revenue DESC
LIMIT 10
