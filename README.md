"Returns & Warranty RAG System"

一個完整的檢索增強生成(RAG) 系統，用於管理退貨和保固資料，具備自然語言處理功能，可以將資料儲存至DB並進行資料輸入和自動報表生成。

#1. Features 
- 自然語言資料輸入：使用自然語言輸入退貨記錄
- 輸入資料解析：自動提取訂單編號、產品、成本、日期等資訊
- 資料庫管理：自動建立 SQLite 資料庫
- Excel 報表生成：Summary + Findings
- Agents：Retrieval & Report

#2. Demo介面(Streamlit)
- 簡易Demo&Test介面：網頁介面
- 資料視覺化：圖表和統計資料
- CSV 檔案上傳/下載：匯入資料或匯出結果

#3. 系統架構
RAG-Agent/
├── Controller.py          # 控制Agent(MCP)
├── LoadDB.py              # 資料庫管理(Raw Data存入)
├── Retrieval.py           # 自然語言解析與資料檢索
├── GenReport.py           # 報表生成
├── appWeb.py              # Streamlit 網頁介面
├── main.py                # 主程式
├── sample.csv             # 題目的範例資料
└── requirements.txt       # packages

#4. Module說明
#4-1 Controller
- 管理系統中各個module的請求及處理

#4-2 LoadDB
- 資料載入與管理
- 基於 CSV 架構動態建立表格

#4-3 Retrieval
- 檢索Agent
- 自然語言解析
- 資料庫查詢管理

#4-4 Report
- 生成報表Agent
- 統計分析
- Excel 報表生成
- Summary & Findings

#4-5 main
- 主程式(整體流程)

#4-6 appWeb
- 簡易介面互動
- Streamlit 網頁

#5. 整體流程
#5-1 載入CSV資料 → LoadDB.load_csv() → 建立資料庫表格
   ↓
#5-2 使用者輸入（輸入自然語言）
   ↓
#5-3 網頁介面（Streamlit）
   ↓
#5-4 Controller.handle_request()
   ↓
#5-5 請求端點
   ├─→ "insert" → RetrievalAgent.insert_return() → 新增退貨記錄
   ├─→ "query" → RetrievalAgent.get_all_returns() → 查詢所有記錄
   └─→ "report" → ReportAgent.create_report() → 生成Excel報告
   ↓
#5-6 資料庫操作（SQLite）
   ↓
#5-7 回應處理
   ↓
#5-8 更新

#6 Output (Generate Report)
- 摘要統計：總退貨數、成本
- 商店分析：購買商店
- 產品洞察：最常退貨的商品
- 原因分析：常見退貨原因
- 成本分析：財務影響

--------------------------------------------------------------------------------------------------
#自然語言輸入格式說明及範例

# 格式說明
|order ID| 
明確格式：
order_id: 1234 / order_id:1234 / order_id :1234 / order_id : 1234 /order: 1234 / order:1234 / order :1234 / order : 1234 / id: 1234 / id:1234 / id :1234 / id : 1234
自動判別：
任何4位以上數字 (如 1001, 2100, 12345)

|Product|
必須使用明確格式：
product: Laptop / product:Laptop / product :Laptop / product : Laptop
product: Bluetooth Speaker/ Smart Watch (支援多詞名稱)

|Return Reason|
必須使用明確格式：
reason: Defective / reason:Defective / reason :Defective / reason : Defective
return_reason: Missing Accessories/ because: Damaged On Arrival

|Date|
明確格式：
date: 2025-01-18 / date:2025-01-18 / date :2025-01-18 / date : 2025-01-18
date: 01/18/2025 / date: 1/18/2025
自動判別：
2025-01-18 (YYYY-MM-DD)
01/18/2025 (MM/DD/YYYY)
1/18/2025 (M/D/YYYY)
無日期時自動使用當前日期

|Cost|
明確格式：
cost: $128 / cost:$128 / cost :$128 / cost : $128
cost: 128.50 / price: $299.99
自動判別：
$128 / $299.99
128 dollars / 299.99 dollars

|Store|
明確格式：
store: Brooklyn Center / store:Brooklyn Center
store_name: Sunnyvale Town

|Category|
必須使用明確格式：
category: Electronics / category:Electronics
category: Accessories

|Approved Flag|
明確格式：
approved: Yes / approved:No / approved :Pending
approved_flag: Yes / status: approved
預設值：No
自動判別：
Yes / yes / true / approved → Yes
No / no / false / rejected → No
pending → Pending

# 範例
#1. 
order: 2100 product: Tablet category: Electronics reason: Missing Accessories cost: $277 approved: Yes store: Sunnyvale Town date: 2025-01-18

#2.
Return 1234 product:Laptop reason:Defective $599 at Brooklyn Center 2025-01-15

#3.
order: 1500 product: Tablet reason: defective category: Electronics approved: Yes cost: $300 store: Brooklyn Center date: 2025-07-18








