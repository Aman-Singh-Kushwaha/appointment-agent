import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ConversationBufferMemory
from .calendar_tools import check_availability, create_appointment

load_dotenv()

# Load Google API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)

# Define the tools for the agent
@tool
def check_calendar_availability(start_time: str, end_time: str) -> list[str]:
    """Checks for available time slots in the calendar between two datetimes.
    Input should be in ISO 8601 format (e.g., '2025-07-02T10:00:00').
    """
    return check_availability(start_time, end_time)

@tool
def create_calendar_appointment(start_time: str, end_time: str, summary: str) -> str:
    """Creates a new event in the calendar.
    Input times should be in ISO 8601 format (e.g., '2025-07-02T10:00:00').
    """
    return create_appointment(start_time, end_time, summary)

tools = [check_calendar_availability, create_calendar_appointment]

# Define the prompt template for the agent
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful receptionist. Your goal is to assist users in booking appointments on their Google Calendar. Be polite and confirm details before booking."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create the agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# In-memory store for conversation history
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    return store[session_id]

with_message_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

def get_agent_response(query: str, session_id: str) -> str:
    """Gets a response from the LangChain agent with conversation history."""
    response = with_message_history.invoke(
        {"input": query},
        config={"configurable": {"session_id": session_id}},
    )
    return response["output"]