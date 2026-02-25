WITH acquisition AS (
    SELECT 
        created_at::DATE AS log_date,
        COUNT(DISTINCT customer_msisdn) AS customers_acquired
    FROM subscription.subscribers
    WHERE created_at::DATE = CURRENT_DATE
    GROUP BY log_date
),

payments AS (
    SELECT 
        created_at::DATE AS log_date,
        COUNT(DISTINCT msisdn) AS customers_attempted,
        COUNT(DISTINCT CASE WHEN status = 'SUCCESS' THEN msisdn END) AS active_customers,
        COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) AS transactions,
        SUM(CASE WHEN status = 'SUCCESS' THEN amount ELSE 0 END) AS revenue
    FROM billing.icg_payments
    WHERE created_at::DATE = CURRENT_DATE
    AND updated_at > '{{LAST_EXECUTION}}'
    GROUP BY log_date
),

churn AS (
    SELECT 
        updated_at::DATE AS log_date,
        COUNT(DISTINCT customer_msisdn) AS churned_customers
    FROM subscription.churn_logs
    WHERE updated_at::DATE = CURRENT_DATE
    GROUP BY log_date
)

SELECT 
    p.log_date,
    COALESCE(a.customers_acquired, 0),
    COALESCE(p.customers_attempted, 0),
    COALESCE(p.active_customers, 0),
    COALESCE(p.transactions, 0),
    COALESCE(p.revenue, 0),
    COALESCE(c.churned_customers, 0)
FROM payments p
LEFT JOIN acquisition a ON p.log_date = a.log_date
LEFT JOIN churn c ON p.log_date = c.log_date
ORDER BY p.log_date;