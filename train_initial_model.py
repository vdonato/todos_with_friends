import firebase_admin
import markovify
from firebase_admin import credentials, firestore

from text_model import TextModel

creds = credentials.Certificate("./firestore-key.json")
firebase_admin.initialize_app(creds)
db = firestore.client()

with open("./issue_titles.txt") as f:
    text = f.read()

model = TextModel(text)
db.collection("models").document("initial_model").set({"json_string": model.to_json()})
