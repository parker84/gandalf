from groq import Groq
import streamlit as st
import pandas as pd # just in case the agent needs it
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
st.caption('Your friendly neighborhood [Groq](https://groq.com/) wizard who can find **data** and then display it in cool **streamlit** charts 📈.')

data_question_system_prompt = """
You are an expert at translating a general question into a specific data question that can be answered with data.
The output of your response will be directed to another expert who will find that data for you.
"""
data_question_system_messages = [
    {'role': 'system', 'content': data_question_system_prompt},
    {'role': 'user', 'content': 'How has the population of India grown over time?'},
    {'role': 'assistant', 'content': 'Population of India per year from 1921 to 2021'}
]

data_system_prompt = """
You are an expert at finding data and then returning it in a specific format so it can be used to create cool charts.

You always return data in a python dict format something like this:
{
    'Date': ['2020-01-01', '2020-01-02', '2020-01-03'],
    'Population': [100, 200, 300]
}
So that I can call eval() on it and get a python dict object.
Do not return anything else.
"""
data_system_messages = [
    {'role': 'system', 'content': data_system_prompt},
    {'role': 'user', 'content': 'What is the population of India over time?'},
    {'role': 'assistant', 'content': """{
        'Year': ['1921', '1951', '1981', '2001', '2011', '2021'],
        'Population': [251321000, 361088000, 683159652, 1028737436, 1210854977, 1393409038]
    }"""}
]

chart_system_prompt = """
You are an expert at making streamlit charts from data.

Your input will look like this:
{
    'Question': 'What is the population of India over time?',
    'Data': {
        'Year': ['1921', '1951', '1981', '2001', '2011', '2021'],
        'Population': [251321000, 361088000, 683159652, 1028737436, 1210854977, 1393409038]
    }
}

You can assume that Data object will be in a pandas dataframe.

Your job is to return python code that will create a streamlit chart using that data.
Do not return anything but the python code - you can assume that the data will be available in a variable called df.
Streamlit is already imported for you.
Only return python code! nothing else - no text before hand.
"""

chart_system_messages = [
    {'role': 'system', 'content': chart_system_prompt},
    {'role': 'user', 'content': """{
        'Question': 'What is the population of India over time?',
        'Data': {
            'Year': ['1921', '1951', '1981', '2001', '2011', '2021'],
            'Population': [251321000, 361088000, 683159652, 1028737436, 1210854977, 1393409038]
        }
    }"""},
    {'role': 'assistant', 'content': """st.line_chart(df, x='Year', y='Population', title='Population of India over time')"""}
]

def get_data_question(prompt):
    data_question_completion = groq_client.chat.completions.create(
        messages=[{'role': 'user', 'content': prompt}],
        model=GROQ_MODEL,
        temperature=0,
        timeout=TIMEOUT
    ).choices[0].message
    return data_question_completion.content

def get_data(prompt):
    data_completion = groq_client.chat.completions.create(
        messages=data_system_messages + [{'role': 'user', 'content': prompt}],
        model=GROQ_MODEL,
        temperature=0,
        timeout=TIMEOUT
    ).choices[0].message
    output = data_completion.content
    return output

def get_chart(prompt):
    chart_completion = groq_client.chat.completions.create(
        messages=chart_system_messages + [{'role': 'user', 'content': prompt}],
        model=GROQ_MODEL,
        temperature=0,
        timeout=TIMEOUT
    ).choices[0].message
    output = chart_completion.content
    if '```' in output:
        output = output.split('```')[1]
        if 'python' in output:
            output = output.split('python')[1]
    return output

prompt = st.chat_input("Ask me a question...")
if prompt:
    with st.chat_message(name='user', avatar='💻'):
        st.write(prompt)

    with st.status('Thinking...', ):
        data_question = get_data_question(prompt)
        st.write('**Data Question**: ' + data_question)
        data = get_data(data_question)
        st.write('**Data**: \n' + data)
        chart_code = get_chart(data_question)
        st.write('**Code**:')
        st.code(chart_code)
    with st.chat_message(name='ai', avatar='🧙🏻‍♂️'):
        df = eval(data)
        exec(chart_code)

else:
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.write('How has the population of India grown over time?')
    with col2:
        with st.container(border=True):
            st.write('What was the biggest crash in Stock Market history?')
    with col3:
        with st.container(border=True):
            st.write('What are the most popular programming languages?')

