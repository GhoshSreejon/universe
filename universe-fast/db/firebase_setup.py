# db/firebase_setup.py
import firebase_admin
from firebase_admin import credentials, firestore

# Load credentials from file
cred = credentials.Certificate("firebase/universal-8e6cf-firebase-adminsdk-fbsvc-dd1685b323.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def save_journal_entry(user_id: str, text: str, mood: str):
    entry = {
        "text": text,
        "mood": mood,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection("journals").document(user_id).collection("entries").add(entry)

def fetch_journal_entries(user_id: str):
    docs = db.collection("journals").document(user_id).collection("entries") \
        .order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    return [{"text": doc.to_dict()["text"], "mood": doc.to_dict()["mood"]} for doc in docs]
