from pymongo import MongoClient
import os
import pprint
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['credit_platform'] # scripts say 'credit_app' or 'credit_platform'? 
# process_messages.py uses: DB_NAME = os.getenv("DB_NAME", "credit_platform")
# verify_mongodb.py used: db = client['creditapp'] (Wait, verify used 'creditapp'?)
# Let's check verify_mongodb.py code again.

# Viewing file content earlier:
# line 17: db = client['creditapp']
# line 63: print(f"📊 Base de données: credit_platform") -> Print says platform but code says creditapp?
# Let's check process_messages.py code.
# line 17: DB_NAME = os.getenv("DB_NAME", "credit_platform")

# POTENTIAL BUG FOUND: verify_mongodb might be looking at a DIFFERENT DB than process_messages?
# If verify says "6000", but process says "0", maybe they look at different DBs.
# verify_mongodb.py:
# db = client['creditapp']

# process_messages.py:
# DB_NAME = "credit_platform" (default)

# user's verify output from step 63 said: "Base de données: credit_platform"
# But the CODE I viewed in step 16 said:
# 17: db = client['creditapp']
# 63: print(f"📊 Base de données: credit_platform")

# THIS IS IT! The print statement is hardcoded to say "credit_platform" but it connects to 'creditapp'.
# process_messages connects to "credit_platform".
# So process_messages is looking at an EMPTY DB?
# Or maybe the data is in 'creditapp'.

# I will check which DB has the data.
print("Check 'creditapp':")
print(client['creditapp'].messages.count_documents({}))
print("Check 'credit_platform':")
print(client['credit_platform'].messages.count_documents({}))
