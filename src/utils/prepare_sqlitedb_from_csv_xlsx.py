import os
import pandas as pd
from utils.load_config import LoadConfig
from sqlalchemy import create_engine, inspect

class PrepareSQLFromTabularData:
    """
    A class that prepares a SQL database from CSV or XLSX files within a specified directory.

    This class reads each file, converts the data to a DataFrame, and then
    stores it as a table in a SQLite database, which is specified by the application configuration.
    """
    def __init__(self, files_dir) -> None:
        """
        Initialize an instance of PrepareSQLFromTabularData.

        Args:
            files_dir (str): The directory containing the CSV or XLSX files to be converted to SQL tables.
        """
        APPCFG = LoadConfig()  # Load the configuration using LoadConfig class
        self.files_directory = files_dir  # Set the directory for files
        self.file_dir_list = os.listdir(files_dir)  # List all files in the directory
        db_path = APPCFG.stored_csv_xlsx_sqldb_directory  # Get the database path from the config
        if not os.path.exists(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path))  # Create the directory if it doesn't exist
        db_path = f"sqlite:///{db_path}"  # Format the path for SQLite
        self.engine = create_engine(db_path)  # Create a connection engine for SQLite database
        print("Number of csv files:", len(self.file_dir_list))  # Print the number of files found

    def _prepare_db(self):
        """
        Private method to convert CSV/XLSX files from the specified directory into SQL tables.

        Each file's name (excluding the extension) is used as the table name.
        The data is saved into the SQLite database referenced by the engine attribute.
        """
        for file in self.file_dir_list:
            full_file_path = os.path.join(self.files_directory, file)  # Get full file path
            file_name, file_extension = os.path.splitext(file)  # Split the file name and extension
            if file_extension == ".csv":  # If it's a CSV file
                df = pd.read_csv(full_file_path)  # Read CSV into a pandas DataFrame
            elif file_extension == ".xlsx":  # If it's an Excel file
                df = pd.read_excel(full_file_path)  # Read Excel into a pandas DataFrame
            try:
                df.to_sql(file_name, self.engine, index=False)  # Write the DataFrame to SQL table
            except Exception as e:
                print(f"Error saving {file_name} to SQL: {e}")  # Print error message if saving fails
                raise ValueError("The selected file type is not supported")  # Error if unsupported file type
            df.to_sql(file_name, self.engine, index=False)  # Write the DataFrame to SQL table
        print("==============================")
        print("All csv files are saved into the sql database.")  # Print completion message

    def _validate_db(self):
        """
        Private method to validate the tables stored in the SQL database.

        It prints out all available table names in the created SQLite database
        to confirm that the tables have been successfully created.
        """
        insp = inspect(self.engine)  # Create a database inspector
        table_names = insp.get_table_names()  # Get the names of all tables in the database
        print("==============================")
        print("Available table names in created SQL DB:", table_names)  # Print available tables
        print("==============================")

    def run_pipeline(self):
        """
        Public method to run the data import pipeline, which includes preparing the database
        and validating the created tables. It is the main entry point for converting files
        to SQL tables and confirming their creation.
        """
        self._prepare_db()  # Run the method to import data into SQL
        self._validate_db()  # Validate that the tables were created
