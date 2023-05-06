import streamlit as st
from streamlit_chat import message
import os
from langchain import LLMChain, OpenAI
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from llama_index.indices.struct_store import GPTPandasIndex
import pandas as pd
from snowflake.connector import connect


#Set page config
st.set_page_config(
    page_title="Data ChatBot",
    page_icon="🗨️",
)

#Set page title
st.title("🗨️ Data Chatbot")
st.markdown("Type a question in the box below and hit submit to ask the AI bot a question about your data. \
            \nThe bot will remember context from prior questions. \
            \nClick Clear chat to clear context.")

st.divider()

st.dataframe(st.session_state.df)

open_ai_key = st.secrets['api_key']["open_ai_key"]
os.environ['OPENAI_API_KEY'] = open_ai_key

    # Create an OpenAI instance
llm = OpenAI(temperature=0, 
            model_name='gpt-3.5-turbo', 
            verbose=False) 


index = GPTPandasIndex(df=st.session_state.df)

query_engine = index.as_query_engine(
    verbose=True
)

tools = [
    Tool(
        name="Pandas",
        func=lambda q: query_engine.query(q),
        description=f"Useful when you want answer questions using the pandas dataframe",
    )
]

prefix = """Have a conversation with a human, answering the following questions as best you can based on the context and memory available. 
                Names in the question may be mispelled, the wrong case or synonyms.
                You have access to a single tool:"""
suffix = """Begin!
            {chat_history}
            Question: {input}
            {agent_scratchpad}"""

prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )

if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(
    memory_key="chat_history"
    )

llm_chain = LLMChain(
            llm=OpenAI(
                temperature=0, openai_api_key=open_ai_key, model_name="gpt-3.5-turbo"
            ),
            prompt=prompt,
        )

agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)

agent_chain = AgentExecutor.from_agent_and_tools(
                agent=agent, tools=tools, verbose=True, memory=st.session_state.memory
            )



if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

if 'cbot_query' not in st.session_state:
    st.session_state["cbot_query"] = ""

if 'input_bx' not in st.session_state:
    st.session_state["input_bx"] = ""

if 'ask_q' not in st.session_state:
    st.session_state["ask_q"] = False


def refresh_chain():
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["buffer"] = []
    st.session_state["memory"] = ConversationBufferMemory(memory_key="chat_history")

def message_func():
    if st.session_state["generated"]:
        for i in range(len(st.session_state["generated"]) - 1, -1, -1):
            message(st.session_state["generated"][i], is_user=True, avatar_style='bottts', key=str(i),seed=105)
            message(st.session_state["past"][i], is_user=False, avatar_style='personas' ,key=str(i) + "_user",seed=103)

def submit():
     st.session_state["cbot_query"] = st.session_state["input_bx"]
     st.session_state["input_bx"] = ''
     st.session_state["ask_q"] = True

query = st.text_input(
                "**What would you like to know?**",
                placeholder="Ask me a question about your dataset",
                key='input_bx',
                on_change=submit()
            )

st.button(label='Clear Chat', on_click=refresh_chain)

if st.session_state["ask_q"] and st.session_state["cbot_query"] != '':
    with st.spinner("Generating Answer to your Query : `{}` ".format(st.session_state["cbot_query"])):
        st.divider()
        try:
            output = agent_chain.run(st.session_state["cbot_query"])
            if not st.session_state["past"]:
                st.session_state["past"] = []
            if not st.session_state["generated"]:
                st.session_state["generated"] = []
            st.session_state["past"].append(st.session_state["cbot_query"])
            st.session_state["generated"].append(output)
        except:
            output = "I can't answer that sorry. Ensure your question is specific and about the data."
            st.session_state["past"].append(st.session_state["cbot_query"])
            st.session_state["generated"].append(output)
        message_func()
        st.session_state["ask_q"] = False

