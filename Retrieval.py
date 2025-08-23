import pandas as pd
from datetime import datetime
import re
from LoadDB import LoadDB

class RetrievalAgent(LoadDB):
    """
    RAG Agent - LoadDB and Retrieval
    """
    def __init__(self):
        super().__init__()
        self.conn = None

    def analyze_input(self, text):
        """
        analyze natural language input
        """
        # check which fields are available in the database
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(returns)")
        columns_info = cursor.fetchall()
        available_columns = [col[1] for col in columns_info]
        
        analyzed_data = {}
        
        # order_id
        order_patterns = [
            r'order[_\s]*id[:\s]*(\d+)',  # order_id: 123
            r'order[:\s]*(\d+)',          # order: 123
            r'id[:\s]*(\d+)',             # id: 123
            r'(\d{4,})'                   # 4位以上數字 (如 1100, 1099)
        ]
        
        order_id = None
        for pattern in order_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                order_id = match.group(1)
                break
        
        if 'order_id' in available_columns:
            analyzed_data['order_id'] = order_id if order_id else None
        
        # product_name
        products = ["laptop", "phone", "tablet", "watch", "headphones", "camera", "speaker", "computer", "monitor", "keyboard", "mouse"]
        for p in products:
            if p in text.lower():
                if 'product_name' in available_columns:
                    analyzed_data['product_name'] = p.capitalize()
                elif 'product' in available_columns:
                    analyzed_data['product'] = p.capitalize()
                break
        
        # return_reason
        if 'return_reason' in available_columns:
            reason = None
            text_lower = text.lower()
            
            # 根據實際數據中的原因進行匹配
            if any(word in text_lower for word in ["defective", "broken", "faulty"]):
                reason = "Defective"
            elif any(word in text_lower for word in ["warranty", "warranty claim"]):
                reason = "Warranty Claim"
            elif any(word in text_lower for word in ["compatible", "compatibility", "not compatible"]):
                reason = "Not Compatible"
            elif any(word in text_lower for word in ["missing", "accessories", "missing accessories"]):
                reason = "Missing Accessories"
            elif any(word in text_lower for word in ["damaged", "arrival", "damaged on arrival"]):
                reason = "Damaged on Arrival"
            elif any(word in text_lower for word in ["wrong", "shipped", "wrong item"]):
                reason = "Wrong Item Shipped"
            elif any(word in text_lower for word in ["performance", "slow", "lag"]):
                reason = "Performance Issues"
            elif any(word in text_lower for word in ["battery", "battery issue"]):
                reason = "Battery Issue"
            elif any(word in text_lower for word in ["screen", "broken screen"]):
                reason = "Broken Screen"
            elif any(word in text_lower for word in ["changed mind", "change mind", "don't want"]):
                reason = "Changed Mind"
            
            analyzed_data['return_reason'] = reason
        
        # date
        if 'date' in available_columns:
            analyzed_data['date'] = datetime.now().strftime("%Y-%m-%d")
        
        return analyzed_data
    
    def insert_return(self, text_input):
        """
        insert new return record
        """
        # analyze input
        data = self.analyze_input(text_input)
        print(f" 新一筆退貨記錄: {data}")
        
        if not data:
            return {"Error": "無法分析輸入"}
        
        # INSERT statement
        columns = list(data.keys())
        placeholders = ['?' for _ in columns]
        values = list(data.values())
        
        sql = f"INSERT INTO returns ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, values)
            self.conn.commit()   
            return self.get_all_returns()

        except Exception as e:
            print(f"Error inserting data: {e}")
            return {"Error": str(e)}
    
    def get_all_returns(self):
        """
        get all return records
        """
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(returns)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info if col[1] not in ['id', 'created_at']]
        
        # select all records
        cursor.execute(f"SELECT {', '.join(column_names)} FROM returns ORDER BY id DESC")
        rows = cursor.fetchall()
        
        # DataFrame
        df = pd.DataFrame(rows, columns=column_names)
        return df
    
    def close(self):
        super().close()

if __name__ == "__main__":
    agent = RetrievalAgent() 
    result = agent.load_csv("sample.csv")
    
    # test insert
    result = agent.insert_return("Return order 123 laptop")
    agent.close()
    print(result)
