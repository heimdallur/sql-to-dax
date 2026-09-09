# Examples

## Simple Projection

SQL:

```sql
SELECT region FROM sales
```

DAX:

```dax
EVALUATE
SELECTCOLUMNS('sales', "region", 'sales'[region])
```

## Filtered Projection

SQL:

```sql
SELECT region FROM sales WHERE year = 2026
```

DAX:

```dax
EVALUATE
SELECTCOLUMNS(FILTER('sales', 'sales'[year] = 2026), "region", 'sales'[region])
```

## Grouped Aggregation With Limit

SQL:

```sql
SELECT region, SUM(revenue) AS total_revenue
FROM sales
WHERE year = 2026
GROUP BY region
ORDER BY total_revenue DESC
LIMIT 10
```

DAX:

```dax
EVALUATE
TOPN(10, SUMMARIZECOLUMNS('sales'[region], FILTER('sales', 'sales'[year] = 2026), "total_revenue", SUM('sales'[revenue])), [total_revenue], DESC)
```
