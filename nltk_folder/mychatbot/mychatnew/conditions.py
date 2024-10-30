from datetime import datetime, timedelta
from nltk.tokenize import word_tokenize
from word2number import w2n  # Ensure this library is installed
from aggregation import get_aggregation_function  # Import the function

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
    "Flipkart": ["flipkart", "online shopping", "e-commerce", "electronics store", "fashion store", "gadget shop", "apparel retailer"],
    "Amazon": ["amazon", "global e-commerce", "e-marketplace", "digital store", "books retailer", "appliance store"],
    "Stock Dividend": ["stock dividend", "stock returns", "dividend payout", "equity returns", "investment income", "equities profit"],
    "Mutual Funds": ["mutual funds", "investment portfolio", "fund management", "savings growth", "financial assets"],
    "Fixed Deposit": ["fixed deposit", "long-term savings", "secured deposit", "time deposit"],
    "Store Assistant": ["store assistant", "part-time store worker", "retail job", "customer service rep", "shop assistant", "sales employee"],
    "Metro": ["metro", "city metro", "urban transit", "subway service", "commuter rail", "train transport"],
    "Cafe Work": ["cafe work", "barista job", "part-time barista", "cafe attendant", "coffeehouse job"],
    "Freelance Project": ["freelance project", "freelance consulting", "gig project", "contract assignment", "consultant project"],
    "Swiggy": ["swiggy", "food delivery app", "online restaurant orders", "quick food delivery"],
    "Zomato": ["zomato", "restaurant platform", "online dining orders", "food app", "dining reservations"],
    "Retail Shift": ["retail shift", "sales shift", "store shift", "retail service", "shift work"],
    "Local Market": ["local market", "farmers market", "street bazaar", "fresh produce market", "vegetable market"],
    "Online Typing": ["online typing", "data entry gig", "online documentation", "transcription work"],
    "Restaurant": ["restaurant", "fine dining", "casual dining", "eatery", "restaurant visit", "bistro"],
    "Spotify": ["spotify", "audio streaming service", "music platform", "digital music service", "audio entertainment"],
    "Internet": ["internet provider", "broadband service", "ISP connection", "Wi-Fi provider", "home internet"],
    "Myntra": ["myntra", "fashion e-commerce", "clothing retailer", "apparel marketplace", "fashion shop"],
    "Kindle": ["kindle", "digital reading", "e-book service", "e-book store", "digital books"],
    "Water Bill": ["water bill", "municipal water fee", "utility water charge"],
    "Netflix": ["netflix", "video streaming platform", "digital streaming", "on-demand video service"],
    "Electricity Bill": ["electricity bill", "power bill", "energy utility fee"],
    "Cafe": ["cafe", "coffee shop", "espresso bar", "bistro", "tea shop"],
    "Fuel Station": ["fuel station", "gas pump", "petrol station", "diesel vendor", "refueling station"],
    "Ola": ["ola", "ride-hailing service", "app-based taxi", "cab company", "transport service"],
    "Amazon Prime": ["amazon prime", "prime membership", "exclusive membership", "premium subscription"],
    "Writing Income": ["writing income", "content writing earnings", "freelance writer income", "journalism pay"],
    "Uber": ["uber", "ride-share service", "transport app", "cab booking service"],
    "Gas Bill": ["gas bill", "cooking gas bill", "LPG bill", "home gas bill"],
    "BookMyShow": ["bookmyshow", "entertainment booking", "event tickets", "show booking", "movie ticketing"],
    "Cleartrip": ["cleartrip", "online travel booking", "flight and hotel booking", "travel planning"],
    "Practitioner": ["doctor visit", "health checkup", "medical appointment", "clinic visit", "physician consultation"],
    "PayPal": ["paypal", "digital payment platform", "e-wallet service", "money transfer app"],
    "Udemy": ["udemy", "online education", "skill courses", "digital learning platform", "educational resources"],
    "Zoom": ["zoom", "video conferencing app", "virtual meeting platform", "webinar hosting"],
    "Trello": ["trello", "team collaboration app", "task management platform", "project organization tool"],
    "Airbnb": ["airbnb", "vacation rental platform", "home-stay booking", "private accommodation"],
    "Insurance": ["insurance", "health policy", "life coverage", "auto insurance", "risk coverage"],
    "Charity": ["charity", "philanthropic donation", "non-profit aid", "fundraising activity"],
    "eBay": ["ebay", "online auction", "resale platform", "second-hand goods", "e-commerce marketplace"],
    "Paytm": ["paytm", "mobile payment app", "digital wallet service", "payment solution"],
    "LinkedIn Learning": ["linkedin learning", "professional education", "career development courses"],
    "HDFC Bank": ["hdfc bank", "banking institution", "financial service", "banking provider"],
    "SBI Bank": ["sbi bank", "government bank", "financial institution", "savings service"],
    "Zerodha": ["zerodha", "online brokerage", "stock trading platform", "investment broker"],
    "Groww": ["groww", "investment app", "mutual fund app", "investment management"],
    "Snacks": ["snacks", "quick bites", "savories", "light refreshments", "junk food"],
    "Beverages": ["beverages", "cold drinks", "hot drinks", "refreshments"],
    "Grocery Store": ["grocery store", "supermarket", "daily essentials market", "food supplies"],
    "Fitness Center": ["fitness center", "gym", "workout club", "exercise facility"],
    "Personal Care": ["personal care", "self-care products", "skincare goods", "beauty supplies"],
    "Household Items": ["household items", "home essentials", "furniture goods", "cleaning supplies"],
    "Travel": ["travel", "tourism", "vacation trips", "holiday planning"]
}

