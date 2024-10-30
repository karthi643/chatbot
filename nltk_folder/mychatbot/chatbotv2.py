import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from datetime import datetime, timedelta
import sqlite3
from word2number import w2n

# Ensure required NLTK data files are downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')

# Connect to the database
conn = sqlite3.connect('nltk_folder/mychatbot/my_database.db')  # Adjust path if necessary
cursor = conn.cursor()

# Commit the changes and close the connection
conn.commit()
conn.close()
word_to_number = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
    "ninety": 90, "hundred": 100
}

# Define a dictionary to map possible user inputs to SQL aggregation functions
aggregation_mappings = {
    "min": ["min", "minimum", "least", "lowest", "smallest", "bottom", "fewest"],
    "max": ["max", "maximum", "highest", "greatest", "largest", "top", "most"],
    "avg": ["avg", "average", "mean", "typical", "median", "usual"],
    "total": ["total", "sum", "overall", "total spent", "add up", "combined", "how much"],
    "top": ["top", "highest", "maximum", "best", "peak"],
    "least": ["least", "minimum", "lowest", "smallest", "bottom", "fewest"]
}
# Define a mapping for time frame keywords
time_frame_mapping = {
    "days": ["day", "days", "daily"],
    "weeks": ["week", "weeks", "weekly"],
    "months": ["month", "months", "monthly", "last month", "this month"],
    "years": ["year", "years", "annually"],
    "last": ["last", "past", "recent"],
}
payment_method_mapping = {
    "online transfer": "Online Transfer",
    "bank transfer": "Online Transfer",
    "net banking": "Online Transfer",
    "credit card": "Card",
    "debit card": "Card",
    "card payment": "Card",
}

# Define the SQL functions corresponding to each aggregation
aggregation_functions = {
    "min": "MIN(Amount)",
    "max": "MAX(Amount)",
    "avg": "AVG(Amount)",
    "total": "SUM(Amount)",
    "top": "MAX(Amount)",
    "least": "MIN(Amount)"
}
platform_mapping = {
    "Flipkart": ["flipkart"],
    "Amazon": ["amazon"],
    "Stock Dividend": ["stock dividend"],
    "Mutual Funds": ["mutual funds"],
    "Fixed Deposit": ["fixed deposit"],
    "Store Assistant": ["store assistant"],
    "Metro": ["metro"],
    "Cafe Work": ["cafe work"],
    "Freelance Project": ["freelance project"],
    "Swiggy": ["swiggy"],
    "Zomato": ["zomato"],
    "Retail Shift": ["retail shift"],
    "Local Market": ["local market"],
    "Online Typing": ["online typing"],
    "Restaurant": ["restaurant"],
    "Spotify": ["spotify"],
    "Internet": ["internet"],
    "Myntra": ["myntra"],
    "Kindle": ["kindle"],
    "Water Bill": ["water bill"],
    "Netflix": ["netflix"],
    "Electricity Bill": ["electricity bill"],
    "Cafe": ["cafe"],
    "Fuel Station": ["fuel station"],
    "Ola": ["ola"],
    "Amazon Prime": ["amazon prime"],
    "Writing Income": ["writing income"],
    "Uber": ["uber"],
    "Gas Bill": ["gas bill"]
}

# Create a mapping for user-friendly terms to database categories
category_mapping = {
    "Food": ["food", "meals", "dining", "restaurants", "swiggy", "zomato"],
    "Entertainment": ["entertainment", "movies", "music", "shows", "netflix", "spotify", "amazon prime"],
    "Transport": ["transport", "travel", "cab", "ola", "uber", "metro"],
    "Utilities": ["utilities", "bills", "electricity", "water", "internet", "electricity bill", "water bill", "gas bill"],
    "Shopping": ["shopping", "clothes", "retail", "buy", "flipkart", "amazon", "myntra"],
    "Investment": ["investment", "stocks", "mutual funds", "savings", "fixed deposit", "stock dividend"],
    "Part-Time Job": ["part-time", "job", "work", "gig", "store assistant", "retail shift"],
    "Freelance": ["freelance", "project", "contract", "consulting", "freelance project", "online typing"],
}


def preprocess_text(text):
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.lower() not in stop_words]
    pos_tags = pos_tag(tokens)
    print(pos_tags)  # This is for debugging
    return pos_tags


def get_aggregation_function(user_input):
    """Identify the corresponding SQL aggregation function. Defaults to SUM if none found."""
    user_input = user_input.lower()
    for agg, keywords in aggregation_mappings.items():
        if any(keyword in user_input for keyword in keywords):
            return aggregation_functions[agg]
    return aggregation_functions["total"]  # Default to SUM if no keywords found

 # Import library to convert words to numbers

