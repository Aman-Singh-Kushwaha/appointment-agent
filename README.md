# Receptionist – Appointment Booking Agent

Receptionist is a conversational AI assistant that helps users book appointments on Google Calendar via a chat interface.

## Features

- Conversational chat UI (Streamlit)
- Google Calendar integration (view availability, create appointments)
- Powered by LangChain and Gemini LLM

## Setup

1. **Clone the repo and install dependencies:**
   ```sh
   git clone https://github.com/Aman-Singh-Kushwaha/appointment-agent.git
   cd appointment-agent
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Copy your Google Cloud service account key credentials to `credentials.json`.
   - Create a `.env` file with:
     ```
     GOOGLE_API_KEY=your_google_api_key
     CALENDAR_ID=your_calendar_email  # or leave blank for 'primary'
     ```

3. **Run the app:**
   ```sh
   streamlit run main.py
   ```

## Usage

- Chat with the assistant to check availability or book appointments.
- Appointments are created directly in your Google Calendar.

## Project Structure

- `main.py` – Streamlit app and agent logic
- `app/agent.py` – LangChain agent and tools
- `app/calendar_tools.py` – Google Calendar API helpers

---

