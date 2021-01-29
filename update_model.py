import string
import time

import firebase_admin
import markovify
from firebase_admin import credentials, firestore

from text_model import TextModel

creds = credentials.Certificate("./firestore-key.json")
firebase_admin.initialize_app(creds)
db = firestore.client()

models_collection = db.collection("models")
todos_collection = db.collection("todos")


def update_model():
    model_ref = models_collection.document("model")
    if not model_ref.get().exists:
        initial_model = models_collection.document("initial_model").get().to_dict()
        model_ref.set({"json_string": initial_model["json_string"]})

    todos = todos_collection.stream()
    to_add = []

    for t in todos:
        t_id = t.id
        text = t.to_dict()["text"]

        # Add some punctuation if not present to help separate different TODOs.
        if text[-1] not in string.punctuation:
            text += "."

        to_add.append(text)
        todos_collection.document(t_id).delete()

    if to_add:
        to_merge = TextModel("\t".join(to_add))

        serialized_model = model_ref.get().to_dict()["json_string"]
        old_model = TextModel.from_json(serialized_model)

        new_model = markovify.combine([old_model, to_merge])
        model_ref.set({"json_string": new_model.to_json()})


while True:
    start_time = time.time()
    print("Updating model with new TODOs.")
    update_model()
    print(f"Finished updating model in {time.time() - start_time} seconds")
    time.sleep(3 * 60)
