import os
from dotenv import load_dotenv
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_openai import AzureChatOpenAI
from langchain_community.agent_toolkits.sql.prompt import SQL_PREFIX, SQL_SUFFIX
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType

# Load environment variables
load_dotenv()

class PostgresChatbot:
    def __init__(self):
        # Initialize database connection
        self.db = SQLDatabase.from_uri(
            database_uri=os.getenv("DATABASE_URL"),
            include_tables=os.getenv("INCLUDE_TABLES", "").split(",") if os.getenv("INCLUDE_TABLES") else None,
            sample_rows_in_table_info=3
        )
        
        # Initialize Azure OpenAI LLM
        self.llm = AzureChatOpenAI(
            api_key="65aaa9f6d52e77f1",
            api_version="2024-02-01",
            azure_endpoint="https://mavericks-secureapi.azurewebsites.net/api/azureai",
            deployment_name="gpt-4o",
            temperature=0,
            streaming=True
        )
        
        # Custom prompt for better SQL generation
        self.custom_prompt = ChatPromptTemplate.from_messages([
            ("system", SQL_PREFIX),
            ("human", "{input}"),
            ("system", SQL_SUFFIX)
        ])
        
        # Create SQL agent
        self.agent_executor = create_sql_agent(
            llm=self.llm,
            db=self.db,
            prompt=self.custom_prompt,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            handle_parsing_errors=True
        )

    def run_chat(self):
        print("PostgreSQL Chatbot initialized. Type 'exit' to quit.")
        print("Connected to database with the following tables:")
        print("\n".join([f"- {table}" for table in self.db.get_usable_table_names()]))
        print("\nHow can I help you with your PostgreSQL database today?")
        
        while True:
            try:
                user_input = input("\nYou: ")
                
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                
                if not user_input.strip():
                    continue
                
                print("\nBot: ", end="", flush=True)
                
                # Execute the agent
                response = self.agent_executor.invoke({"input": user_input})
                print(response["output"])
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                continue

if __name__ == "__main__":
    # Check required environment variables
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_OPENAI_API_VERSION",
        "DATABASE_URL"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: The following required environment variables are missing:")
        for var in missing_vars:
            print(f"- {var}")
        exit(1)
    
    # Run the chatbot
    chatbot = PostgresChatbot()
    chatbot.run_chat()