import sqlite3
import pandas as pd
from datetime import datetime
import re

class LoadDB:
    def __init__(self):
        self.db_path = "ReturnsData.db"
        self.conn = None
        self.table_created = False

    def create_table(self, df):
        """
        Create a table in the database based on the DataFrame columns
        """
        if self.table_created:
            return
        # connect to the database
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
        
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
        self.conn.execute(create_table_sql)
        self.conn.commit()
        
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
            
            # step 3: create a database table based on the cleaned columns
            self.create_table(df)
            
            # step 4: write
            df.to_sql('returns', self.conn, if_exists='append', index=False)
            
            print(f"Successfully wrote {len(df)} records to the database")
            
            return {"success": True, "records": len(df), "columns": list(df.columns)}
            
        except FileNotFoundError:
            print(f"CSV file not found: {csv_path}")
            return {"success": False, "error": "File not found"}
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return {"success": False, "error": str(e)}
            
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

if __name__ == "__main__":
    loader = LoadDB()
    result = loader.load_csv("sample.csv")
    loader.close()