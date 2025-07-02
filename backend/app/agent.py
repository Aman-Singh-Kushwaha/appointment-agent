import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
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
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# In-memory store for conversation history
store = {}

def get_agent_response(query: str, session_id: str) -> str:
    """Gets a response from the LangChain agent with conversation history."""
    if session_id not in store:
        store[session_id] = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    
    memory = store[session_id]

    # Create the agent executor for each call, passing the memory directly
    agent_executor = AgentExecutor(agent=create_tool_calling_agent(llm, tools, prompt), tools=tools, verbose=True)

    response = agent_executor.invoke(
        {"input": query, "chat_history": memory.load_memory_variables({})["chat_history"]}
    )
    
    # Save the new interaction to memory
    memory.save_context({"input": query}, {"output": response["output"]})

    return response["output"]