# Shutterfly-Customer-Lifetime-Value
Coding challenge from shutterfly.

# Overview
Calculate simple LTV using equation: 52(a) x t. t is 10 years here. a = customer expenditures per visit (USD) x number of site visits per week. A customer's expenditures is the sum of all expenditures of this customer, and the time of visit can be extracted from all his/her visit events. The timeframe is calculated by substracting the earliest time from the latest time, which are recorded from all event times.

# Input
The input data should be provided in a file named input.txt

# Output
The output is generated in a file named output.txt and contains the top x customers with the highest Simple LTV, where x is the specified value. Each line in the output file corresponds to a customer and includes their ID and calculated Simple LTV value

# Design

- ingest(): This function ingests an event and updates the LTV of the corresponding customer.
- calculate_avg_weekly_expenditure(): This function calculates the average weekly expenditure of a customer. 
- calculate_top_x_ltv_customers(): This function calculates the top x customers with the highest LTV. Takes O(nlogn) time complexity
