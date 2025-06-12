import os
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_openai import AzureChatOpenAI
from langchain_community.agent_toolkits.sql.prompt import SQL_PREFIX, SQL_SUFFIX
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType

class PostgresChatbot:
    def __init__(self):
        # Direct configuration values (no .env needed)
        self.config = {
            "azure": {
                "api_key": "65aaa9f6d52e77f1",
                "api_version": "2024-02-01",
                "endpoint": "https://mavericks-secureapi.azurewebsites.net/api/azureai",
                "deployment": "gpt-4o"
            },
            "database": {
                "url": "postgresql+psycopg2://postgres:projectmgnt@localhost/project_management",
                "include_tables": None  # None means include all tables
            }
        }

        # Initialize database connection with error handling
        try:
            self.db = SQLDatabase.from_uri(
                database_uri=self.config["database"]["url"],
                include_tables=self.config["database"]["include_tables"],
                sample_rows_in_table_info=2  # Reduced for better performance
            )
            print("✓ Database connection established")
        except Exception as db_error:
            print(f"Database connection failed: {db_error}")
            raise

        # Initialize Azure OpenAI with error handling
        try:
            self.llm = AzureChatOpenAI(
                api_key=self.config["azure"]["api_key"],
                api_version=self.config["azure"]["api_version"],
                azure_endpoint=self.config["azure"]["endpoint"],
                deployment_name=self.config["azure"]["deployment"],
                temperature=0,
                max_retries=2,
                timeout=30
            )
            print("✓ Azure OpenAI configured")
        except Exception as llm_error:
            print(f"Azure OpenAI setup failed: {llm_error}")
            raise

        # Create SQL agent with robust configuration
        self.agent = create_sql_agent(
            llm=self.llm,
            db=self.db,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            early_stopping_method="generate"
        )

    def run_chat(self):
        print("\nPostgreSQL Chatbot Ready")
        print("Available Tables:")
        print("\n".join([f"- {table}" for table in self.db.get_usable_table_names()]))
        print("\nType your question or 'exit' to quit\n")

        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                    
                if not user_input:
                    continue
                
                print("Bot: ", end="", flush=True)
                
                try:
                    response = self.agent.invoke({"input": user_input})
                    print(response.get("output", "No response generated"))
                except Exception as e:
                    print(f"Error processing query: {e}")
                    print("Please try rephrasing your question.")
                    
            except KeyboardInterrupt:
                print("\nSession ended by user")
                break
            except Exception as e:
                print(f"\nUnexpected error: {e}")
                continue

if __name__ == "__main__":
    try:
        print("Starting PostgreSQL Chatbot...")
        chatbot = PostgresChatbot()
        chatbot.run_chat()
    except Exception as e:
        print(f"Failed to initialize chatbot: {e}")
        print("Please check your configuration and try again.")