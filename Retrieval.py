import pandas as pd
from datetime import datetime
import re
import sqlite3
import threading
from LoadDB import LoadDB

class RetrievalAgent(LoadDB):
    """
    RAG Agent - LoadDB and Retrieval
    """
    def __init__(self):
        super().__init__()
        self.conn = None
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

    def analyze_input(self, text):
        """
        analyze natural language input
        """
        # 使用線程安全的連接
        conn = self._get_connection()
            
        # check which fields are available in the database
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(returns)")
        columns_info = cursor.fetchall()
        available_columns = [col[1] for col in columns_info]
        
        analyzed_data = {}
        
        # order_id
        order_patterns = [
            r'order[_\s]*id\s*:\s*(\d+)',  # order_id: 123, order_id:123
            r'order\s*:\s*(\d+)',          # order: 123, order:123, order :123, order : 123
            r'id\s*:\s*(\d+)',             # id: 123, id:123, id :123, id : 123
            r'(\d{4,})'                    # 數字
        ]
        
        order_id = None
        for pattern in order_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                order_id = match.group(1)
                break
        
        if 'order_id' in available_columns:
            analyzed_data['order_id'] = order_id if order_id else None
        
        # product 
        product_patterns = [
            r'product\s*:\s*([A-Za-z\s]+?)(?:\s|$|,)',     # product: Laptop, product:Laptop, product :Laptop, product : Laptop
        ]
        
        product_value = None
        for pattern in product_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                product_value = match.group(1).strip().title()  # 大小寫
                break
        
        if product_value:
            if 'product_name' in available_columns:
                analyzed_data['product_name'] = product_value
            elif 'product' in available_columns:
                analyzed_data['product'] = product_value
        
        # return_reason 
        if 'return_reason' in available_columns:
            reason = None
            
            # 優先使用模式匹配
            reason_patterns = [
                r'reason\s*:\s*([A-Za-z\s]+?)(?:\s|$|,)',      # reason: Defective, reason:Defective, reason :Defective, reason : Defective
                r'because\s*:\s*([A-Za-z\s]+?)(?:\s|$|,)',     # because: defective, because:defective, because :defective, because : defective
                r'return_reason\s*:\s*([A-Za-z\s]+?)(?:\s|$|,)', # return_reason: Missing Accessories, return_reason:Missing Accessories, return_reason :Missing Accessories, return_reason : Missing Accessories
            ]
            
            for pattern in reason_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    reason = match.group(1).strip().title()
                    break
            

            
            analyzed_data['return_reason'] = reason
        
        # date 
        if 'date' in available_columns:
            date_patterns = [
                r'date\s*:\s*(\d{4}-\d{2}-\d{2})', # date: 2025-01-03, date:2025-01-03, date :2025-01-03, date : 2025-01-03
                r'date\s*:\s*(\d{2}/\d{2}/\d{4})', # date: 01/03/2025, date:01/03/2025, date :01/03/2025, date : 01/03/2025
                r'(\d{4}-\d{2}-\d{2})',           # 2025-01-03
                r'(\d{2}/\d{2}/\d{4})',           # 01/03/2025
                r'(\d{1,2}/\d{1,2}/\d{4})',       # 1/3/2025
            ]
            
            extracted_date = None
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date_str = match.group(1)
                    # 標準化日期格式為 YYYY-MM-DD
                    if '/' in date_str:
                        if len(date_str.split('/')[2]) == 4:  # MM/DD/YYYY
                            month, day, year = date_str.split('/')
                            extracted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    else:
                        extracted_date = date_str  # 已經是 YYYY-MM-DD 格式
                    break
            
            analyzed_data['date'] = extracted_date if extracted_date else datetime.now().strftime("%Y-%m-%d")
        
        # cost 
        if 'cost' in available_columns:
            cost_patterns = [
                r'cost\s*:\s*\$?(\d+\.?\d*)',       # cost: $128, cost:$128, cost :$128, cost : $128
                r'price\s*:\s*\$?(\d+\.?\d*)',      # price: $128, price:$128, price :$128, price : $128
                r'\$(\d+\.?\d*)',                   # $128
                r'(\d+\.?\d*)\s*dollars?',          # 128 dollars
            ]
            
            cost_value = None
            for pattern in cost_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    cost_value = float(match.group(1))
                    break
            
            analyzed_data['cost'] = cost_value
        
        # store_name 
        if 'store_name' in available_columns:
            store_patterns = [
                r'store\s*:\s*([A-Za-z\s]+?)(?:\s|$|,)',       # store: Brooklyn Center, store:Brooklyn Center, store :Brooklyn Center, store : Brooklyn Center
                r'store_name\s*:\s*([A-Za-z\s]+?)(?:\s|$|,)',  # store_name: Sunnyvale Town, store_name:Sunnyvale Town, store_name :Sunnyvale Town, store_name : Sunnyvale Town
                r'at\s+([A-Za-z\s]+?)(?:\s|$|,)',              # at Brooklyn Center
                r'from\s+([A-Za-z\s]+?)(?:\s|$|,)',            # from Riverdale Outlet
            ]
            
            store_value = None
            for pattern in store_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    store_value = match.group(1).strip().title()
                    break
            
            analyzed_data['store_name'] = store_value
        
        # category 
        if 'category' in available_columns:
            category_patterns = [
                r'category\s*:\s*([A-Za-z]+)',      # category: Electronics, category:Electronics, category :Electronics, category : Electronics
            ]
            
            category_value = None
            for pattern in category_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    category_value = match.group(1).strip().title()
                    break
            
            analyzed_data['category'] = category_value
        
        # approved_flag 
        if 'approved_flag' in available_columns:
            approval_patterns = [
                r'approved\s*:\s*(yes|no|true|false)',     # approved: yes, approved:yes, approved :yes, approved : yes
                r'status\s*:\s*(approved|rejected|pending)', # status: approved, status:approved, status :approved, status : approved
                r'approved_flag\s*:\s*(yes|no)',           # approved_flag: yes, approved_flag:yes, approved_flag :yes, approved_flag : yes
            ]
            
            approval_value = "No"  # 預設值
            for pattern in approval_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    status = match.group(1).lower()
                    if status in ['yes', 'true', 'approved']:
                        approval_value = "Yes"
                    elif status in ['no', 'false', 'rejected']:
                        approval_value = "No"
                    elif status == 'pending':
                        approval_value = "Pending"
                    break
            
            analyzed_data['approved_flag'] = approval_value
        
        return analyzed_data
    
    def insert_return(self, text_input):
        """
        insert new return record
        """
        # 使用線程安全的連接
        conn = self._get_connection()
        
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
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()   
            return self.get_all_returns()

        except Exception as e:
            print(f"Error inserting data: {e}")
            return {"Error": str(e)}
    
    def get_all_returns(self):
        """
        get all return records
        """
        # 使用線程安全的連接
        conn = self._get_connection()
            
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(returns)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info if col[1] not in ['id', 'created_at']]
        
        # select all records - use id for ordering
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