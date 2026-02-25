WITH payment_status AS (
    SELECT 
        DATE(updated_at) AS payment_date,
        plan_code,
        amount,
        msisdn,
        CASE
            WHEN plan_code = '921465_P02' AND amount = 150 THEN 'FULLY SMS'
            WHEN plan_code = '921465_P02' AND amount > 150 THEN 'GREATER SMS'
            WHEN plan_code = '921465_P02' AND amount < 150 THEN 'PARTIAL SMS'
            WHEN plan_code = '921465_P01' AND amount = 300 THEN 'FULLY IVR'
            WHEN plan_code = '921465_P01' AND amount < 300 THEN 'PARTIAL IVR'
            WHEN plan_code = '921465_P03' AND amount = 200 THEN 'FULLY DR SUB'
            WHEN plan_code = '921465_P03' AND amount < 200 THEN 'PARTIAL DR SUB'
            WHEN plan_code = '921465_P04' AND amount = 1000 THEN 'OD1000'
            WHEN plan_code = '921465_P05' AND amount = 2000 THEN 'OD2000'
            WHEN plan_code = '921465_P06' AND amount = 3000 THEN 'OD3000'
        END AS payment_status
    FROM billing.icg_payments
    WHERE updated_at::DATE = CURRENT_DATE
    AND updated_at > '{{LAST_EXECUTION}}'
    AND status = 'SUCCESS'
)

SELECT 
    payment_date,
    payment_status,
    COUNT(DISTINCT msisdn) AS customers,
    SUM(amount) AS revenue_tsh
FROM payment_status
WHERE payment_status IS NOT NULL
GROUP BY payment_date, payment_status
ORDER BY payment_date, payment_status;