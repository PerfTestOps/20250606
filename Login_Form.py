from pymongo import MongoClient

# MongoDB connection
MONGO_URL="mongodb+srv://perftestanalyzer:D9C6yDTNkVuDzrUT@clustertransaction.wqku6mp.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTransaction"
client = MongoClient(MONGO_URL)

# Database and collection
db = client["Login_Form"]
user_collection = db["UserID's"]

# Check credentials
def check_user(username, password):
    user = user_collection.find_one({"username": username})
    return user and user["password"] == password

# Create new user
def create_user(name, email, username, password):
    if user_collection.find_one({"username": username}):
        return "username_exists"
    if user_collection.find_one({"email": email}):
        return "email_exists"

    user_collection.insert_one({
        "name": name,
        "email": email,
        "username": username,
        "password": password
    })
    return "success"
