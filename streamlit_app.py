import streamlit as st
import pandas as pd
import os
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_groq import ChatGroq
import os

os.environ["GROQ_API_KEY"] = "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" # REPLACE THIS WITH YOUR ACTUAL GROQ API KEY

st.set_page_config(page_title="CSV Chatbot")
st.header("Chat with your CSV 💬")

# Initialize chat history in session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Save the uploaded file temporarily
    file_path = os.path.join("uploads", uploaded_file.name)
    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Initialize the Groq model
    llm = ChatGroq(temperature=0, model_name="llama3-70b-8192")

    # Create the CSV agent
    agent = create_csv_agent(
            llm,
            file_path,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            allow_dangerous_code=True,
            handle_parsing_errors=True,
        )

    # Accept user input
    if prompt := st.chat_input("What do you want to know about the CSV?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = agent.run(prompt)
                    st.markdown(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
else:
    st.info("Please upload a CSV file to start chatting.")
