import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.memory import ConversationBufferMemory
import datetime
from app.calendar_tools import check_availability, create_appointment


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
def create_calendar_appointment(start_time: str, end_time: str, summary: str, attendee_email:str = None) -> str:
    """Creates a new event in the calendar with optional attendee.
    Input times should be in ISO 8601 format (e.g., '2025-07-02T10:00:00').
    If attendee_email is provided, an invitation will be sent to that email address.
    """
    return create_appointment(start_time, end_time, summary, attendee_email)

tools = [check_calendar_availability, create_calendar_appointment]

today= datetime.datetime.now().isoformat()

# Define the prompt template for the agent
prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You are a professional receptionist assistant for Google Calendar appointment booking.
        ## Core Responsibilities:
        - Book appointments on Google Calendar
        - Be polite, helpful, and professional
        - Confirm all details before creating appointments

        ## Required Information for Booking:
        1. Date and time (use today's date: {today} for relative terms like "tomorrow", "next week")
        2. Meeting purpose/title

        ## Conversation Flow:
        1. Gather missing information politely
        2. Confirm all details with the user
        3. Create the appointment only after confirmation
        4. Provide booking confirmation with calendar link

        ## Guidelines:
        - For unclear dates/times, ask for clarification
        - Use descriptive titles for appointments (e.g., "Project Review Meeting" not just "Meeting")
        - Handle scheduling conflicts by suggesting alternative times
        - Only take attendee_email if explicitly provided by the user, otherwise create the appointment without it.

        ## Response Style:
        - Professional yet friendly tone
        - Clear and concise communication
        - Always confirm before taking action"""
    ),
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