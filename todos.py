import streamlit as st

st.set_page_config(layout="wide")

session_state = st.beta_session_state(
    default_key="some_key",
    input_key=0,
    my_todos=[],
    my_finished_tasks=[],
    our_todos=[],
    our_finished_tasks=[],
)


def todos(col):
    col.write("### My TODOs")


def finished_tasks(col):
    col.write("### My Finished Tasks")


def public_todos(col):
    col.write("### Public TODOs")


def public_finished_tasks(col):
    col.write("### Public Finished Tasks")


render_funcs = [todos, finished_tasks, public_todos, public_finished_tasks]


st.write("# TODOs and Stuff")

# TODO: markov-generated todo suggestions (lol)

with st.beta_form(submit_label="Submit", key="submit_form"):
    input_placeholder = st.empty()
    todo_text = input_placeholder.text_input(
        "Add a TODO!", key=session_state.input_key
    ).strip()
    share_me = st.checkbox("Share with the World?")

    if todo_text:
        session_state.input_key += 1
        session_state.my_todos.append(todo_text)
        input_placeholder.text_input("Add a TODO!", key=session_state.input_key)

columns = st.beta_columns(4)

for fn, col in zip(render_funcs, columns):
    fn(col)
