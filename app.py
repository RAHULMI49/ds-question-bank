import streamlit as st
import json
import random
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
# creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open the sheet
sheet = client.open("DS subscribers").sheet1

# Save function
def save_subscriber(name, email):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([name, email, timestamp])




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

selected_topic = st.sidebar.selectbox("Filter by Topic", topics + ["All"])
selected_difficulty = st.sidebar.selectbox("Filter by Difficulty", difficulties + ["All"])

if st.sidebar.button("🔄 Filter"):
    st.session_state.shuffled_questions = None
    st.session_state.q_index = 0
    st.session_state.submitted = False
    st.session_state.selected_option = None
    st.session_state.score = 0
    st.session_state.attempted = 0
    st.session_state.quiz_ended = False
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
if "quiz_ended" not in st.session_state:
    st.session_state.quiz_ended = False


# Title
st.title("📊 The Data Science Practice Quiz")

st.markdown("""
Welcome to the DailyDS — your one-stop app to practice and master **Machine Learning**, **Statistics**, **Deep Learning**, and **Python**.
""")
st.write("📬 Subscribe to get 1 question in your inbox every day")

col1, col2, col3 = st.columns([1.5, 2, 1])  # Adjust widths for name, email, button

with col1:
    name = st.text_input(" ", placeholder="Name", label_visibility="collapsed")

with col2:
    email = st.text_input(" ", placeholder="Email", label_visibility="collapsed")

with col3:
    subscribe = st.button("Subscribe")

if subscribe:
    if name and email:
        save_subscriber(name, email)
        st.success(f"Thanks {name}! You're subscribed. ✅")
        # Save logic here
    else:
        st.warning("Please enter both name and email.")

# Main Content
if not filtered_questions:
    st.info("No questions match your filters.")
elif st.session_state.q_index >= len(filtered_questions):
    st.success("🎉 You’ve completed all available questions.")
    st.info(f"🏁 Final Score: {st.session_state.score} / {st.session_state.attempted}")
elif st.session_state.quiz_ended:
    st.markdown("## 🧾 Quiz Summary")
    st.write(f"✅ **Score:** {st.session_state.score}")
    st.write(f"📊 **Questions Attempted:** {st.session_state.attempted}")
    st.write(f"⏭️ **Questions Skipped:** {st.session_state.q_index - st.session_state.attempted}")

    if st.button("🔄 Restart"):
        st.session_state.shuffled_questions = None
        st.session_state.q_index = 0
        st.session_state.submitted = False
        st.session_state.selected_option = None
        st.session_state.score = 0
        st.session_state.attempted = 0
        st.session_state.quiz_ended = False
        st.rerun()
else:
    q = st.session_state.shuffled_questions[st.session_state.q_index]
    st.markdown(f"###### Topic: {q['topic']}")
    # st.markdown(f"###### Difficulty : {q['difficulty']}")
    st.markdown(f"### {st.session_state.q_index + 1}. {q['question']}")

    options_map = {f"{k}. {v}": k for k, v in q["options"].items()}
    selected_display = st.radio("Select an option:", list(options_map.keys()), key=f"radio_{q['id']}")
    st.session_state.selected_option = options_map[selected_display]

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
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
    
    with col2:
        if not st.session_state.submitted:
            if st.button("⏭️ Skip Question"):
                st.session_state.q_index += 1
                st.session_state.submitted = False
                st.session_state.selected_option = None
                st.rerun()
        else:
            if st.button("Next Question"):
                st.session_state.q_index += 1
                st.session_state.submitted = False
                st.session_state.selected_option = None
                st.rerun()
    with col3:
        if st.button("🛑 End Quiz"):
            st.session_state.quiz_ended = True
            st.rerun()
    

    # Show score only AFTER submission
    if st.session_state.submitted:
        st.markdown(f"**📈 Score: {st.session_state.score} / {st.session_state.attempted}**")
        
