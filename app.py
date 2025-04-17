import hashlib
import json
import os
import time
import subprocess
from blockchain import Blockchain

# Load or create user database (in JSON file)
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

# SHA-256 hash function for ZKP-style commitment
def hash_secret(secret):
    return hashlib.sha256(secret.encode()).hexdigest()

# Register a new user
def register_user(username, password, role="officer"):
    users = load_users()
    if username in users:
        print("⚠️ Username already exists.")
        return

    users[username] = {
        "zkp_hash": hash_secret(password),
        "role": role
    }
    save_users(users)
    print(f"✅ User registered successfully as '{role}'.")

def get_user_role(username):
    users = load_users()
    return users.get(username, {}).get("role", "unknown")

def is_authorized(username, action):
    role = get_user_role(username)
    role_permissions = {
        "admin": ["search", "view_logs", "register"],
        "officer": ["search"],
        "analyst": ["view_logs"]
    }
    return action in role_permissions.get(role, [])

# Log successful ZKP-style login to blockchain
def log_zkp_auth_to_blockchain(username, zkp_hash):
    ledger = Blockchain()
    ledger.add_block({
        "action": "ZKP login",
        "user": username,
        "zkp_hash": zkp_hash,
        "timestamp": time.time()
    })
    ledger.persist_chain()
    print("🔗 ZKP login logged to blockchain.")

# Post-login role router
def role_router(username):
    role = get_user_role(username)
    print(f"🚦 Routing based on role: {role}")

    if role == "admin":
        while True:
            print("\n🧑‍💼 Admin Panel")
            print("[1] Add new user")
            print("[0] Exit admin panel")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                new_username = input("Enter new username: ").strip()
                new_password = input("Enter new password: ").strip()
                print("Available roles: admin, officer, analyst")
                new_role = input("Enter role for new user: ").strip().lower()
                register_user(new_username, new_password, new_role)
            elif choice == "0":
                break
            else:
                print("❌ Invalid choice.")

    elif role == "officer":
        print("🕵️ Launching federated search query interface...")
        subprocess.run(["python", "ten_query.py"])

    elif role == "analyst":
        log_file = "blockchain_log.json"
        if os.path.exists(log_file):
            print("📜 Viewing Blockchain Logs:")
            with open(log_file, "r") as f:
                logs = json.load(f)
                for entry in logs:
                    print(json.dumps(entry, indent=2))
        else:
            print("❌ Log file not found.")

    else:
        print("⛔ Unknown role. No actions available.")

# Verify proof of knowledge (ZKP login)
def login_user(username, password):
    users = load_users()
    if username not in users:
        print("❌ Username not found.")
        return

    provided_hash = hash_secret(password)
    stored_hash = users[username]["zkp_hash"]

    if provided_hash == stored_hash:
        print("✅ ZKP-style login successful!")
        log_zkp_auth_to_blockchain(username, provided_hash)

        role = get_user_role(username)
        print(f"🔐 Role: {role}")

        role_router(username)
    else:
        print("❌ Invalid password.")

# Command line interface
if __name__ == "__main__":
    print("\n🧪 ZKP Authentication + Authorization")
    choice = input("Choose [1] Register  [2] Login: ").strip()

    username = input("Enter username: ").strip()
    password = input("Enter password (secret): ").strip()

    if choice == "1":
        print("Available roles: admin, officer, analyst")
        role = input("Enter role: ").strip().lower()
        register_user(username, password, role)
    elif choice == "2":
        login_user(username, password)
    else:
        print("❌ Invalid choice.")
