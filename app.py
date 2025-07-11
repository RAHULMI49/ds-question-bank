import streamlit as st
import json
import random
import os

# Load questions
@st.cache_data
def load_data():
    files = os.listdir("data")
    questions = []
    index = 0
    for file in files:
        with open('data/' + file, "r") as f:
            Q = json.load(f)
            topic = ' '.join(file.split('.')[0].split('_'))
            for q in Q:
                q['id'] = index
                q['topic'] = topic
                questions.append(q)
                index += 1
    return questions


questions = load_data()

# Sidebar filters
topics = sorted(set(q["topic"] for q in questions))
difficulties = sorted(set(q["difficulty"] for q in questions))

selected_topic = st.sidebar.selectbox("Filter by Topic", ["All"] + topics)
selected_difficulty = st.sidebar.selectbox("Filter by Difficulty", ["All"] + difficulties)

if st.sidebar.button("🔄 Refresh"):
    st.session_state.shuffled_questions = None
    st.session_state.q_index = 0
    st.session_state.submitted = False
    st.session_state.selected_option = None
    st.session_state.score = 0
    st.session_state.attempted = 0
    st.rerun()

# Filter questions
filtered_questions = [
    q for q in questions
    if (selected_topic == "All" or q["topic"] == selected_topic)
    and (selected_difficulty == "All" or q["difficulty"] == selected_difficulty)
]

# Shuffles the list randomly

# random.shuffle(filtered_questions) 

# Session state init
if ("shuffled_questions" not in st.session_state):
    st.session_state.shuffled_questions = filtered_questions.copy()
    random.shuffle(st.session_state.shuffled_questions)
elif st.session_state.shuffled_questions is None:
    st.session_state.shuffled_questions = filtered_questions.copy()
    random.shuffle(st.session_state.shuffled_questions)
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "attempted" not in st.session_state:
    st.session_state.attempted = 0

# Title
st.title("📊 Data Science Questions")

# Restart Button
if st.button("🔄 Restart Quiz"):
    st.session_state.shuffled_questions = None
    st.session_state.q_index = 0
    st.session_state.submitted = False
    st.session_state.selected_option = None
    st.session_state.score = 0
    st.session_state.attempted = 0
    st.rerun()

# Main Content
if not filtered_questions:
    st.info("No questions match your filters.")
elif st.session_state.q_index >= len(filtered_questions):
    st.success("🎉 You’ve completed all available questions.")
    st.info(f"🏁 Final Score: {st.session_state.score} / {st.session_state.attempted}")
else:
    q = st.session_state.shuffled_questions[st.session_state.q_index]
    st.markdown(f"###### Topic: {q['topic']}")
    # st.markdown(f"###### Difficulty : {q['difficulty']}")
    st.markdown(f"### {q['question']}")

    options_map = {f"{k}. {v}": k for k, v in q["options"].items()}
    selected_display = st.radio("Select an option:", list(options_map.keys()), key=f"radio_{q['id']}")
    st.session_state.selected_option = options_map[selected_display]

    if st.button("Submit"):
        if not st.session_state.submitted:
            st.session_state.submitted = True
            st.session_state.attempted += 1
            if st.session_state.selected_option == q["answer"]:
                st.session_state.score += 1
                st.success("✅ Correct! " + q["explanation"])
            else:
                correct_text = q["options"][q["answer"]]
                st.error(f"❌ Incorrect. Correct answer is {q['answer']}. {correct_text}\n\n{q['explanation']}")

    # Show score only AFTER submission
    if st.session_state.submitted:
        st.markdown(f"**📈 Score: {st.session_state.score} / {st.session_state.attempted}**")

    # Show Next only after submission
    if st.session_state.submitted:
        if st.button("Next Question"):
            st.session_state.q_index += 1
            st.session_state.submitted = False
            st.session_state.selected_option = None
            st.rerun()
