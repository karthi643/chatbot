import sqlite3

# Step 1: Connect to the database
def create_connection():
    conn = sqlite3.connect(r'nltk_folder\mychatbot\my_database.db')
    return conn

# Step 2: Preprocess user input
def preprocess_input(user_input):
    return user_input.strip().lower()

# Step 3: Construct wildcard query
def construct_wildcard_query(search_term):
    columns = ['Description', 'Category', 'Platform', 'Notes']
    like_clauses = [f"{column} LIKE '%{search_term}%'" for column in columns]
    where_clause = " OR ".join(like_clauses)
    query = f"SELECT * FROM my_transactions WHERE {where_clause};"
    return query

# Step 4: Execute SQL query
def execute_query(query):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Main flow
search_term = input("Enter search term: ")
search_term = preprocess_input(search_term)
sql_query = construct_wildcard_query(search_term)
results = execute_query(sql_query)

# Step 5: Display results
for row in results:
    print(row)
