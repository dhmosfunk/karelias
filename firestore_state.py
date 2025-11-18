import firebase_admin
from firebase_admin import credentials, firestore
import os

def init_firestore():
    key_path = os.environ["FIREBASE_KEY_FILE"]
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

def load_seen_ids(db):
    doc = db.collection("msrc_monitor").document("state")
    snap = doc.get()
    if snap.exists:
        return set(snap.to_dict().get("seen", []))
    return set()

def save_seen_ids(db, seen_ids):
    doc = db.collection("msrc_monitor").document("state")
    doc.set({"seen": list(seen_ids)})
