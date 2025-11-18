import firebase_admin
from firebase_admin import credentials, firestore
import os

def init_firestore():
    key_path = os.environ["FIREBASE_KEY_FILE"]
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

def load_seen_ids(db, source):
    doc = db.collection("cve_sources").document(source)
    snap = doc.get()
    if snap.exists:
        return set(snap.to_dict().get("seen", []))
    return set()

def save_seen_ids(db, source, seen_ids):
    doc = db.collection("cve_sources").document(source)
    doc.set({"seen": list(seen_ids)})
