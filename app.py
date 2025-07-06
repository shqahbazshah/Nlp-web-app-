import nltk

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import streamlit as st
import json
import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Sentiment & Emotion APIs
class Api:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.api_key = "UnsBKoIBMCVzT1y0beOGPgrgDCjDZE8b"

    def sentiment(self, text):
        scores = self.analyzer.polarity_scores(text)
        return scores

    def emotion_detection(self, text):
        url = "https://api.apilayer.com/text_to_emotion"
        payload = text.encode("utf-8")
        headers = {"apikey": self.api_key, "Content-Type": "text/plain"}
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}

# Local JSON Database
class Data:
    def __init__(self):
        self.db_path = 'db.json'
        with open(self.db_path, 'r') as f:
            self.database = json.load(f)

    def save_db(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.database, f, indent=4)

    def add_data(self, name, email, password):
        if email in self.database:
            return 0
        else:
            self.database[email] = [name, password]
            self.save_db()
            return 1

    def search(self, email, password):
        if email in self.database and self.database[email][1] == password:
            return 1
        return 0

# App Logic
api = Api()
dbo = Data()

st.set_page_config(page_title="NLP Web App", page_icon="💬")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Registration
def register():
    st.title("📝 Register")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        res = dbo.add_data(name, email, password)
        if res:
            st.success("Registered Successfully! You can log in now.")
        else:
            st.error("Email already exists!")

# Login
def login():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = dbo.search(email, password)
        if res:
            st.session_state.logged_in = True
            st.session_state.email = email
            st.success("Logged in successfully!")
        else:
            st.error("Invalid Email/Password")

# Home
def home():
    st.title("🏠 NLP Web App")

    menu = st.sidebar.radio("Menu", ["Sentiment Analysis", "Emotion Detection", "Logout"])

    if menu == "Sentiment Analysis":
        st.subheader("📝 Sentiment Analysis")
        text = st.text_area("Enter Text:")
        if st.button("Analyze Sentiment"):
            result = api.sentiment(text)
            st.write(f"**Positive:** {result['pos']}")
            st.write(f"**Neutral:** {result['neu']}")
            st.write(f"**Negative:** {result['neg']}")
            st.write(f"**Compound:** {result['compound']}")

    elif menu == "Emotion Detection":
        st.subheader("🎭 Emotion Detection")
        text = st.text_area("Enter Text:")
        if st.button("Analyze Emotions"):
            result = api.emotion_detection(text)
            if "error" in result:
                st.error(result["error"])
            else:
                for emotion, score in result.items():
                    st.write(f"**{emotion}:** {score:.2f}")

    elif menu == "Logout":
        st.session_state.logged_in = False


# Main
if not st.session_state.logged_in:
    option = st.sidebar.radio("Select", ["Login", "Register"])
    if option == "Login":
        login()
    else:
        register()
else:
    home()
