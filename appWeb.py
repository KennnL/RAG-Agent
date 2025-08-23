import streamlit as st
import pandas as pd
import os
from datetime import datetime
from Controller import Controller
from LoadDB import LoadDB
from Retrieval import RetrievalAgent
from GenReport import ReportAgent

# 頁面設定
st.set_page_config(
    page_title="Returns & Warranty System",
    page_icon="📦",
    layout="wide"
)

# 初始化 session state
if 'controller' not in st.session_state:
    try:
        st.session_state.controller = Controller()
        st.session_state.data_loaded = False
    except Exception as e:
        st.error(f"Failed to initialize system: {str(e)}")
        st.stop()

def safe_handle_request(controller, action, data=None):
    """Safely handle controller requests with error handling"""
    try:
        return controller.handle_request(action, data)
    except Exception as e:
        st.error(f"System error: {str(e)}")
        return None

def main():
    # 標題
    st.title("📦 Returns & Warranty RAG System")
    st.markdown("2-Agent System for Product Returns Management")
    
    # 側邊欄 - 資料載入
    with st.sidebar:
        st.header("📂 Data Management")
        
        # CSV 上傳
        uploaded_file = st.file_uploader(
            "Upload CSV file", 
            type=['csv'],
            help="Upload your returns data CSV"
        )
        
        if uploaded_file is not None:
            try:
                # 儲存上傳的檔案
                temp_file_path = f"temp_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                if st.button("Load Data", type="primary"):
                    with st.spinner("Loading data..."):
                        result = safe_handle_request(st.session_state.controller, "load_csv", temp_file_path)
                        
                        if result and result.get('success'):
                            st.success(f"✓ Loaded {result['records']} records")
                            st.session_state.data_loaded = True
                            
                            # 清理臨時檔案
                            try:
                                os.remove(temp_file_path)
                            except:
                                pass
                        else:
                            error_msg = result.get('error', 'Unknown error') if result else 'System error'
                            st.error(f"Failed to load data: {error_msg}")
                            
            except Exception as e:
                st.error(f"Error processing uploaded file: {str(e)}")
        
        # 或使用範例資料
        st.divider()
        if st.button("Use Sample Data"):
            try:
                with st.spinner("Loading sample data..."):
                    # 使用現有的 sample.csv 檔案
                    sample_file = 'sample.csv'
                    
                    if not os.path.exists(sample_file):
                        st.error(f"Sample file not found: {sample_file}")
                        return
                    
                    result = safe_handle_request(st.session_state.controller, "load_csv", sample_file)
                    if result and result.get('success'):
                        st.success(f"✓ Loaded {result['records']} sample records")
                        st.session_state.data_loaded = True
                    else:
                        error_msg = result.get('error', 'Unknown error') if result else 'System error'
                        st.error(f"Failed to load sample data: {error_msg}")
                        
            except Exception as e:
                st.error(f"Error loading sample data: {str(e)}")
    
    # 主要內容 - 分頁
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Insert Return", 
        "📋 View Records", 
        "📊 Statistics", 
        "📈 Generate Report"
    ])
    
    # Tab 1: 自然語言插入
    with tab1:
        st.header("Insert New Return")
        
        # 說明
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            **Input Examples:**
            - Return order 1234 laptop defective
            - Order 5678 phone wrong item shipped
            - Tablet damaged on arrival, order id: 9012
            
            **Supported Products:** laptop, phone, tablet, watch, headphones, camera, speaker
            
            **Return Reasons:** defective, wrong item, damaged, warranty claim, changed mind, etc.
            """)
        
        # 輸入區
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_input = st.text_input(
                "Describe the return (natural language):",
                placeholder="e.g., Return order 1234 laptop defective"
            )
        
        with col2:
            if st.button("Insert", type="primary", disabled=not st.session_state.data_loaded):
                if user_input:
                    with st.spinner("Processing..."):
                        result = safe_handle_request(st.session_state.controller, "insert", user_input)
                        
                        if isinstance(result, pd.DataFrame):
                            st.success("✓ Record inserted successfully!")
                            st.write(f"Total records now: {len(result)}")
                        else:
                            error_msg = result.get('error', 'Unknown error') if result else 'System error'
                            st.error(f"Insert failed: {error_msg}")
                else:
                    st.warning("Please enter a return description")
        
        # 顯示最近插入的記錄
        if st.session_state.data_loaded:
            st.subheader("Recent Returns")
            try:
                all_returns = safe_handle_request(st.session_state.controller, "query")
                if isinstance(all_returns, pd.DataFrame) and not all_returns.empty:
                    # 只顯示最近5筆
                    st.dataframe(all_returns.head(), use_container_width=True)
                else:
                    st.info("No records found")
            except Exception as e:
                st.error(f"Error loading recent returns: {str(e)}")
    
    # Tab 2: 查看記錄
    with tab2:
        st.header("All Return Records")
        
        if st.session_state.data_loaded:
            if st.button("Refresh Data"):
                st.rerun()
                
            try:
                all_returns = safe_handle_request(st.session_state.controller, "query")
                
                if isinstance(all_returns, pd.DataFrame) and not all_returns.empty:
                    # 顯示統計
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Returns", len(all_returns))
                    with col2:
                        if 'product' in all_returns.columns:
                            st.metric("Unique Products", all_returns['product'].nunique())
                    with col3:
                        if 'return_reason' in all_returns.columns:
                            top_reason = all_returns['return_reason'].value_counts().iloc[0] if 'return_reason' in all_returns.columns else 'N/A'
                            st.metric("Top Reason", top_reason)
                    
                    # 顯示資料表
                    st.dataframe(all_returns, use_container_width=True)
                    
                    # 下載選項
                    try:
                        csv = all_returns.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"returns_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    except Exception as e:
                        st.error(f"Error creating download: {str(e)}")
                else:
                    st.info("No records found")
            except Exception as e:
                st.error(f"Error loading records: {str(e)}")
        else:
            st.warning("Please load data first")
    
    # Tab 3: 統計
    with tab3:
        st.header("Returns Statistics")
        
        if st.session_state.data_loaded:
            try:
                all_returns = safe_handle_request(st.session_state.controller, "query")
                
                if isinstance(all_returns, pd.DataFrame) and not all_returns.empty:
                    # 基本統計
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Product Distribution")
                        if 'product' in all_returns.columns:
                            product_counts = all_returns['product'].value_counts()
                            st.bar_chart(product_counts)
                    
                    with col2:
                        st.subheader("Return Reasons")
                        if 'return_reason' in all_returns.columns:
                            reason_counts = all_returns['return_reason'].value_counts()
                            st.bar_chart(reason_counts)
                    
                    # 詳細統計表
                    st.subheader("Detailed Statistics")
                    
                    if 'product' in all_returns.columns:
                        product_stats = all_returns['product'].value_counts().reset_index()
                        product_stats.columns = ['Product', 'Count']
                        product_stats['Percentage'] = (product_stats['Count'] / len(all_returns) * 100).round(1)
                        st.dataframe(product_stats, use_container_width=True)
                else:
                    st.info("No data available for statistics")
            except Exception as e:
                st.error(f"Error loading statistics: {str(e)}")
        else:
            st.warning("Please load data first")
    
    # Tab 4: 生成報告
    with tab4:
        st.header("Generate Excel Report")
        
        if st.session_state.data_loaded:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                report_name = st.text_input(
                    "Report filename:",
                    value=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                )
            
            with col2:
                if st.button("Generate Report", type="primary"):
                    with st.spinner("Generating report..."):
                        try:
                            result = safe_handle_request(st.session_state.controller, "report", report_name)
                            
                            if result and result.get('success'):
                                st.success(f"✓ Report generated: {report_name}")
                                
                                # 顯示摘要
                                st.subheader("Report Summary")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Total Returns", result['summary']['total'])
                                with col2:
                                    if result['summary']['top_product']:
                                        st.metric("Top Product", result['summary']['top_product'])
                                with col3:
                                    if result['summary']['top_reason']:
                                        st.metric("Top Reason", result['summary']['top_reason'])
                                
                                # 提供下載
                                try:
                                    with open(report_name, 'rb') as f:
                                        st.download_button(
                                            label="📥 Download Excel Report",
                                            data=f,
                                            file_name=report_name,
                                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                        )
                                except Exception as e:
                                    st.error(f"Error creating download: {str(e)}")
                            else:
                                error_msg = result.get('error', 'Unknown error') if result else 'System error'
                                st.error(f"Report generation failed: {error_msg}")
                        except Exception as e:
                            st.error(f"Error generating report: {str(e)}")
        else:
            st.warning("Please load data first")
    
    # 頁尾
    st.divider()
    st.markdown("""
    ---
    Returns & Warranty RAG System | 2-Agent Architecture (Retrieval + Report)
    """)

if __name__ == "__main__":
    main()