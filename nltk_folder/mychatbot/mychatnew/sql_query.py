from conditions import platform_mapping, category_mapping  # Import mappings

def construct_sql_query(conditions):
    query = "SELECT "

    # Select the aggregation function if provided, otherwise select all columns
    query += f"{conditions.get('aggregation', '*')} " if 'aggregation' in conditions else "* "
    query += "FROM my_transactions WHERE "

    # Initialize a list to hold the condition clauses
    condition_clauses = []

    # Helper function to match platforms or categories
    def match_conditions(input_list, mapping):
        matched_keys = []
        for item in input_list:
            for key, keywords in mapping.items():
                if any(keyword.lower() in item.lower() for keyword in keywords):
                    matched_keys.append(key)
                    break  # Stop searching once a match is found
        return matched_keys

    # Platform matching logic with IN clause for multiple platforms
    if 'platform' in conditions and len(conditions['platform']) > 0 :
        platforms = conditions['platform']
        matched_platforms = match_conditions(platforms, platform_mapping)

        if matched_platforms:
            condition_clauses.append(f"Platform IN ({', '.join(f'\'{p}\'' for p in matched_platforms)})")

    # Category matching logic with IN clause for multiple categories
    if 'category' in conditions and len(conditions['category']) > 0:
        categories = conditions['category']
        matched_categories = match_conditions(categories, category_mapping)

        if matched_categories:
            condition_clauses.append(f"Category IN ({', '.join(f'\'{c}\'' for c in matched_categories)})")

    # Add spent filter using the Notes column
    if 'is_credit' in conditions and conditions['is_credit'] is not None:
        condition_clauses.append("Notes = 'Credit'" if conditions['is_credit'] else "Notes = 'Debit'")
    
    # Add date range condition if specified
    if 'date_range' in conditions and conditions['date_range'] is not None:
        condition_clauses.append(f"Date >= '{conditions['date_range']}'")

    # Add payment method condition if specified
    if 'payment_method' in conditions and conditions['payment_method'] is not None:
        condition_clauses.append(f"Payment_Method = '{conditions['payment_method'].lower()}'")

    # Combine conditions
    if condition_clauses:
        query += " AND ".join(condition_clauses)
    else:
        query = query[:-7]  # Remove the last ' WHERE ' if no conditions

    return query
