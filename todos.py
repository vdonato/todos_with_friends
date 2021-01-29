import json
import os
import string
from functools import partial

import firebase_admin
import markovify
from firebase_admin import credentials, firestore
import streamlit as st

import secrets_beta
from text_model import TextModel

st.set_page_config(layout="wide")

TMP_CREDS_PATH = "/tmp/todo_creds.json"


@st.cache
def firestore_setup():
    creds_dict = json.loads(st.secrets["firestore_key"])

    with open(TMP_CREDS_PATH, "w") as f:
        json.dump(creds_dict, f)
        f.write("\n")

    creds = credentials.Certificate(TMP_CREDS_PATH)
    firebase_admin.initialize_app(creds)

    os.remove(TMP_CREDS_PATH)

    return st.secrets["firestore_key"]


firestore_setup()
db = firestore.client()
todos_collection = db.collection("todos")

session_state = st.beta_session_state(
    default_key="some_key",
    input_key=0,
    my_todos=[],
    my_finished_tasks=[],
    model=None,
)


def update_model(todo_text=None):
    if not session_state.model:
        serialized_model = (
            db.collection("models").document("model").get().to_dict()["json_string"]
        )
        session_state.model = TextModel.from_json(serialized_model)
    if todo_text:
        to_combine = TextModel(todo_text, state_size)
        session_state.model = markovify.combine([session_state.model, to_combine])


def render_tasks_and_buttons(column, tasks, button_label, button_action):
    for i, t in enumerate(tasks):
        column.markdown(f"* {t}")
        column.button(
            button_label, key=f"{button_label}{i}", on_click=partial(button_action, i)
        )


def move_to_finished(i):
    move_me = session_state.my_todos.pop(i)
    session_state.my_finished_tasks.append(move_me)


def remove_finished_task(i):
    session_state.my_finished_tasks.pop(i)


def todos(col):
    col.write("### My TODOs")
    render_tasks_and_buttons(
        column=col,
        tasks=session_state.my_todos,
        button_label="Mark Done",
        button_action=move_to_finished,
    )


def finished_tasks(col):
    col.write("### My Finished Tasks")
    render_tasks_and_buttons(
        column=col,
        tasks=session_state.my_finished_tasks,
        button_label="Remove",
        button_action=remove_finished_task,
    )


update_model()
st.write("# TODOs and Stuff")

if session_state.model:
    suggestion = session_state.model.make_sentence(tries=100)
    if suggestion:
        if suggestion[-1] in string.punctuation:
            suggestion = suggestion[:-1]

        st.write(f"Don't know what to do? Why not work on...")
        st.write(f"`{suggestion}`?")

with st.beta_form(submit_label="Submit", key="submit_form"):
    input_placeholder = st.empty()
    todo_text = input_placeholder.text_input(
        "Add a TODO!", key=session_state.input_key
    ).strip()
    share_me = st.checkbox("Contribute to the Hivemind?", value=True)

    if todo_text:
        session_state.input_key += 1
        session_state.my_todos.append(todo_text)
        update_model(todo_text)
        input_placeholder.text_input("Add a TODO!", key=session_state.input_key)

        if share_me:
            doc_ref = todos_collection.document()
            doc_ref.set({"text": todo_text})


col1, col2 = st.beta_columns(2)
todos(col1)
finished_tasks(col2)
