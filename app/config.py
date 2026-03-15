REPORTS = [
    {
        "name": "PaymentType_Sheet1",
        "spreadsheet": "Payment type",
        "worksheet": "Sheet1",
        "sql_file": "reports/payment_type_sheet1.sql",
        "data_columns": 4,
        "mode": "upsert",
        "key_columns": 2
    },
    {
        "name": "PaymentType_Sheet2",
        "spreadsheet": "Payment type",
        "worksheet": "Sheet2",
        "sql_file": "reports/payment_type_sheet2.sql",
        "data_columns": 4,
        "mode": "upsert",
        "key_columns": 2
    },
    {
        "name": "Analysis2_Main",
        "spreadsheet": "Analysis 2",
        "worksheet": "Analysis 2.csv",
        "sql_file": "reports/analysis2_main.sql",
        "data_columns": 10,
        "mode": "upsert",
        "key_columns": 2
    },
    {
        "name": "Analysis2_Engagement",
        "spreadsheet": "Analysis 2",
        "worksheet": "Engagement",
        "sql_file": "reports/analysis2_engagement.sql",
        "data_columns": 3,
        "mode": "upsert",
        "key_columns": 1
    },
    {
        "name": "OverallAnalysis_Sheet1",
        "spreadsheet": "Overall Analysis",
        "worksheet": "Sheet1",
        "sql_file": "reports/overall_analysis_sheet1.sql",
        "data_columns": 9,
        "mode": "upsert",
        "key_columns": 1
    },
    {
        "name": "OverallAnalysis_Sheet3",
        "spreadsheet": "Overall Analysis",
        "worksheet": "Sheet3",
        "sql_file": "reports/overall_analysis_sheet3.sql",
        "data_columns": 4,
        "mode": "upsert",
        "key_columns": 3
    }
]