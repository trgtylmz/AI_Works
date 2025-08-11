import os
import json
from typing import List, Tuple

from dotenv import load_dotenv
import chainlit as cl
from openai import AzureOpenAI
import pyodbc

load_dotenv()

CONFIG_FILE = "config.json"


def load_config() -> dict:
    """Load the agent configuration from disk."""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_sql(query: str) -> Tuple[List[str], List[Tuple]]:
    """Execute a SQL query and return columns and rows."""
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.environ.get('DB_SERVER')};"
        f"DATABASE={os.environ.get('DB_DATABASE')};"
        f"UID={os.environ.get('DB_USER')};"
        f"PWD={os.environ.get('DB_PASSWORD')};"
        "TrustServerCertificate=yes;"
    )
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return columns, rows


def find_sql(user_input: str) -> str | None:
    """Find a matching SQL statement from config based on user input."""
    config = load_config()
    for sample in config.get("samples", []):
        if sample["question"].lower() in user_input.lower():
            return sample["sql"]
    return None


@cl.on_chat_start
async def start_chat():
    config = load_config()
    await cl.Message(content=config.get("instructions", "")).send()


@cl.on_message
async def main(message: cl.Message):
    user_text = message.content
    sql = find_sql(user_text)

    if sql:
        columns, rows = run_sql(sql)
        table = cl.DataTable(columns=columns, data=rows)
        await cl.Message(content="Query result", elements=[table]).send()
        return

    client = AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_version="2023-07-01-preview",
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    )

    response = client.chat.completions.create(
        model=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        messages=[{"role": "user", "content": user_text}],
    )

    await cl.Message(content=response.choices[0].message.content).send()
