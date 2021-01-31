import json
import os
import string
from functools import partial

import markovify
import streamlit as st

import secrets_beta
from text_model import TextModel

st.set_page_config(layout="wide")

session_state = st.beta_session_state(
    default_key="some_key",
    input_key=0,
    my_todos=[],
    my_finished_tasks=[],
    model=None,
)


def update_model(todo_text=None):
    to_combine = TextModel(todo_text)
    session_state.model = markovify.combine([session_state.model, to_combine])


def render_tasks_and_buttons(column, tasks, button_label, button_action):
    for i, t in enumerate(tasks):
        column.markdown(f"* {t}")
        column.button(
            button_label, key=f"{button_label}{i}", on_click=partial(button_action, i)
        )


def make_suggestion():
    suggestion = session_state.model.make_sentence(tries=100)
    session_state.my_todos.append(suggestion)


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


placeholder = st.empty()
if not session_state.model:
    placeholder.warning("Initializing. Please wait...")
    with open("./issue_titles.txt") as f:
        text = f.read()
    session_state.model = TextModel(text)

placeholder.empty()


st.write("# TODOs and Stuff")

with st.beta_form(submit_label="Submit", key="submit_form"):
    input_placeholder = st.empty()
    todo_text = input_placeholder.text_input(
        "Add a TODO!", key=session_state.input_key
    ).strip()
    share_me = st.checkbox("Help improve our TODO suggestions?", value=True)

    if todo_text:
        session_state.input_key += 1
        session_state.my_todos.append(todo_text)
        input_placeholder.text_input("Add a TODO!", key=session_state.input_key)

        if share_me:
            update_model(todo_text)

st.text("")
st.button("Help! I don't know what to do! :(", on_click=make_suggestion)


col1, col2 = st.beta_columns(2)
todos(col1)
finished_tasks(col2)
