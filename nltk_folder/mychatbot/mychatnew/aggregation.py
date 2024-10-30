aggregation_functions = {
    "total": "SUM(Amount)",
    "average": "AVG(Amount)",
    "max": "MAX(Amount)",
    "min": "MIN(Amount)",
    # Add more as needed
}

aggregation_mappings = {
    "total": ["total", "sum", "spent"],
    "average": ["average", "mean"],
    "max": ["maximum", "most"],
    "min": ["minimum", "least"],
    # Add more as needed
}

def get_aggregation_function(user_input):
    """Identify the corresponding SQL aggregation function. Defaults to SUM if none found."""
    user_input = user_input.lower()
    for agg, keywords in aggregation_mappings.items():
        if any(keyword in user_input for keyword in keywords):
            return aggregation_functions[agg]
    return aggregation_functions["total"]  # Default to SUM if no keywords found
