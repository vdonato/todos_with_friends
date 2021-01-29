import string
from functools import partial

import markovify
import streamlit as st

st.set_page_config(layout="wide")

session_state = st.beta_session_state(
    default_key="some_key",
    input_key=0,
    my_todos=[],
    my_finished_tasks=[],
    model=None,
)


def update_model(todo_text):
    model = session_state.model
    new_model = markovify.Text(todo_text, state_size=1)
    if not model:
        session_state.model = new_model
    else:
        session_state.model = markovify.combine([model, new_model])


def render_tasks_and_buttons(tasks, button_label, button_action):
    for i, t in enumerate(tasks):
        col.markdown(f"* {t}")
        col.button(
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
        tasks=session_state.my_todos,
        button_label="Mark Done",
        button_action=move_to_finished,
    )


def finished_tasks(col):
    col.write("### My Finished Tasks")
    render_tasks_and_buttons(
        tasks=session_state.my_finished_tasks,
        button_label="Remove",
        button_action=remove_finished_task,
    )


st.write("# TODOs and Stuff")

if session_state.model:
    suggestion = session_state.model.make_sentence()
    if suggestion:
        if suggestion[-1] in string.punctuation:
            suggestion = suggestion[:-1]

        st.write(f"Don't know what to do? Why not...")
        st.write(f"{suggestion}?")

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
        pass

col1, col2 = st.beta_columns(2)
todos(col1)
finished_tasks(col2)
