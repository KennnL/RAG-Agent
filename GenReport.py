import pandas as pd

class ReportAgent:
    """
    report agent
    """
    def analyze_data(self, data):
        if data is None or (hasattr(data, 'empty') and data.empty):
            return {}
        
        df = pd.DataFrame(data)
        total_returns = len(df)
        
        # product
        product_stats = {}
        if 'product' in df.columns:
            product_stats = df['product'].value_counts().to_dict()
        
        # category
        category_stats = {}
        if 'category' in df.columns:
            category_stats = df['category'].value_counts().to_dict()
        
        # store
        store_stats = {}
        if 'store_name' in df.columns:
            store_stats = df['store_name'].value_counts().to_dict()
        
        # reason
        reason_stats = {}
        if 'return_reason' in df.columns:
            reason_stats = df['return_reason'].value_counts().to_dict()
        
        # cost analysis
        cost_analysis = {}
        if 'cost' in df.columns and df['cost'].notna().any():
            cost_analysis = {
                'total': df['cost'].sum(),
                'average': df['cost'].mean(),
                'max': df['cost'].max(),
                'min': df['cost'].min()
            }
        
        return {
            "total_returns": total_returns,
            "by_product": product_stats,
            "by_category": category_stats,
            "by_store": store_stats,
            "by_reason": reason_stats,
            "cost_analysis": cost_analysis,
            "recent_returns": data[:10] 
        }
    
    def create_report(self, data, output_file="report.xlsx"):
        if data is None or (hasattr(data, 'empty') and data.empty):
            return {"Error": "沒有資料"}
        
        analysis = self.analyze_data(data)
        
        try:
            # Excel
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Summary
                summary_data = []
                summary_data.append(['總退貨數', analysis['total_returns']])
                summary_data.append(['產品種類', len(analysis['by_product'])])
                summary_data.append(['涉及商店', len(analysis['by_store'])])
                
                if analysis['cost_analysis']:
                    summary_data.append(['總成本', f"${analysis['cost_analysis']['total']:.2f}"])
                    summary_data.append(['平均成本', f"${analysis['cost_analysis']['average']:.2f}"])
                
                summary_df = pd.DataFrame(summary_data, columns=['指標', '數值'])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Raw Data
                pd.DataFrame(data).to_excel(writer, sheet_name='Raw Data', index=False)
                
                # Product Analysis
                if analysis['by_product']:
                    product_df = pd.DataFrame(
                        list(analysis['by_product'].items()),
                        columns=['Product', 'Returns Count']
                    ).sort_values('Returns Count', ascending=False)
                    product_df.to_excel(writer, sheet_name='Product Analysis', index=False)
                
                # Reason Analysis
                if analysis['by_reason']:
                    reason_df = pd.DataFrame(
                        list(analysis['by_reason'].items()),
                        columns=['Return Reason', 'Count']
                    ).sort_values('Count', ascending=False)
                    reason_df.to_excel(writer, sheet_name='Reason Analysis', index=False)
                
                # Findings
                findings = self.generate_findings(analysis)
                findings_df = pd.DataFrame(findings, columns=['Findings'])
                findings_df.to_excel(writer, sheet_name='Findings', index=False)
            

            
            # Summary
            return {
                "success": True,
                "file": output_file,
                "summary": {
                    "total": analysis['total_returns'],
                    "top_product": max(analysis['by_product'], key=analysis['by_product'].get) if analysis['by_product'] else None,
                    "top_reason": max(analysis['by_reason'], key=analysis['by_reason'].get) if analysis['by_reason'] else None
                }
            }
            
        except Exception as e:
            print(f"   ✗ 生成報告時發生錯誤: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_findings(self, analysis):
        findings = []
        
        # Product
        if analysis['by_product']:
            top_product = max(analysis['by_product'], key=analysis['by_product'].get)
            count = analysis['by_product'][top_product]
            percentage = (count / analysis['total_returns']) * 100
            findings.append(f"最常退貨產品: {top_product} ({count} 次, {percentage:.1f}%)")
        
        # Store
        if analysis['by_store']:
            top_store = max(analysis['by_store'], key=analysis['by_store'].get)
            findings.append(f"退貨最多商店: {top_store} ({analysis['by_store'][top_store]} 次)")
        
        # Reason
        if analysis['by_reason']:
            top_reason = max(analysis['by_reason'], key=analysis['by_reason'].get)
            findings.append(f"主要退貨原因: {top_reason} ({analysis['by_reason'][top_reason]} 次)")
        
        # Cost
        if analysis['cost_analysis']:
            findings.append(f"總成本: ${analysis['cost_analysis']['total']:.2f}")
            findings.append(f"平均成本: ${analysis['cost_analysis']['average']:.2f}")
        
        return findings

if __name__ == "__main__":
    pass