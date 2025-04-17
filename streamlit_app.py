import streamlit as st
import hashlib
import json
import os
import base64
import time
import tenseal as ts
from pymongo import MongoClient
from dotenv import load_dotenv
from blockchain import Blockchain

# --- User Database Management (ZKP-style) ---
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_secret(secret):
    return hashlib.sha256(secret.encode()).hexdigest()

def add_user(username, password, role="officer"):
    users = load_users()
    if username in users:
        return False, "Username already exists."
    users[username] = {
        "zkp_hash": hash_secret(password),
        "role": role
    }
    save_users(users)
    return True, f"User '{username}' added as '{role}'."

def verify_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Username not found."
    if hash_secret(password) == users[username]["zkp_hash"]:
        return True, users[username]["role"]
    else:
        return False, "Invalid password."

# --- Blockchain Logging ---
ledger = Blockchain()

def log_zkp_auth_to_blockchain(username, zkp_hash):
    ledger.add_block({
        "action": "ZKP login",
        "user": username,
        "zkp_hash": zkp_hash,
        "timestamp": time.time()
    })
    ledger.persist_chain()

# --- Encrypted Search Logic ---
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

@st.cache_resource
def get_context():
    with open("bfv_context.tenseal", "rb") as f:
        return ts.context_from(f.read())

@st.cache_resource
def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def encrypt_query(context, value):
    return ts.bfv_vector(context, [int(value)])

def decrypt_vector(context, encrypted_b64):
    try:
        enc = ts.bfv_vector_from(context, base64.b64decode(encrypted_b64))
        return enc.decrypt()[0]
    except Exception as e:
        return f"Error: {e}"

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
            st.warning(f"⚠️ Skipping doc {doc['_id']} due to error: {e}")
    return matched_ids

# --- Streamlit App ---
def main():
    st.set_page_config(page_title="Encrypted Federated Crime Search", layout="centered")
    st.title("🔐 ZKP Authentication & Encrypted Federated Crime Search")

    if "authenticated" not in st.session_state:
        st.session_state.update({
            "authenticated": False,
            "username": "",
            "role": ""
        })

    # --- Login ---
    if not st.session_state["authenticated"]:
        st.subheader("🔑 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            valid, result = verify_user(username, password)
            if valid:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = result
                log_zkp_auth_to_blockchain(username, hash_secret(password))
                st.success("✅ Login successful!")
                st.experimental_rerun()
            else:
                st.error(result)
        return

    # --- Sidebar Logout ---
    st.sidebar.success(f"Logged in as: {st.session_state['username']} ({st.session_state['role']})")
    if st.sidebar.button("🚪 Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.experimental_rerun()

    # --- Admin User Management Panel ---
    if st.session_state["role"] == "admin":
        st.subheader("👤 Add New User")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        new_role = st.selectbox("Select Role", ["officer", "analyst", "admin"])
        if st.button("Add User"):
            success, msg = add_user(new_user, new_pass, new_role)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    # --- Search for Officer and Admin ---
    if st.session_state["role"] in ["officer", "admin"]:
        st.header("🔍 Encrypted Federated Search")
        field_option = st.selectbox(
            "Select the field to search by:",
            ["Crime Code", "Report Number", "Victim Age", "Police Deployed"]
        )
        query_input = st.text_input(f"Enter {field_option} (numeric):")

        if st.button("Search"):
            if not query_input.isdigit():
                st.error(f"{field_option} must be numeric.")
                return

            field_map = {
                "Crime Code": "crime code",
                "Report Number": "report number",
                "Victim Age": "victim age",
                "Police Deployed": "police deployed"
            }
            field = field_map[field_option]
            context = get_context()
            db = get_db()
            total_results = []

            for city in ['mumbai', 'delhi', 'chennai']:
                st.subheader(f"📂 Searching in collection: crimes_{city}")
                collection = db[f"crimes_{city}"]
                found_ids = search_in_collection(context, query_input, collection, field)

                ledger.add_block({
                    "query": query_input,
                    "timestamp": time.time(),
                    "result_count": len(found_ids),
                    "collection": f"crimes_{city}"
                })
                ledger.persist_chain()

                if found_ids:
                    results = list(collection.find({"_id": {"$in": found_ids}}))
                    total_results.extend(results)
                else:
                    st.info(f"No results found in crimes_{city}")

            if total_results:
                st.success(f"✅ Found {len(total_results)} matching document(s):")
                for doc in total_results:
                    with st.expander(f"Document ID: {doc['_id']}"):
                        for key, value in doc.items():
                            if key in field_map.values():
                                decrypted = decrypt_vector(context, value)
                                st.write(f"**{key.title()}**: {decrypted}")
                            else:
                                st.write(f"**{key.title()}**: {value}")
            else:
                st.error("❌ No matching documents found.")

    # --- Analyst Role ---
    elif st.session_state["role"] == "analyst":
        st.header("📜 Blockchain Logs")
        log_file = "blockchain_log.json"
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)
                for entry in logs:
                    st.json(entry)
        else:
            st.warning("Blockchain log file not found.")

    else:
        st.warning("Unknown role. No actions available.")

if __name__ == "__main__":
    main()