category_mapping = {
    "Food": ["food", "dining out", "restaurant meals", "snacks", "groceries", "beverages", "cafe visit"],
    "Entertainment": ["entertainment", "movies", "music", "shows", "subscriptions", "events", "concerts", "games"],
    "Transport": ["transport", "commuting", "ride-hailing", "public transport", "fuel costs", "flights"],
    "Utilities": ["utilities", "water bill", "power bill", "internet bill", "gas bill", "phone bills", "service charges"],
    "Shopping": ["shopping", "clothing", "apparel", "home goods", "fashion accessories", "electronics", "gifts", "furniture"],
    "Investment": ["investment", "stocks", "mutual funds", "dividends", "fixed deposits", "financial planning", "investment returns"],
    "Part-Time Job": ["part-time work", "store assistant job", "retail shift work", "side hustle", "gig job"],
    "Freelance": ["freelance work", "project payment", "contract jobs", "consulting gigs", "writing assignments"],
    "Healthcare": ["healthcare expenses", "medical costs", "treatment fees", "hospital bills", "clinic charges"],
    "Education": ["education costs", "school fees", "college expenses", "online learning", "skill courses", "books"],
    "Gifts & Donations": ["gifts", "donations", "charitable contributions", "philanthropic spending"],
    "Travel": ["travel expenses", "flight bookings", "hotel stays", "vacation costs", "tourist activities"],
    "Subscription Services": ["subscriptions", "membership fees", "digital services", "monthly plans", "streaming services"],
    "Home Improvement": ["home improvement", "repairs", "decor updates", "furniture purchases", "maintenance costs"],
    "Miscellaneous": ["miscellaneous expenses", "other spending", "general costs", "various items"]
}


payment_method =  {
    "online transfer": "Online Transfer",
    "bank transfer": "Online Transfer",
    "net banking": "Online Transfer",
    "credit card": "Card",
    "debit card": "Card",
    "card payment": "Card",
}


def extract_conditions(pos_tags):
    conditions = {
        'platform': [],
        'category': [],
        'numeric_value': None,
        'aggregation': None,
        'time_frame': None,
        'is_credit': None,
        'date_range': None,
        'payment_method': None
    }

    for i, (word, tag) in enumerate(pos_tags):
        word_lower = word.lower()

        # Check for aggregation functions
        aggregation_func = get_aggregation_function(word_lower)  # Call imported function
        if aggregation_func:
            conditions['aggregation'] = aggregation_func

        # Check for category
        for category, synonyms in category_mapping.items():
            if word_lower in synonyms:
                if category.capitalize() not in conditions['category']:  # Avoid duplicates
                    conditions['category'].append(category.capitalize())  # Store as array

        # Check for platform
        for platform, synonyms in platform_mapping.items():
            if word_lower in synonyms:
                if platform.capitalize() not in conditions['platform']:  # Avoid duplicates
                    conditions['platform'].append(platform.capitalize())  # Store as array

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
        debit_keywords = ["spent", "debit", "expenditure", "expenses", "expense", "pay", "payment", "cost", "outflow", "withdrawal", "spend", "spending", "spendings"]
        credit_keywords = ["income", "credit", "earnings", "revenue", "gain", "gained", "profit", "deposit", "inflow", "earned", "earning", "got"]

        if word_lower in debit_keywords:
            conditions['is_credit'] = False
        elif word_lower in credit_keywords:
            conditions['is_credit'] = True

        # Check for payment method
        for method, keywords in payment_method.items():
            if word_lower in keywords:
                conditions['payment_method'] = method
                break  # Stop checking once we find a match

    # Set default date range if "time_frame" is found in conditions
    if 'time_frame' in conditions and conditions['time_frame'] is not None:
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

    return conditions