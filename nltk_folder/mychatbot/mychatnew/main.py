import sqlite3
import re
from preprocess import preprocess_text
from aggregation import get_aggregation_function
from conditions import extract_conditions, platform_mapping,category_mapping
from sql_query import construct_sql_query

def generate_sql_query(natural_text):
    pos_tags = preprocess_text(natural_text)
    conditions = extract_conditions(pos_tags)
    sql_query = construct_sql_query(conditions)
    return sql_query

def filter_query_conditions_from_db(sql_query):
    """
    Extract WHERE conditions from the generated query and validate each condition against the database records.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect('nltk_folder/mychatbot/my_database.db')
    cursor = conn.cursor()

    # Extract WHERE clause using regular expressions
    where_clause_match = re.search(r"WHERE (.+)", sql_query, re.IGNORECASE)
    if not where_clause_match:
        conn.close()
        return None  # No WHERE clause, nothing to filter

    # Get the WHERE conditions as a string
    where_conditions = where_clause_match.group(1)

    # Split the conditions by AND (considering potential spacing around AND)
    conditions_list = re.split(r"\s+AND\s+", where_conditions, flags=re.IGNORECASE)

    # Loop through each condition to check if it matches existing records
    for condition in conditions_list:
        # Extract column and value from each condition (simple assumption for "column = 'value'" format)
        condition_match = re.match(r"(\w+)\s*=\s*'([^']+)'", condition)
        if condition_match:
            column_name, value = condition_match.groups()
            
            # Check if the value exists in the corresponding column in the database
            cursor.execute(f"SELECT COUNT(*) FROM my_transactions WHERE {column_name} = ?", (value,))
            count = cursor.fetchone()[0]

            if count == 0:  # No matches found for this condition
                conn.close()
                return f"No matching records found for condition: {column_name} = '{value}'"

    # If all conditions match records in the database
    conn.close()
    return "All conditions matched"

def execute_query(query):
    # Use filter function to check if the WHERE conditions in the query are valid
    filter_result = filter_query_conditions_from_db(query)

    # If filtering indicates no matching records, return the feedback
    if filter_result != "All conditions matched":
        return filter_result

    # Connect to the SQLite database and execute the final query
    conn = sqlite3.connect('nltk_folder/mychatbot/my_database.db')
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        return f"Database error occurred: {e}"
    finally:
        conn.close()
    
    # Check if results are empty and handle accordingly
    if not results:
        return "No spending found in this category."  # Message for no matching records
    
    return results

if __name__ == "__main__":
    print("Welcome to the Transaction Chatbot!")
    print("You can ask about your spending, income, or any transaction-related queries.")
    print("Type 'exit' to quit the chatbot.\n")

    while True:
        text = input("Please enter your query: ")
        
        if text.lower() == 'exit':
            print("Exiting the chatbot. Goodbye!")
            break  # Exit the loop

        # Validate the input
        if not text.strip():
            print("Please enter a valid query.")
            continue

        sql_query = generate_sql_query(text)
        print("Generated SQL Query:", sql_query)  # Debugging: Print the generated SQL query
        #check= filter_query_conditions_from_db(sql_query)
        # Execute the query
        results = execute_query(sql_query)
        
        if not results:  # If results are None or an empty list
            print("No relevant data found for your query.")
        else:
            print("Query Results:")
            for result in results:
                print(result)  # Print each result in a structured format
