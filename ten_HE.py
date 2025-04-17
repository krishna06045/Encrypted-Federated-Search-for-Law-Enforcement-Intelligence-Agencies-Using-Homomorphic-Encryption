import pandas as pd
import os
import tenseal as ts
import base64
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def generate_and_save_context(path="bfv_context.tenseal") -> ts.Context:
    poly_mod_degree = int(os.getenv("CONTEXT_POLY_MOD_DEGREE", 8192))
    plain_modulus = int(os.getenv("CONTEXT_PLAIN_MODULUS", 1032193))

    ctx = ts.context(ts.SCHEME_TYPE.BFV, poly_mod_degree, plain_modulus)
    ctx.generate_galois_keys()

    with open(path, "wb") as f:
        f.write(ctx.serialize(
            save_public_key=True,
            save_secret_key=True,
            save_galois_keys=True
        ))

    return ctx

def encrypt_value(context: ts.Context, value) -> str:
    try:
        value = [ord(c) for c in value.lower()] if isinstance(value, str) else [int(value)]
        vec = ts.bfv_vector(context, value)
        return base64.b64encode(vec.serialize()).decode()
    except Exception as e:
        print(f"❌ Encryption failed for {value}: {e}")
        return None

def connect_mongo():
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")
    client = MongoClient(uri)
    return client[db_name]

def load_crime_data(csv_path, city):
    df = pd.read_csv(csv_path)
    df = df[df['City'].str.lower() == city.lower()]
    df = df.drop_duplicates().fillna('Unknown')
    df.columns = df.columns.str.strip().str.lower()
    return df.head(200)

def encrypt_and_store(df, context, city, db):
    fields_to_encrypt = ['report number', 'crime code', 'victim age', 'police deployed']
    encrypted_docs = []
    collection = db[f"crimes_{city.lower()}"]

    for _, row in df.iterrows():
        doc = {}
        for col in df.columns:
            val = row[col]
            doc[col] = encrypt_value(context, val) if col in fields_to_encrypt else val
        doc['city'] = city.lower()
        encrypted_docs.append(doc)

    collection.insert_many(encrypted_docs)
    print(f"\n✅ Encrypted & inserted {len(encrypted_docs)} records into collection: crimes_{city.lower()}")

def main():
    context = generate_and_save_context()
    db = connect_mongo()
    csv_path = r"C:\Users\Krishna Agrawal\Downloads\crime_dataset_india.csv"

    for city in ['Mumbai', 'Delhi','Chennai']:
        print(f"\n🔷 Encrypting data for city: {city}")
        df = load_crime_data(csv_path, city)
        encrypt_and_store(df, context, city, db)

if __name__ == "__main__":
    main()