from Retrieval import RetrievalAgent
from GenReport import ReportAgent

class Controller:
    """
    Controller - control the work of the two agents
    """
    def __init__(self):
        print("Controller Ready")
        self.retrieval_agent = RetrievalAgent()
        self.report_agent = ReportAgent()
    
    def handle_request(self, action, data=None):
        """
        Assign the request
        """
        #print(f"\nController received request: {action}")
        
        try:
            if action == "load_csv":
                return self.retrieval_agent.load_csv(data)
            
            elif action == "insert":
                return self.retrieval_agent.insert_return(data)
            
            elif action == "query":
                return self.retrieval_agent.get_all_returns()
            
            elif action == "report":
                all_data = self.retrieval_agent.get_all_returns()
                return self.report_agent.create_report(all_data, data)
            
            else:
                return {"Error"}
                
        except Exception as e:
            return {"Error": str(e)}
    
    def close(self):
        """Close database connections"""
        if self.retrieval_agent:
            self.retrieval_agent.close()