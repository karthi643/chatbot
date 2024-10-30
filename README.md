# Creating the README.txt content for the offline ChatGPT project.
readme_content = """
# Offline ChatGPT for Bank Transaction Analysis

## Overview

This project implements an offline ChatGPT model designed to analyze and answer questions regarding personal bank transaction records. The model utilizes a local SQLite database containing six months of transaction data, including expenses and income from various platforms. The goal is to provide insights into spending habits and income sources through natural language queries.

## Features

- Transaction Analysis: Answer questions about specific spending categories (e.g., food, shopping) and platforms (e.g., Swiggy, Amazon).
- Trend Analysis: Determine whether spending is increasing or decreasing over time.
- Flexible Queries: Supports aggregation functions such as `min`, `max`, `avg`, `total`, `top`, and `least`.
- Contextual Understanding: Utilizes TextBlob or similar tools to identify the context of queries as related to income or expenses.

## Database Structure

The SQLite database (`my_database.db`) contains a table named `my_transactions` with the following columns:

- Date (TEXT): Date of the transaction (formatted as `YYYY-MM-DD`).
- Transaction ID (TEXT): Unique identifier for each transaction (e.g., `TX{10000 + i}`).
- Description (TEXT): Description of the transaction (e.g., `{platform} Transaction`).
- Platform (TEXT): The platform where the transaction occurred (e.g., Swiggy, Amazon).
- Category (TEXT): Type of expense or income (e.g., Food, Transport).
- Amount (REAL): Amount of the transaction (negative for expenses, positive for income).
- Payment Method (TEXT): Method used for the transaction (e.g., Card, Online Transfer).
- Balance (REAL): Account balance after the transaction.
- Notes (TEXT): Additional notes about the transaction (e.g., Spent, Income).