def extract_conditions(pos_tags):
    conditions = {
        'platform': None,
        'category': None,
        'numeric_value': None,
        'aggregation': None,
        'time_frame': None,
        'is_spent': None,
        'date_range': None,
        'payment_method': None
    }

    found_platform = False
    found_category = False
    found_payment_method = False

    for i, (word, tag) in enumerate(pos_tags):
        word_lower = word.lower()

        # Check for aggregation functions
        aggregation_func = get_aggregation_function(word_lower)
        if aggregation_func:
            conditions['aggregation'] = aggregation_func

        # Check for category
        for category, synonyms in category_mapping.items():
            if word_lower in synonyms:
                conditions['category'] = category.capitalize()  # Capitalize the category name
                found_category = True
                break  # Stop checking once we find a match

        # Check for platform
        for platform, synonyms in platform_mapping.items():
            if word_lower in synonyms:
                conditions['platform'] = platform.capitalize()  # Capitalize the platform name
                found_platform = True
                break  # Stop checking once we find a match
        # Check for payment method
        for payment, synonyms in payment_method_mapping.items():
            if word_lower in synonyms:
                conditions['payment_method'] = payment_method_mapping[payment]  # Use mapped payment method
                found_payment_method = True
                break  # Stop checking once we find a match

        # Handle numeric values and explicit time frames
        if tag == 'CD' or word_lower in word_to_number:  # Check for cardinal numbers
            try:
                numeric_value = int(word_lower)
            except ValueError:
                try:
                    numeric_value = w2n.word_to_num(word_lower)
                except ValueError:
                    numeric_value = None  # If conversion fails, skip

            if numeric_value is not None and i + 1 < len(pos_tags):
                next_word = pos_tags[i + 1][0].lower()
                for time_unit, synonyms in time_frame_mapping.items():
                    if next_word in synonyms:
                        conditions['time_frame'] = (time_unit, numeric_value)  # Example: ('months', 3)
                        break

        # Check for credit or debit keywords
        debit_keywords = ["spent", "debit", "expenditure", "expense", "pay", "payment", "cost", "outflow", "withdrawal"]
        credit_keywords = ["income", "credit", "earnings", "revenue", "gain", "profit", "deposit", "inflow"]

        if word_lower in debit_keywords:
            conditions['is_spent'] = True
        elif word_lower in credit_keywords:
            conditions['is_spent'] = False

    # Set default date range if "time_frame" is found in conditions
    if 'time_frame' in conditions and conditions['time_frame']:
        today = datetime.now()
        time_unit, value = conditions['time_frame']

        if time_unit == "months":
            date_threshold = today - timedelta(days=value * 30)
        elif time_unit == "weeks":
            date_threshold = today - timedelta(weeks=value)
        elif time_unit == "days":
            date_threshold = today - timedelta(days=value)
        elif time_unit == "years":
            date_threshold = today - timedelta(days=value * 365)

        conditions['date_range'] = date_threshold.strftime("%Y-%m-%d")

    # Set flags if no category or platform was found
    if not found_category:
        conditions['no_category_found'] = True
    if not found_platform:
        conditions['no_platform_found'] = True

    return conditions

def construct_sql_query(conditions):
    query = "SELECT "
    
    # Select the aggregation function if provided
    if 'aggregation' in conditions:
        query += f"{conditions['aggregation']} "
    else:
        query += "* "  # If no aggregation specified, select all columns

    query += "FROM my_transactions WHERE "

    # Initialize a list to hold the clauses
    clauses = []

    # Add category filter if specified and not 'None'
    if 'category' in conditions and conditions['category'] != 'None':
        clauses.append(f"Category = '{conditions['category']}'")

    # Add platform filter if specified and not 'None'
    if 'platform' in conditions and conditions['platform'] != 'None':
        clauses.append(f"Platform = '{conditions['platform']}'")

    # Handle case where both category and platform are 'None'
    if 'category' in conditions and conditions['category'] == 'None' and\
       'platform' in conditions and conditions['platform'] == 'None':
        if 'is_spent' in conditions:
            if conditions['is_spent']:
                clauses.append("Notes = 'Debit'")  # Expenses (debit)
            else:
                clauses.append("Notes = 'Credit'")  # Income (credit)

   # Add payment method filter if specified
    if 'payment_method' in conditions and conditions['payment_method']:
        clauses.append(f"Payment_Method = '{conditions['payment_method'].lower()}'")

    # Add date range filter if specified
    if 'date_range' in conditions:
        clauses.append(f"Date >= '{conditions['date_range']}'")

    # Combine clauses with AND
    if clauses:
        query += " AND ".join(clauses)
    else:
        # If no conditions were provided, select all transactions
        query = "SELECT * FROM my_transactions"

    return query


def generate_sql_query(natural_text):
    pos_tags = preprocess_text(natural_text)
    conditions = extract_conditions(pos_tags)
    sql_query = construct_sql_query(conditions)
    return sql_query

def execute_query(query):
    # Connect to the SQLite database
    conn = sqlite3.connect('nltk_folder/mychatbot/my_database.db')  # Ensure to connect to the correct database
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    # Check if results are empty and handle accordingly
    if not results:
        return "No spending found in this category."  # Message for no matching records
    
    return results

if __name__ == "__main__":
    # Example natural language input
    text = "What is the total amount spent for food in last six months?"
    sql_query = generate_sql_query(text)
    print("Generated SQL Query:", sql_query)  # Debugging: Print the generated SQL query

    # Execute the query
    results = execute_query(sql_query)
    print("Query Results:", results)  # Debugging: Print the results from SQL execution
