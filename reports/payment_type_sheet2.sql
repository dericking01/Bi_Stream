SELECT 
    DATE(updated_at) AS log_date,
    status,
    COUNT(DISTINCT msisdn) AS customers,
    COUNT(msisdn) AS transaction,
    SUM(amount) AS total_amount
FROM billing.icg_payments
WHERE updated_at::DATE = CURRENT_DATE
AND updated_at > '{{LAST_EXECUTION}}'
GROUP BY status, DATE(updated_at)
ORDER BY log_date, status;