"""Shared constants for the app."""

# EUR -> INR conversion. The source dataset (European_Bank.csv) reports
# Balance/EstimatedSalary in EUR; the dashboard displays everything in INR
# per project requirements. Rate is an approximate mid-market snapshot
# (mid-July 2026, ~₹110/EUR) — update this constant if a live rate is needed.
EUR_TO_INR_RATE = 110.0
