WITH params AS (
    SELECT CURRENT_DATE AS report_date
),

engagement AS (
    SELECT 
        p.report_date AS date,
        COUNT(DISTINCT SUBSTRING(ch.session_id FROM '^([0-9]+)')) AS unique_customers
    FROM chat.chat_history ch
    CROSS JOIN params p
    WHERE ch.session_id ~ '[0-9]{2}-[0-9]{2}-[0-9]{4}'
    AND to_date(
        SUBSTRING(ch.session_id FROM '([0-9]{2}-[0-9]{2}-[0-9]{4})'),
        'DD-MM-YYYY'
    ) = p.report_date
    GROUP BY p.report_date
),

active_base AS (
    SELECT 
        p.report_date AS date,
        COUNT(DISTINCT b.msisdn) AS active_customers
    FROM billing.icg_payments b
    CROSS JOIN params p
    WHERE b.plan_code = '921465_P02'
    AND b.updated_at::DATE = p.report_date
    AND b.status = 'SUCCESS'
    GROUP BY p.report_date
)

SELECT 
    e.date,
    e.unique_customers,
    a.active_customers,
    ROUND(
        e.unique_customers::NUMERIC / NULLIF(a.active_customers, 0),
        4
    ) AS engagement_rate
FROM engagement e
LEFT JOIN active_base a ON e.date = a.date;