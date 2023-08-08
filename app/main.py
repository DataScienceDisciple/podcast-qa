import streamlit as st
import os
import vecs

from loguru import logger
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas as pd

# from src.llm.qa.local_qa_engine import LocalQAEngine, EmbeddingModel
from src.llm.qa.postgres_qa_engine import PostgresQAEngine, EmbeddingModel
from src.api.client import call_answer_hubermanlab, call_resource_hubermanlab
from src.service.service import answer_response_to_html, resource_response_to_html
from dotenv import load_dotenv, set_key

load_dotenv()


DB_CONNECTION = f"postgresql://postgres:{os.environ['POSTGRES_DB_PASS']}@{os.environ['POSTGRES_DB_HOST']}:5432/postgres"
USER_ID = 1

custom_css = """
<style>
    body {
        background-color: #f4f4f4;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextInput input[type="text"] {
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
    }
    .sidebar .sidebar-content {
        padding: 15px;
        background-color: #fff;
        border-radius: 10px;
        box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
    }
    .stMarkdown img {
        height: 30px;
        margin: 0 5px;
        vertical-align: text-bottom; /* Align icons with the bottom of the text line */
    }
    .stMarkdown a {
        display: inline-flex;
        align-items: center;
    }
    .stInfo {
        background-color: #f0f4f8;
        padding: 10px 20px;
        border-radius: 5px;
        border: 1px solid #ccc;
    }
    #connect-section {
        text-align: center;
    }
</style>
"""

embedding_model = EmbeddingModel("sbert")


def create_db_engine():
    engine = create_engine(DB_CONNECTION)
    Session = sessionmaker(bind=engine)

    # start a new session
    session = Session()

    # create vector store client
    vx = vecs.create_client(DB_CONNECTION)
    qa_engine = PostgresQAEngine(embedding_model=embedding_model,
                                 sql_session=session,
                                 vecs_client=vx,
                                 vecs_collection_name="docs")
    return qa_engine


def on_api_key_change():
    os.environ['OPENAI_API_KEY'] = st.session_state.get('api_key')


def ui_spacer(n=2, line=False, next_n=0):
    for _ in range(n):
        st.write('')
    if line:
        st.tabs([' '])
    for _ in range(next_n):
        st.write('')


def api_key_panel():
    st.write("## Enter your OpenAI API key")
    st.text_input("OpenAI API key", type="password", key="api_key",
                  on_change=on_api_key_change, label_visibility="collapsed")
    st.write("### Don't know how?")
    st.markdown(
        "[Watch this quick YouTube Video](https://www.youtube.com/watch?v=nafDyRsVnXU)")


