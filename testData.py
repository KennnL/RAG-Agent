import pandas as pd

def testData():
    test_data = {
        'order_id': ['SKU-001', 'SKU-002', 'SKU-003', 'SKU-004', 'SKU-005'],
        'product': ['Laptop', 'Phone', 'TV', 'Laptop', 'Earphone'],
        'store_name': ['Store A', 'Store B', 'Store A', 'Store C', 'Store B'],
        'date': ['2025-08-01', '2025-08-02', '2025-08-03', '2025-08-04', '2025-08-06'],
        'reason': ['Defective', 'Wrong-item', 'Damaged', 'Defective', 'Not-specified']
    }
    
    df = pd.DataFrame(test_data)
    df.to_csv('test_data.csv', index=False)
    print("CSV file created: test_data.csv")
    return 'test_data.csv'
