WITH acquisition AS (
    SELECT 
        created_at::DATE AS log_date,
        plan_code,
        COUNT(DISTINCT customer_msisdn) AS customers_acquired
    FROM subscription.subscribers
    WHERE created_at::DATE = CURRENT_DATE
    GROUP BY log_date, plan_code
),

payments AS (
    SELECT 
        created_at::DATE AS log_date,
        plan_code,
        COUNT(DISTINCT msisdn) AS customers_attempted,
        COUNT(DISTINCT CASE WHEN status = 'SUCCESS' THEN msisdn END) AS active_customers,
        COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) AS transactions,
        SUM(CASE WHEN status = 'SUCCESS' THEN amount ELSE 0 END) AS revenue
    FROM billing.icg_payments
    WHERE created_at::DATE = CURRENT_DATE
    AND updated_at > '{{LAST_EXECUTION}}'
    GROUP BY log_date, plan_code
),

churn AS (
    SELECT 
        updated_at::DATE AS log_date,
        unnest(plan_codes) AS plan_code,
        COUNT(DISTINCT customer_msisdn) AS churned_customers
    FROM subscription.churn_logs
    WHERE updated_at::DATE = CURRENT_DATE
    GROUP BY log_date, plan_code
),

new_subscribers_paid AS (
    SELECT 
        s.created_at::DATE AS log_date,
        s.plan_code,
        COUNT(DISTINCT s.customer_msisdn) AS paid_new_customers,
        SUM(p.amount) AS new_subscriber_revenue
    FROM subscription.subscribers s
    JOIN billing.icg_payments p 
      ON s.customer_msisdn = p.msisdn
     AND s.created_at::DATE = p.updated_at::DATE
     AND p.status = 'SUCCESS'
    WHERE s.created_at::DATE = CURRENT_DATE
    GROUP BY log_date, s.plan_code
)

SELECT 
    p.log_date,
    p.plan_code,
    COALESCE(a.customers_acquired, 0),
    COALESCE(p.customers_attempted, 0),
    COALESCE(p.active_customers, 0),
    COALESCE(p.transactions, 0),
    COALESCE(p.revenue, 0),
    COALESCE(nsp.paid_new_customers, 0),
    COALESCE(nsp.new_subscriber_revenue, 0),
    COALESCE(c.churned_customers, 0)
FROM payments p
LEFT JOIN acquisition a ON p.log_date = a.log_date AND p.plan_code = a.plan_code
LEFT JOIN new_subscribers_paid nsp ON p.log_date = nsp.log_date AND p.plan_code = nsp.plan_code
LEFT JOIN churn c ON p.log_date = c.log_date AND p.plan_code = c.plan_code
ORDER BY p.log_date, p.plan_code;