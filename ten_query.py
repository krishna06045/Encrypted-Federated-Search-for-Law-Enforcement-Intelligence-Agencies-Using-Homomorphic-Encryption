import base64
import os
import time
import tenseal as ts
from pymongo import MongoClient
from dotenv import load_dotenv
from blockchain import Blockchain

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

def get_context():
    with open("bfv_context.tenseal", "rb") as f:
        return ts.context_from(f.read())

# Global blockchain instance
ledger = Blockchain()

def encrypt_query(context, value):
    return ts.bfv_vector(context, [int(value)])

def decrypt_vector(context, encrypted_b64):
    try:
        enc = ts.bfv_vector_from(context, base64.b64decode(encrypted_b64))
        return enc.decrypt()[0]
    except Exception as e:
        return f"❌ Error: {e}"

def search_in_collection(context, value, collection, field):
    encrypted_query = encrypt_query(context, value)
    docs = list(collection.find({}, {"_id": 1, field: 1}))

    matched_ids = []
    for doc in docs:
        try:
            enc_val = ts.bfv_vector_from(context, base64.b64decode(doc[field]))
            if enc_val.decrypt() == encrypted_query.decrypt():
                matched_ids.append(doc["_id"])
        except Exception as e:
            print(f"⚠️ Skipping doc {doc['_id']} due to error: {e}")

    return matched_ids

def main():
    context = get_context()
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    print("🔍 Choose the field you want to search by:")
    print("1. Crime Code")
    print("2. Report Number")
    print("3. Victim Age")
    print("4. Police Deployed")
    choice = input("Enter the number corresponding to your choice: ").strip()

    if choice == '1':
        field = "crime code"
    elif choice == '2':
        field = "report number"
    elif choice == '3':
        field = "victim age"
    elif choice == '4':
        field = "police deployed"
    else:
        print("❌ Invalid choice.")
        return

    query = input(f"🔍 Enter {field} to search: ").strip()
    if not query.isdigit():
        print(f"❌ {field} must be numeric.")
        return

    total_results = []
    all_found_ids = []

    for city in ['mumbai', 'delhi', 'chennai']:
        print(f"\n📂 Searching in collection: crimes_{city}")
        collection = db[f"crimes_{city}"]
        found_ids = search_in_collection(context, query, collection, field)
        all_found_ids.extend(found_ids)

        if not found_ids:
            ledger.add_block({
                "query": query,
                "timestamp": time.time(),
                "result_count": 0,
                "collection": f"crimes_{city}"
            })
            ledger.persist_chain()
            continue

        results = list(collection.find({"_id": {"$in": found_ids}}))
        total_results.extend(results)

        ledger.add_block({
            "query": query,
            "timestamp": time.time(),
            "result_count": len(found_ids),
            "collection": f"crimes_{city}"
        })
        ledger.persist_chain()

    if not total_results:
        print("\n❌ No matching documents found.")
        return

    print(f"\n✅ Found {len(total_results)} matching document(s):")
    for doc in total_results:
        print("-" * 40)
        for key, value in doc.items():
            if key in ["crime code", "report number", "victim age", "police deployed"]:  # Decrypt all these fields
                decrypted = decrypt_vector(context, value)
                print(f"{key:<18}: {decrypted}")
            else:
                print(f"{key:<18}: {value}")
        print("-" * 40)

if __name__ == "__main__":
    main()
