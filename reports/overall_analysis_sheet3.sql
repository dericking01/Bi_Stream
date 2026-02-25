SELECT 
    DATE(updated_at) AS log_date,
    plan,
    churn_type,
    COUNT(DISTINCT customer_msisdn) AS unique_customers
FROM (
    SELECT 
        customer_msisdn,
        updated_at,
        churn_type,
        unnest(plan_codes) AS plan
    FROM subscription.churn_logs
    WHERE updated_at::DATE = CURRENT_DATE
    AND updated_at > '{{LAST_EXECUTION}}'
) subquery
GROUP BY log_date, plan, churn_type
ORDER BY log_date, plan, churn_type;