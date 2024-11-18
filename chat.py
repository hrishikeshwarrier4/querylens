import os
import warnings
import sys
import streamlit as st
import unidecode

from helper import display_python_code_plots, display_text_with_images
from agent import create_agent_for_python, create_agent_for_sql


from dotenv import load_dotenv


warnings.filterwarnings("ignore")
current_dir = os.path.dirname(os.path.abspath(__file__)) # Get the directory of the current file

# Test if the SQL agent can execute a simple query directly
# try:
#     test_query = "SELECT COUNT(*) FROM users"  # Replace with a simple test query
#     result = st.session_state.sql_agent.run(test_query)
#     print("Direct SQL Test Result:", result)  # Check if this returns the expected count or an error
# except Exception as e:
#     print("SQL Agent Test Error:", e)

# Define the path relative to the current file
# For example, if the directory to add is the parent directory of the current file
parent_dir = os.path.join(current_dir, "..")

# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

load_dotenv()  # Load environment variables from .env file
# Access the API key from the environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key in the environment variable
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

#os.environ['OPENAI_API_KEY'] = "enter-your-key"

st.set_page_config(page_title="Query Based Analytics")


# # Initialize agents if not already in session state
# if 'agent_memory_sql' not in st.session_state:
#     st.session_state['agent_memory_sql'] = create_agent_for_sql()
# if 'agent_memory_python' not in st.session_state:
#     st.session_state['agent_memory_python'] = create_agent_for_python()

if 'agent_memory' not in st.session_state:
    st.session_state['agent_memory_sql'] = create_agent_for_sql()
    st.session_state['agent_memory_python'] = create_agent_for_python()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []



def reset_conversation():
    st.session_state.messages = []
    st.session_state['agent_memory_sql'] = create_agent_for_sql()
    st.session_state['agent_memory_python'] = create_agent_for_python()
    st.session_state.sql_agent = st.session_state['agent_memory_sql']
    st.session_state.python_agent = st.session_state['agent_memory_python']
    st.session_state.messages.append({"role": "system", "content": "Chat has been reset. You can start a new conversation."})






# Layout improvements
with st.sidebar:
    st.header("Instructions for Using the QueryLens")
    st.write("Welcome to the QueryLens! This platform allows you to interact with data through natural language queries and receive insightful responses or visualizations.")
    st.write("Example prompts:")
    st.write("- 'Show the total sales by year.'")
    st.write("- 'Plot the number of users by country.'")
    if st.button("Reset Chat"):
        reset_conversation()

def generate_response(code_type, input_text):
    """
    Generate a response based on the provided input text and code type.

    This function takes input text and a code type (e.g., "python" or "sql") and generates a response
    using corresponding agents for the given code type.

    Args:
        code_type (str): The type of code to be generated ("python" or "sql").
        input_text (str): The input text to be processed.

    Returns:
        str or dict: The generated response based on the input text and code type. If no response is generated,
        it returns "NO_RESPONSE".
    """
    # prompt = unidecode.unidecode(input_text)
    # try:
    #     if code_type == "python":
    #         response = st.session_state.python_agent.invoke({"input": prompt})['output']
    #         print("Python Response:", response)  # Debugging line
    #     elif code_type == "sql":
    #         response = st.session_state.sql_agent.run(prompt)
    #         print("SQL Response:", response)  # Debugging line
    #     else:
    #         response = "NO_RESPONSE"
    #
    #     # Handle cases where response may be unexpected format
    #     if not response:
    #         return "NO_RESPONSE"
    #
    #     return response
    #
    # except Exception as e:
    #     print(f"Error in generate_response ({code_type}):", e)
    #     return "An error occurred while processing your request."
    prompt = unidecode.unidecode(input_text)
    if code_type == "python":
        try:
            response = st.session_state.sql_agent.invoke({"input": prompt})['output']
            print("Response->", response)
        except:
            return "NO_RESPONSE"
        keywords = ["please provide", "don't know", "more context", "provide more", "vague request"]
        if any(token in response.lower() for token in keywords):
            return "NO_RESPONSE"
        prompt = {"input": "Write a code in python to plot the following data\n\n" + response}
        return st.session_state.python_agent.invoke(prompt)
    else:
        return st.session_state.sql_agent.run(prompt)



if "agent" not in st.session_state:
    st.session_state.sql_agent = st.session_state['agent_memory_sql']
    st.session_state.python_agent = st.session_state['agent_memory_python']


st.title("QueryLens: Query Based Analytics")
col1, col2 = st.columns([3, 1])


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] in ("assistant", "error"):
            display_text_with_images(message["content"])
        elif message["role"] == "plot":
            exec(message["content"])
        else:
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Please ask your question:"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    keywords = ["plot", "graph", "chart", "diagram"]
    if any(token in prompt.lower() for token in keywords):
        prev_context = ""
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "assistant":
                prev_context = msg["content"] + "\n\n" + prev_context
                break
        if len(prev_context) > 0:
            prompt = prompt + "\n\nGiven previous agent responses:\n" + prev_context + "\n"
        response = generate_response("python", prompt)
        if response == "NO_RESPONSE":
            response = "Please try again with a re-phrased query and more context"
            with st.chat_message("error"):
                display_text_with_images(response)
            st.session_state.messages.append(
                {"role": "error", "content": response})
        else:
            code = display_python_code_plots(response['output'])
            try:
                # Check if response is a dictionary and has the 'output' key
                if isinstance(response, dict) and 'output' in response:
                    code = response['output']
                else:
                    code = response

                # Remove any markdown code block markers (e.g., ```python and ```)
                code = code.strip().strip("```").replace("python", "").strip()

                print("Code to execute:", code)  # Debugging line to verify code content

                import time  # Add this import at the top of the file if not already present

                # Generate a unique key using the current timestamp
                unique_key = f"plot_{int(time.time())}"


                # Modify the code to run it with Streamlit
                code = "import pandas as pd\n" + code.replace("fig.show()", "")
                code += f"st.plotly_chart(fig, theme='streamlit', use_container_width=True, key='{unique_key}')"

                # Execute the cleaned code
                exec(code)

                # Add the executed code to chat history for display purposes
                st.session_state.messages.append({"role": "plot", "content": code})

            except Exception as e:
                error_message = f"An error occurred while executing the plot code: {e}"
                print("Plot Execution Error:", error_message)  # Print error for debugging
                with st.chat_message("error"):
                    display_text_with_images(error_message)
                st.session_state.messages.append({"role": "error", "content": error_message})
    else:
        if len(st.session_state.messages) > 1:
            context_length = 0
            prev_context = ""
            for msg in reversed(st.session_state.messages):
                if context_length > 1:
                    break
                if msg["role"] == "assistant":
                    prev_context = msg["content"] + "\n\n" + prev_context
                    context_length += 1
            response = generate_response("sql", prompt + "\n\nGiven previous agent responses:\n" + prev_context + "\n")
        else:
            response = generate_response("sql", prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            display_text_with_images(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})