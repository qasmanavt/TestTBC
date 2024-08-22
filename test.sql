WITH monthly_sales AS (
    SELECT 
        FORMAT(purchase_date, 'yyyy-MM') AS sales_month,
        SUM(p.price * st.quantity) AS total_sales,
        COUNT(st.transaction_id) AS total_transactions
    FROM 
        sales_transactions st
    JOIN 
        products p ON st.product_id = p.product_id
    GROUP BY 
        FORMAT(purchase_date, 'yyyy-MM')
),

moving_avg AS (
    SELECT 
        sales_month,
        total_sales,
        total_transactions,
        AVG(total_sales) OVER (ORDER BY sales_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_sales
    FROM 
        monthly_sales
)

SELECT 
    sales_month,
    total_sales,
    total_transactions,
    moving_avg_sales
FROM 
    moving_avg
ORDER BY 
    sales_month;
