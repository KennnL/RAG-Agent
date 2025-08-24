import sqlite3
import pandas as pd
from datetime import datetime
import re
import threading

class LoadDB:
    def __init__(self):
        self.db_path = "ReturnsData.db"
        self.conn = None
        self.table_created = False
        self._local = threading.local()
    
    def _get_connection(self):
        """Get a thread-safe database connection"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
        return self._local.conn
    
    def _refresh_connection(self):
        """Refresh the thread-local connection to see latest data"""
        if hasattr(self._local, 'conn') and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None

    def create_table(self, df):
        """
        Create a table in the database based on the DataFrame columns
        """
        # Use thread-safe connection
        conn = self._get_connection()
            
        if self.table_created:
            return
        
        columns = []
        columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        
        # According to the DataFrame columns and data type
        for col in df.columns:
            if df[col].dtype == 'object': 
                col_type = 'TEXT'
            elif df[col].dtype in ['int64', 'int32']:  
                col_type = 'INTEGER'
            elif df[col].dtype in ['float64', 'float32']:  
                col_type = 'REAL'
            else:
                col_type = 'TEXT'  
            
            columns.append(f"{col} {col_type}")
 
        # create table sql
        create_table_sql = f"CREATE TABLE IF NOT EXISTS returns ({', '.join(columns)})"

        # execute create table sql
        conn.execute(create_table_sql)
        conn.commit()
        
        self.table_created = True
        print("Database table created")
    
    def load_csv(self, csv_path):
        """
        Load CSV and create a database table
        """
        if not csv_path or not csv_path.strip():
            return {"Invalid file path"}
        try:
            # step 1: read the csv file
            df = pd.read_csv(csv_path)
            
            # step 2: clean the column name first
            df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
            
            # step 3: write - replace existing data but preserve id column
            # Use thread-safe connection
            conn = self._get_connection()
            
            # First, drop the table if it exists
            conn.execute("DROP TABLE IF EXISTS returns")
            conn.commit()
            
            # Reset table_created flag
            self.table_created = False
            
            # Create table with id column
            self.create_table(df)
            
            # Insert data
            df.to_sql('returns', conn, if_exists='append', index=False)
            
            # Refresh thread-local connections to see new data
            self._refresh_connection()
            
            print(f"Successfully wrote {len(df)} records to the database")
            
            return {"success": True, "records": len(df), "columns": list(df.columns)}
            
        except FileNotFoundError:
            print(f"CSV file not found: {csv_path}")
            return {"success": False, "error": "File not found"}
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return {"success": False, "error": str(e)}
            
    def close(self):
        # Close legacy connection if exists
        if self.conn:
            self.conn.close()
            self.conn = None
        
        # Close thread-local connection if exists
        if hasattr(self._local, 'conn') and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None

if __name__ == "__main__":
    loader = LoadDB()
    result = loader.load_csv("sample.csv")
    loader.close()