def main_layout():
    st.markdown("# PodcastGPT Engine 🎙️")
    st.markdown(
        "Welcome to the PodcastGPT Engine! Choose a mode below to get started.")

    with st.sidebar:
        with st.expander("### Currently Supported Podcast: HubermanLab Podcast 🧠", expanded=False):
            st.info(
                """
                The PodcastGPT Engine is specially designed for the [**HubermanLab podcast**](https://www.youtube.com/@hubermanlab), which focuses on health and performance-related subjects. This means you'll get the most precise answers for questions in these areas:

                - Meditation, Focus, and Cognitive Training
                - Physical Performance and Recovery
                - Nutrition, Supplements, and Metabolic Health
                - Mental Health and Emotional Resilience
                - Sleep, Circadian Rhythms and Light
                - Neuroscience, Biohacking, and Health Monitoring
                - Relationships, Social Dynamics, and Personal Development
                - Taste, Smell, and Perception
                - Gut Health and Microbiome

                More podcasts will be supported in the future, and we welcome your suggestions for adding your favorite shows (DM me on Twitter(X))!
                """
            )
        st.markdown("### Configure API key 🔑")
        with st.expander('Click here to enter OpenAI API key 🛠️'):
            api_key_panel()
        # Some space before the coffee link
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### FAQ")

        # Initialize session state variable if it doesn't exist
        if 'show_faq' not in st.session_state:
            st.session_state.show_faq = False

        # Create a placeholder for the button
        btn_placeholder = st.empty()
        # Determine the label for the button
        btn_label = "Hide FAQ" if st.session_state.show_faq else "Show FAQ"
        # Create the button in the placeholder
        if btn_placeholder.button(btn_label):
            # Update the session state variable
            st.session_state.show_faq = not st.session_state.show_faq
            # Update the button label
            btn_label = "Hide FAQ" if st.session_state.show_faq else "Show FAQ"
            # Re-create the button with the new label
            btn_placeholder.button(btn_label)

        if st.session_state.show_faq:
            st.markdown("# FAQ")
            st.markdown("Here are some common questions and answers:")
            st.markdown("""
                **1. What is PodcastGPT Engine?**

                PodcastGPT Engine is an AI-powered tool that helps identify relevant podcast sections from the supported list of podcasts and can construct answers to specific questions. Currently, the database contains only [HubermanLab podcast](https://www.youtube.com/@hubermanlab). That means, health and performance related questions will be answered most accurately.

                **2. Which podcasts are supported?**

                Currently, the PodcastGPT Engine exclusively supports the [HubermanLab podcast](https://www.youtube.com/@hubermanlab). That means the questions should revolve around these topics:
                - Meditation, Focus, and Cognitive Training
                - Physical Performance and Recovery
                - Nutrition, Supplements, and Metabolic Health
                - Mental Health and Emotional Resilience
                - Sleep, Circadian Rhythms and Light
                - Neuroscience, Biohacking, and Health Monitoring
                - Relationships, Social Dynamics, and Personal Development
                - Taste, Smell, and Perception
                - Gut Health and Microbiome 
                
                However, I'm actively working on extending the database to other podcasts in the future. If you have a favorite podcast that you'd like to see supported, please don't hesitate to contact me!

                **3. How do I use Resource Mode and Question Mode?**

                In Resource Mode, the engine identifies relevant podcast sections without constructing a final answer. That means you will get resources that you should listen to if you want to learn more about a specific topic. Question Mode also identifies relevant sections but also constructs the final answer using ChatGPT. This results in a better, more actionable information. However, it requires configuring OpenAI API keys.

                **4. How do I get an OpenAI API key?**

                You can enter your OpenAI API key in the left panel under the "Configure API key" section. If you don't know how to obtain the key, watch this [video](https://www.youtube.com/watch?v=nafDyRsVnXU).

                **5. Why am I not getting an answer in Question Mode?**

                For Question Mode, valid API keys are required. Please ensure that you have provided them in the left panel.

                **6. How long does it take to process a question?**

                Processing a question can take up to a minute, depending on the mode and how well it is represented in the database. The resource mode will be a lot faster since we don't call OpenAI API.

                **7. What are the limitations of PodcastGPT Engine?**

                PodcastGPT Engine can answer questions only related to topics presented in the podcasts that are currently supported. As of now, the engine can answer only the answers regarding [HubermanLab podcast](https://www.youtube.com/@hubermanlab). That means, health and performance related questions will be answered most accurately.
            """)

        st.markdown("### Connect with Me 🌐")
        st.markdown(
            "<a href='https://twitter.com/Olearningcurve' target='_blank'><img src='https://seeklogo.com/images/T/twitter-x-logo-0339F999CF-seeklogo.com.png?v=638264860180000000' height='30' alt='Twitter' style='margin:5px' /></a> "
            "<a href='https://www.youtube.com/channel/UClYzGYx6gmntp7TVFU2AGDg' target='_blank'><img src='https://www.iconpacks.net/icons/2/free-youtube-logo-icon-2431-thumb.png' height='30' alt='LinkedIn' style='margin:5px' /></a> "
            "<a href='https://ko-fi.com/V7V6I2E05' target='_blank'><img height='30' style='border:0px;height:30px; margin:5px;' src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>",
            unsafe_allow_html=True)

    modes = {"Resource Mode": "Resource Mode 📚",
             "Question Mode": "Question Mode 🧠"}
    mode = st.radio("Choose a Mode:", list(modes.keys()))
    selected_mode = modes[mode]

    with st.container():
        st.markdown("### " + selected_mode)
        if mode == "Resource Mode":
            st.info(
                """
                🎙️  Identifies relevant podcast sections.

                ❌  Does not construct a final answer.

                🔓  No API keys needed.

                **Output:** You'll receive 7 sections for deeper analysis.
                """
            )
        elif mode == "Question Mode":
            st.info(
                """
                🎙️  Identifies relevant podcast sections.

                ✅  Constructs a final answer with ChatGPT.

                🔑  API keys required.

                **Output:** You'll receive 3 sections and a precise answer based on them.
                """
            )

        input_text = st.text_area(label="🖋️ Ask a question:",
                                  placeholder="Your question, e.g. How to sleep better?", key="user_input")

        run_button = st.button("Run 🚀")

        if input_text and run_button:
            with st.spinner('Processing...'):
                st.write(
                    "🕓 Your question is being processed. It can take up to a minute.")
                st.markdown(f"## {input_text}")

                if mode.endswith("Question Mode") and st.session_state.get('api_key'):
                    answer_response = call_answer_hubermanlab(
                        USER_ID, input_text, st.session_state.get('api_key'))
                    st.markdown(answer_response_to_html(
                        answer_response=answer_response), unsafe_allow_html=True)
                elif mode.endswith("Resource Mode"):
                    resource_response = call_resource_hubermanlab(
                        USER_ID, input_text)
                    st.markdown(resource_response_to_html(
                        resource_response=resource_response), unsafe_allow_html=True)
                elif mode.endswith("Question Mode") and not st.session_state.get('api_key'):
                    st.error(
                        "🚫 For Question Mode, API Keys are required. Please provide them in the left panel.")

        st.markdown("---")

        st.markdown(
            "##### Connect with Me 🌐")
        st.markdown(
            "<a href='https://twitter.com/Olearningcurve' target='_blank'><img src='https://seeklogo.com/images/T/twitter-x-logo-0339F999CF-seeklogo.com.png?v=638264860180000000' height='30' alt='Twitter' style='margin:5px' /></a> "
            "<a href='https://www.youtube.com/channel/UClYzGYx6gmntp7TVFU2AGDg' target='_blank'><img src='https://www.iconpacks.net/icons/2/free-youtube-logo-icon-2431-thumb.png' height='30' alt='LinkedIn' style='margin:5px' /></a> "
            "<a href='https://ko-fi.com/V7V6I2E05' target='_blank'><img height='30' style='border:0px;height:30px; margin:5px;' src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>",
            unsafe_allow_html=True)

        st.markdown(
            "Made with :heart: by Luke Skyward")


# UI
st.set_page_config(page_title="Podcast QA AI Engine",
                   page_icon="🎙️")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.markdown(custom_css, unsafe_allow_html=True)
main_layout()
