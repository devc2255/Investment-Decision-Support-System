import sqlite3
import pandas as pd
from datetime import date

DB_NAME = "deals_pipeline.db"

def init_db():
    """Initializes the database and creates the deals table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            target_name TEXT NOT NULL,
            sector TEXT,
            market_cap REAL,
            thesis TEXT,
            status TEXT,
            entry_date DATE
        )
    ''')
    conn.commit()
    conn.close()

def add_deal(ticker, target_name, sector, market_cap, thesis, status):
    """Inserts a new deal into the ledger."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO deals (ticker, target_name, sector, market_cap, thesis, status, entry_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (ticker.upper(), target_name, sector, market_cap, thesis, status, date.today()))
    conn.commit()
    conn.close()

def get_all_deals():
    """Retrieves all deals and returns them as a Pandas DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    # Using pandas to read SQL makes Streamlit integration seamless
    df = pd.read_sql_query("SELECT * FROM deals", conn)
    conn.close()
    return df

def delete_deal(deal_id):
    """Removes a deal from the database by its ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM deals WHERE id = ?", (deal_id,))
    conn.commit()
    conn.close()