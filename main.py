import os
import pandas as pd
from Controller import Controller

def demo():

    print("\n" + "="*60)
    print("Returns & Warranty System")
    print("="*60)
    
    # step 1. init system
    controller = Controller()
    
    try:
        # step 1. load csv data
        print("\nStep 1. load csv data")
        
        # input csv file path
        csv_file = input("input csv file path: ").strip()
        
        if not os.path.exists(csv_file):
            print(f"file not found: {csv_file}")
            return
        
        result = controller.handle_request("load_csv", csv_file)
        print(f"load result: {result}")
        
        # step 2. natural language insert
        print("\nStep 2. natural language insert")
        print("Enter natural language to insert return records (type 'quit' to stop):")
        
        while True:
            user_input = input("\nEnter new return : ").strip()
            
            if user_input.lower() == 'quit':
                break
                
            if not user_input:
                print("Please enter a new return")
                continue
                
            print(f"Processing: '{user_input}'")
            result = controller.handle_request("insert", user_input)
            
            if isinstance(result, dict) and "Error" in result:
                print(f"Insert failed: {result['Error']}")
            else:
                print(f"Insert success, now have {len(result)} records")
        
        # step 3. query all records
        print("\nStep 3. query all records")
        all_returns = controller.handle_request("query")
        print(f"Total {len(all_returns)} records")
        if len(all_returns) > 0:
            print("First 5 records:")
            for i, row in all_returns.head().iterrows():
                print(f"  - {row.get('order_id', 'N/A')}: {row.get('product', 'N/A')} ({row.get('return_reason', 'N/A')})")
        
        # step 4. generate report
        print("\nStep 4. generate report")
        result = controller.handle_request("report", "summary_report.xlsx")
        if isinstance(result, dict) and result.get('success'):
            print(f"Report generated: {result['file']}")
            print(f"  總退貨數: {result['summary']['total']}")
            if result['summary']['top_product']:
                print(f"  最常退貨: {result['summary']['top_product']}")
            if result['summary']['top_reason']:
                print(f"  主要原因: {result['summary']['top_reason']}")
        else:
            print(f" 報告生成失敗: {result}")
        
        print("\n" + "="*60)
        print("Demo done!")
        print("="*60)
        
    finally:
        controller.close()
        
if __name__ == "__main__":
    demo()