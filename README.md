# Encrypted-Federated-Search-for-Law-Enforcement-Intelligence-Agencies-Using-Homomorphic-Encryption

This is a **secure search system** built for **law enforcement and intelligence agencies**. It allows officers to search criminal data **without revealing the actual data or the search terms** using **Homomorphic Encryption**.

Each city (like Mumbai, Delhi, Chennai) has its own encrypted database. When someone searches, all data remains encrypted — only the final result is decrypted. All searches are **recorded using Blockchain**, and different users (Admin, Officer, Analyst) have different roles.

---

## 🖥️ What You’ll See (Add Screenshots Here)

**Landing page**
![image](https://github.com/user-attachments/assets/b54476de-58e9-45c6-adad-0b0ce18d5dd2)

**Query Search**
![image](https://github.com/user-attachments/assets/af32789b-88c7-444b-bba5-116ede953059)

**Query Result**
![image](https://github.com/user-attachments/assets/96c25396-b8c6-440f-be35-4ad450d63f75)

**Blockchain Logging**
![image](https://github.com/user-attachments/assets/9e224ba8-4201-4a96-80a0-290280ac35da)

**MongoDB**
![image](https://github.com/user-attachments/assets/353af0c4-6ee5-4944-83cc-a8a0f32fc4ba)


📌 *Add a screenshot of MongoDB collections here*

---

## ✅ Features (in Simple Terms)

- **Encrypted Data & Searches**  
  Nobody can see your data or what you search for.

- **Multiple City Databases**  
  Data is stored separately for Mumbai, Delhi, and Chennai.

- **Secure Login**  
  Users log in with roles like Admin, Officer, or Analyst.

- **Blockchain Logging**  
  Every search is recorded forever so no one can deny it later.

- **Simple Web Interface**  
  You can use everything through an easy Streamlit app.

---

## 🧑‍💼 User Roles

| Role     | What They Can Do                         |
|----------|------------------------------------------|
| Admin    | Register other users                     |
| Officer  | Perform encrypted search                 |
| Analyst  | View search logs (Blockchain ledger)     |

---

## ▶️ How to Run

1. **Install Required Packages**
```bash
pip install -r requirements.txt
```
2. Start MongoDB
Make sure MongoDB is running on your computer (localhost:27017).

3. Run the Web App
```bash
streamlit run streamlit_app.py
```
4. Use the Interface
Login with one of the roles and start exploring.

