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
# Creating dictionaries for credit and debit keywords
credit_keywords = {
    "Salary": ["salary", "paycheck", "monthly salary"],
    "Freelance": ["freelance income", "project payment", "consulting fees"],
    "Part-Time Job": ["part-time job income", "retail shift", "store assistant", "cafe work"],
    "Dividends": ["stock dividend", "mutual fund dividend"],
    "Investment Returns": ["fixed deposit", "interest", "investment return"],
    "Writing Income": ["writing income", "content creation income"],
    "Online Typing": ["online typing", "typing job income"]
}

debit_keywords= {
    "Shopping": ["shopping", "clothes", "buy", "purchase", "retail", "flipkart", "amazon", "myntra", "local market"],
    "Food": ["food", "meals", "dining", "restaurant", "swiggy", "zomato", "cafe"],
    "Transport": ["transport", "travel", "cab", "ola", "uber", "metro", "fuel station"],
    "Utilities": ["utilities", "bills", "electricity", "water bill", "internet", "gas bill", "electricity bill"],
    "Entertainment": ["entertainment", "movies", "music", "shows", "netflix", "spotify", "kindle", "amazon prime"],
    "Rent": ["rent", "house rent", "apartment rent", "flat rent"],
    "Healthcare": ["healthcare", "doctor", "hospital", "medicine", "medical bill"],
    "Education": ["tuition fees", "education", "college fees", "school fees", "course fees"]
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
    # Tokenize text
    tokens = word_tokenize(text)
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.lower() not in stop_words]
    # Tag parts of speech
    pos_tags = pos_tag(tokens)
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
        'is_credit': None,
        'date_range': None,
    }

    found_platform = False
    found_category = False

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
        credit_keywords = ["income", "credit", "earnings", "revenue", "gain","gained", "profit", "deposit", "inflow","earned","earning","got"]

        if word_lower in debit_keywords:
            conditions['is_credit'] = False
        elif word_lower in credit_keywords:
            conditions['is_credit'] = True

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

    # Initialize a list to hold the conditions
    condition_clauses = []

    # Define platform and category mappings (provided by you)
   

    # Platform matching logic
    matched_platform = False
    if 'platform' in conditions and conditions['platform'] is not None:
        for platform, keywords in platform_mapping.items():
            if any(keyword.lower() in conditions['platform'].lower() for keyword in keywords):
                condition_clauses.append(f"Platform = '{platform}'")
                matched_platform = True
                break

    # Category matching logic (if no platform match)
    if not matched_platform and 'category' in conditions and conditions['category'] is not None:
        for category, keywords in category_mapping.items():
            if any(keyword.lower() in conditions['category'].lower() for keyword in keywords):
                condition_clauses.append(f"Category = '{category}'")
                break

    # Add spent filter using the Notes column
    if 'is_credit' in conditions:
        if conditions['is_credit']:  # If it's a credit
            condition_clauses.append("Notes = 'Credit'")  # Filter for income (credit)
        else:  # If it's a debit
            condition_clauses.append("Notes = 'Debit'")  # Filter for expenses (debit)

    # Add date range filter if present
    if 'date_range' in conditions and conditions['date_range'] is not None:
        condition_clauses.append(f"Date >= '{conditions['date_range']}'")

    # Check if both category and platform are not provided
    if not any(key in conditions for key in ['category', 'platform']):
        condition_clauses.append("Notes IS NOT NULL")  # Or any other condition based on Notes

    # Ensure that any None results are not included in the final query
    if condition_clauses:
        query += " AND ".join(condition_clauses)
    else:
        query = query.rstrip(" WHERE ")  # Remove WHERE if no conditions

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
    while True:
        text = input("Please enter your query (or type 'exit' to quit): ")
        if text.lower() == 'exit':
            print("Exiting the chatbot. Goodbye!")
            break  # Exit the loop

        sql_query = generate_sql_query(text)
        print("Generated SQL Query:", sql_query)  # Debugging: Print the generated SQL query
        
        # Execute the query
        results = execute_query(sql_query)
        
        if not results:  # If results are None or an empty list
            print("No relevant data found.")
        else:
            print("Query Results:", results)  # Debugging: Print the results from SQL execution