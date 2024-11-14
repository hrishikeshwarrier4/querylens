from async_timeout import timeout
from langchain import hub
#xfrom langchain.agents import AgentExecutor
from langchain.agents import initialize_agent, AgentExecutor , create_openai_functions_agent

#from langchain.agents.openai_functions_agent import create_openai_functions_agent
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.utilities import SQLDatabase
#from langchain.tools import PythonREPLTool
from langchain_experimental.tools import PythonREPLTool
#from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI

#import pymysql
#from langchain_openai import ChatOpenAI

CUSTOM_SUFFIX = """Begin!

Relevant pieces of previous conversation:
{chat_history}
(Note: Only reference this information if it is relevant to the current query.)

Question: {input}

Thought Process: I will follow these steps:
- Ensure that I do not fabricate information or engage in hallucination; maintaining trustworthiness is crucial.
- Identify and validate the data relevant to the query.
- If the current question requires using data from the previous query, identify and reuse that data.
- Outline a clear, step-by-step plan based on available data.
- Execute the plan, checking each intermediate step to ensure it aligns with known data and logical inference.
- Use the `LOWER()` function for case-insensitive comparisons and the `LIKE` operator for fuzzy matching in SQL queries involving string or TEXT comparisons.
- Return percentage is defined as the total number of returns divided by the total number of orders. I can join the `orders` table with the `users` table to get more detailed user information.
- Ensure that the query is relevant to the SQL database schema and the available tables.
- If the result is empty, the response should be "No results found". I must not create or assume data if no result exists.

My final response should be the exact output of the SQL query, or "No results found" if there is no matching data.

{agent_scratchpad}
"""




langchain_chat_kwargs = {
    "temperature": 0,
    "max_tokens": 4000,
    "verbose": True,
}
chat_openai_model_kwargs = {
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": -1,
}

# Code if you've set up password in mysql
import urllib.parse

password = urllib.parse.quote_plus("gugegush")  # Replace "your#password" with your actual password
db = SQLDatabase.from_uri(f"mysql+pymysql://root:{password}@localhost:3306/ecommerce")



#db = SQLDatabase.from_uri("mysql://localhost:3306/ecommerce?user=root")


def get_chat_openai(model_name):
    """
    Returns an instance of the ChatOpenAI class initialized with the specified model name.

    Args:
        model_name (str): The name of the model to use.

    Returns:
        ChatOpenAI: An instance of the ChatOpenAI class.

    """
    llm = ChatOpenAI(
        model_name=model_name,
        model_kwargs=chat_openai_model_kwargs,
        timeout=300,
        **langchain_chat_kwargs
    )
    return llm


def get_sql_toolkit(tool_llm_name: str):
    """
    Instantiates a SQLDatabaseToolkit object with the specified language model.

    This function creates a SQLDatabaseToolkit object configured with a language model
    obtained by the provided model name. The SQLDatabaseToolkit facilitates SQL query
    generation and interaction with a database.

    Args:
        tool_llm_name (str): The name or identifier of the language model to be used.

    Returns:
        SQLDatabaseToolkit: An instance of SQLDatabaseToolkit initialized with the provided language model.
    """
    llm_tool = get_chat_openai(model_name=tool_llm_name)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm_tool)
    return toolkit


def get_agent_llm(agent_llm_name: str):
    """
    Retrieve a language model agent for conversational tasks.

    Args:
        agent_llm_name (str): The name or identifier of the language model for the agent.

    Returns:
        ChatOpenAI: A language model agent configured for conversational tasks.
    """
    llm_agent = get_chat_openai(model_name=agent_llm_name)
    return llm_agent


def create_agent_for_sql(tool_llm_name: str = "gpt-4-0125-preview", agent_llm_name: str = "gpt-4-0125-preview"):
    """
    Create an agent for SQL-related tasks.

    Args:
        tool_llm_name (str): The name or identifier of the language model for SQL toolkit.
        agent_llm_name (str): The name or identifier of the language model for the agent.

    Returns:
        Agent: An agent configured for SQL-related tasks.

    """
    # agent_tools = sql_agent_tools()
    llm_agent = get_agent_llm(agent_llm_name)
    toolkit = get_sql_toolkit(tool_llm_name)
    message_history = SQLChatMessageHistory(
        session_id="my-session",
        connection_string=f"mysql+pymysql://root:{password}@localhost:3306/ecommerce",
        table_name="message_store",
        session_id_field_name="session_id"
    )

    memory = ConversationBufferMemory(memory_key="chat_history", input_key='input', chat_memory=message_history, return_messages=False)

    agent = create_sql_agent(
        llm=llm_agent,
        toolkit=toolkit,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        input_variables=["input", "agent_scratchpad", "chat_history"],
        #suffix=CUSTOM_SUFFIX,
        memory=memory,
        agent_executor_kwargs={"memory": memory, "handle_parsing_errors":True},
        # extra_tools=agent_tools,
        verbose=True,
    )
    return agent


def create_agent_for_python(agent_llm_name: str = "gpt-4-0125-preview"):
    """
    Create an agent for Python-related tasks.

    Args:
        agent_llm_name (str): The name or identifier of the language model for the agent.

    Returns:
        AgentExecutor: An agent executor configured for Python-related tasks.

    """
    instructions = """You are an agent tasked with writing Python code to answer questions and perform data visualization.
                You have access to a Python REPL, which you can use to execute Python code.
                If you encounter an error, debug your code and try again.
                While you may know the answer without executing code, always run the code to confirm the accuracy of your response.
                If you cannot write code to answer the question, simply return "I don't know" as the answer.
                Your code output should be formatted as Python code only.

                When generating code, follow this chain of thought process:
                1. Understand the Question: Break down the question to identify what data is needed and what kind of plot or analysis is required.
                2. Plan Your Approach: Outline the necessary steps for data extraction, processing, and visualization. Think about which Plotly plot type (e.g., bar, line, scatter, map) suits the question best.
                3. Write and Test Code: Implement the Python code and run it in the REPL to ensure it produces the expected output. Debug if necessary.
                4. Check the Context: Ensure that the generated code aligns with previous data or context from the conversation, if applicable.
                5. Validate the Visualization: Verify that visualizations, especially maps, are appropriately centered and zoomed to display only relevant data (e.g., specific state, country, or region) without unnecessary global context.
                6. Output Only the Code: Provide only the code snippet, formatted as follows:
                ```python
                <code>
                ```

                Additional Guidelines:
                - Use Plotly exclusively for all visualizations. Do not use other libraries like Matplotlib or Seaborn.
                - For geographical data, ensure that the map's center and zoom are automatically adjusted based on the data's scope for better focus.
                - Do not fabricate data or assumptions. Base all code on the provided or requested data only.
                """

    tools = [PythonREPLTool()]
    base_prompt = hub.pull("langchain-ai/openai-functions-template")
    prompt = base_prompt.partial(instructions=instructions)
    agent = create_openai_functions_agent(ChatOpenAI(model=agent_llm_name, temperature=0), tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor





