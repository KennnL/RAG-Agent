import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 頁面設定
st.set_page_config(
    page_title="Returns & Warranty RAG System",
    layout="wide"
)

# session state
if 'controller' not in st.session_state:
    try:
        from Controller import Controller
        st.session_state.controller = Controller()
        st.session_state.data_loaded = False
    except Exception as e:
        st.error(f"Failed to initialize system: {str(e)}")
        st.stop()

def safe_handle_request(action, data=None):
    """Safely handle controller requests with error handling"""
    try:
        return st.session_state.controller.handle_request(action, data)
    except Exception as e:
        st.error(f"System error: {str(e)}")
        return None

def main():
    # title
    st.title("Returns & Warranty RAG System")
    st.markdown("2-Agent System, MCP-style")
    
    # data load
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
                # save uploaded file
                temp_file_path = f"temp_upload_{datetime.now().strftime('%Y%m%d')}.csv"
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                if st.button("Load Data", type="primary"):
                    with st.spinner("Loading data..."):
                        result = safe_handle_request("load_csv", temp_file_path)
                        
                        if result and result.get('success'):
                            st.success(f"Loaded {result['records']} records")
                            st.session_state.data_loaded = True
                            
                            # clean up 
                            try:
                                os.remove(temp_file_path)
                            except:
                                pass
                        else:
                            error_msg = result.get('error', 'Unknown error') if result else 'System error'
                            st.error(f"Failed to load data: {error_msg}")
                            
            except Exception as e:
                st.error(f"Error processing uploaded file: {str(e)}")
        
        # use sample data
        st.divider()
        if st.button("Use Sample Data"):
            try:
                with st.spinner("Loading sample data..."):
                    # use existing sample.csv
                    sample_file = 'sample.csv'
                    
                    if not os.path.exists(sample_file):
                        st.error(f"Sample file not found: {sample_file}")
                        return
                    
                    result = safe_handle_request("load_csv", sample_file)
                    if result and result.get('success'):
                        st.success(f"Loaded {result['records']} sample records")
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
    
    # Tab 1: insert new return
    with tab1:
        st.header("Insert New Return")
        
        # how
        with st.expander("ℹ️ How to insert new return"):
            st.markdown("""
            **Input Rules & Examples:**
            **Must specify:**
            - `product: Laptop` - product name
            - `reason: Defective` - return reason  
            - `category: Electronics` - product category
            - `approved: Yes` - approval status (default: No)
            
            **Automatically identified:**
            - `order: 1234` or `1234` - order id
            - `cost: $128` or `$128` - cost
            - `store: Brooklyn Center` or `at Brooklyn Center` - store name
            - `date: 2025-01-18` or `2025-01-18` - date
            
            **Complete Example:**
            ```
            order: 2100 product: Tablet reason: Missing Accessories cost: $277 store: Sunnyvale Town date: 2025-05-20
            ```
            ```
            order: 1500 product: Tablet reason: defective category: Electronics approved: Yes cost: $300 store: Brooklyn Center date: 2025-07-18
            ```
            """)
        
        # 輸入區
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_input = st.text_input(
                "Describe the return (natural-language):",
                placeholder="e.g., order: 2100 product: Tablet reason: Missing Accessories cost: $277 store: Sunnyvale Town",
                key="user_input"
            )
        
        with col2:
            st.write("")  
            st.write("")  
            if st.button("Insert", type="primary", disabled=not st.session_state.data_loaded):
                if user_input:
                    with st.spinner("Processing..."):
                        result = safe_handle_request("insert", user_input)
                        
                        if isinstance(result, pd.DataFrame):
                            st.success("Record inserted successfully!")
                            st.write(f"Total records: {len(result)}")
                        else:
                            if result is None:
                                st.error("Insert failed: System error - no response")
                            elif isinstance(result, dict) and 'Error' in result:
                                st.error(f"Insert failed: {result['Error']}")
                            else:
                                st.error(f"Insert failed: {result}")
                else:
                    st.warning("Please enter a return description")
        
        # 顯示最近插入的記錄
        if st.session_state.data_loaded:
            st.subheader("Recent Returns")
            try:
                all_returns = safe_handle_request("query")
                if isinstance(all_returns, pd.DataFrame) and not all_returns.empty:
                    # show recent 5 records
                    st.dataframe(all_returns.head(), use_container_width=True)
                else:
                    st.info("No records found")
            except Exception as e:
                st.error(f"Error loading recent returns: {str(e)}")
    
    # Tab 2: all records
    with tab2:
        st.header("All Return Records")
        
        if st.session_state.data_loaded:
            if st.button("Refresh Data"):
                st.rerun()
                
            try:
                all_returns = safe_handle_request("query")
                
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
                    
                    # show all records
                    st.dataframe(all_returns, use_container_width=True)
                    
                    # download options
                    try:
                        csv = all_returns.to_csv(index=False)
                        st.download_button(
                            label="Download as CSV",
                            data=csv,
                            file_name=f"return_records_{datetime.now().strftime('%Y%m%d')}.csv",
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
    
    # Tab 3: statistics
    with tab3:
        st.header("Returns Statistics")
        
        if st.session_state.data_loaded:
            try:
                all_returns = safe_handle_request("query")
                
                if isinstance(all_returns, pd.DataFrame) and not all_returns.empty:
                    # basic statistics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Product Category")
                        if 'product' in all_returns.columns:
                            product_counts = all_returns['product'].value_counts()
                            st.bar_chart(product_counts)
                    
                    with col2:
                        st.subheader("Return Reasons")
                        if 'return_reason' in all_returns.columns:
                            reason_counts = all_returns['return_reason'].value_counts()
                            st.bar_chart(reason_counts)
                    
                    # detailed statistics
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
    
    # Tab 4: generate report
    with tab4:
        st.header("Generate Excel Report")
        
        if st.session_state.data_loaded:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                report_name = st.text_input(
                    "Report filename:",
                    value=f"summary_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
                )
            
            with col2:
                st.write("")
                st.write("")  
                if st.button("Generate Report", type="primary"):
                    with st.spinner("Generating report..."):
                        try:
                            result = safe_handle_request("report", report_name)
                            
                            if result and result.get('success'):
                                st.success(f"Successfully! {report_name}")
                                
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
                                            label="Download Excel Report",
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
    
    # footer
    st.divider()
    st.markdown("""
    ---
    Returns & Warranty RAG System | 2-Agent (Retrieval + Report)
    """)

if __name__ == "__main__":
    main()