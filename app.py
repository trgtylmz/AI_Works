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
    drivers = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "SQL Server",
    ]
    conn = None
    last_exc: Exception | None = None
    for driver in drivers:
        try:
            conn = pyodbc.connect(
                f"DRIVER={{{driver}}};"
                f"SERVER={os.environ.get('DB_SERVER')};"
                f"DATABASE={os.environ.get('DB_DATABASE')};"
                f"UID={os.environ.get('DB_USER')};"
                f"PWD={os.environ.get('DB_PASSWORD')};"
                "TrustServerCertificate=yes;",
            )
            break
        except pyodbc.InterfaceError as e:
            last_exc = e
    if conn is None:
        raise RuntimeError(
            "No suitable ODBC driver found. Install 'ODBC Driver 18 for SQL Server'."
        ) from last_exc
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return columns, rows


def find_sql(user_input: str, config: dict) -> str | None:
    """Find a matching SQL statement from config based on user input."""
    for sample in config.get("samples", []):
        if sample["question"].lower() in user_input.lower():
            return sample["sql"]
    return None


@cl.on_chat_start
async def start_chat():
    await cl.Message(content="Merhaba, sana nasıl yardımcı olabilirim?").send()


@cl.on_message
async def main(message: cl.Message):
    user_text = message.content
    config = load_config()
    sql = find_sql(user_text, config)

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
        messages=[
            {"role": "system", "content": config.get("instructions", "")},
            {"role": "user", "content": user_text},
        ],
    )

    await cl.Message(content=response.choices[0].message.content).send()
