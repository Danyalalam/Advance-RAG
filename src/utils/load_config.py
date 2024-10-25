import os
from dotenv import load_dotenv
import yaml
from pyprojroot import here
import shutil
from openai import AzureOpenAI
from langchain_community.chat_models import AzureChatOpenAI
import chromadb

# Load environment variables from a .env file and print confirmation
print("Environment variables are loaded:", load_dotenv())


class LoadConfig:
    def __init__(self) -> None:
        # Load the YAML configuration file for the app
        with open(here("configs/app_config.yml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)

        # Call methods to load different configurations and resources
        self.load_directories(app_config=app_config)
        self.load_llm_configs(app_config=app_config)
        self.load_openai_models()
        self.load_chroma_client()
        self.load_rag_config(app_config=app_config)

        # Uncomment the code below if you want to clean up the uploaded files SQL DB on every fresh run (if it exists)
        # self.remove_directory(self.uploaded_files_sqldb_directory)

    # Load directory paths from the configuration file
    def load_directories(self, app_config):
        # Resolve paths relative to the project root and store them in instance variables
        self.stored_csv_xlsx_directory = here(
            app_config["directories"]["stored_csv_xlsx_directory"])
        self.sqldb_directory = str(here(
            app_config["directories"]["sqldb_directory"]))
        self.uploaded_files_sqldb_directory = str(here(
            app_config["directories"]["uploaded_files_sqldb_directory"]))
        self.stored_csv_xlsx_sqldb_directory = str(here(
            app_config["directories"]["stored_csv_xlsx_sqldb_directory"]))
        self.persist_directory = app_config["directories"]["persist_directory"]

    # Load the configuration for the language models (LLM) from environment variables and the YAML config file
    def load_llm_configs(self, app_config):
        self.model_name = os.getenv("DEPLOYMENT_NAME")  # Get GPT deployment name from environment variables
        self.agent_llm_system_role = app_config["llm_config"]["agent_llm_system_role"]  # Load system role for agent
        self.rag_llm_system_role = app_config["llm_config"]["rag_llm_system_role"]  # Load system role for RAG model
        self.temperature = app_config["llm_config"]["temperature"]  # Load LLM temperature setting
        self.embedding_model_name = os.getenv("GOOGLE_API_KEY")  # Get embedding model name from environment variables

    # Set up OpenAI models (GPT and embedding models) using Azure OpenAI API
    def load_openai_models(self):
        # Get API credentials and endpoint from environment variables
        azure_openai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
        azure_openai_endpoint = os.environ["ENDPOINT_URL"]

        # Initialize Azure OpenAI client with credentials and API version
        self.azure_openai_client = AzureOpenAI(
            api_key=azure_openai_api_key,
            api_version=os.getenv("OPENAI_API_VERSION"),
            azure_endpoint=azure_openai_endpoint
        )

        # Initialize Langchain's Azure Chat OpenAI model with the specified model, temperature, and API key
        self.langchain_llm = AzureChatOpenAI(
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("OPENAI_API_VERSION"),
            azure_deployment=self.model_name,
            model_name=self.model_name,
            temperature=self.temperature,
            azure_endpoint=os.getenv("ENDPOINT_URL")
        )

    # Initialize ChromaDB client for handling embeddings persistence
    def load_chroma_client(self):
        # Set up ChromaDB with a persistent client, storing the path for persistence
        self.chroma_client = chromadb.PersistentClient(
            path=str(here(self.persist_directory)))

    # Load Retrieval-Augmented Generation (RAG) configuration from the YAML file
    def load_rag_config(self, app_config):
        self.collection_name = app_config["rag_config"]["collection_name"]  # Load the ChromaDB collection name
        self.top_k = app_config["rag_config"]["top_k"]  # Load top_k value for retrieval in RAG model

    # Method to remove a directory if it exists
    def remove_directory(self, directory_path: str):
        """
        Removes the specified directory.

        Parameters:
            directory_path (str): The path of the directory to be removed.

        Raises:
            OSError: If an error occurs during the directory removal process.

        Returns:
            None
        """
        # Check if the directory exists
        if os.path.exists(directory_path):
            try:
                # Remove the directory and its contents
                shutil.rmtree(directory_path)
                print(
                    f"The directory '{directory_path}' has been successfully removed.")
            except OSError as e:
                # Print error if removal fails
                print(f"Error: {e}")
        else:
            # Print message if the directory doesn't exist
            print(f"The directory '{directory_path}' does not exist.")
