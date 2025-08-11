# AI Works SQL Agent

This project contains a Chainlit-based chat agent backed by Azure OpenAI and SQL Server, along with a FastAPI admin panel for managing sample questions and SQL statements.

## Setup

1. **Create an environment file** named `.env` and fill in your Azure OpenAI and SQL Server credentials:
   ```env
   AZURE_OPENAI_API_KEY=your-key
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your-deployment
   DB_SERVER=your-db-server
   DB_DATABASE=your-db-name
   DB_USER=your-username
   DB_PASSWORD=your-password
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the admin panel**
   ```bash
   uvicorn admin_app:app --reload
   ```
   Visit [http://localhost:8000](http://localhost:8000) to update instructions and sample query mappings.

4. **Run the chat agent**
   ```bash
   chainlit run app.py -w
   ```
   Open the printed URL in your browser to chat with the agent.

The admin panel edits `config.json`, which is shared by the chat agent at runtime.
