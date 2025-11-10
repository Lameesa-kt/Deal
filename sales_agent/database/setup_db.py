import sqlite3
import pandas as pd
import os

# Path to your CSV
csv_path = "customer.csv"
# Target database file (will be created automatically)
db_path = "customer.sqlite"

def csv_to_sqlite(csv_path, db_path):
    # Load CSV into pandas DataFrame
    df = pd.read_csv(csv_path)
    
    # Create SQLite connection
    conn = sqlite3.connect(db_path)
    # Save to table called "customer"
    df.to_sql("customer", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    print(f"✅ Created SQLite database at: {db_path}")
    print(f"✅ Table 'customer' created with {len(df)} records.")

if __name__ == "__main__":
    if not os.path.exists("database"):
        os.makedirs("database")
    csv_to_sqlite(csv_path, db_path)
