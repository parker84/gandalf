from groq import Groq
import streamlit as st
from decouple import config
import logging, coloredlogs
logger = logging.getLogger(__name__)
coloredlogs.install(level=config('LOG_LEVEL', 'INFO'), logger=logger)


GROQ_MODEL = 'mixtral-8x7b-32768'
TIMEOUT = 120
groq_client = Groq(
    api_key=config('GROQ_API_KEY'),
)

st.set_page_config(
    page_title='Gandalf',
    page_icon='🪄',
    initial_sidebar_state='collapsed'
)

st.title('🧙🏻‍♂️ Gandalf')
st.caption('Your friendly neighborhood [Groq](https://groq.com/) wizard.')

prompt = st.chat_input("Ask me a question...")
if prompt:
    with st.chat_message(name='user', avatar='💻'):
        st.write(prompt)

    with st.status('Thinking...', ):
        chat_completion = groq_client.chat.completions.create(
            messages=[{'role': 'user', 'content': prompt}],
            model=GROQ_MODEL,
            temperature=0,
            timeout=TIMEOUT
        ).choices[0].message
    with st.chat_message(name='ai', avatar='🧙🏻‍♂️'):
        st.write(chat_completion.content)

else:
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.write('What is the population of India?')
    with col2:
        with st.container(border=True):
            st.write('What is the capital of France?')
    with col3:
        with st.container(border=True):
            st.write('What is the currency of Japan?')

