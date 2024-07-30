
# Import the libraries
import mysql.connector
from mysql.connector import Error
from sqlalchemy import *
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os


# Function for executing the MySQL queries using SQLAlchemy
def execute_mysql_query(query, database_name, params=None):
    try:
        # Create the SQLAlchemy engine
        engine = create_engine(
            f"mysql+pymysql://{os.getenv('MYSQL_USERNAME')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{database_name}"
        )
        
        # Create a configured "Session" class
        Session = sessionmaker(bind=engine)
        
        # Create a Session
        session = Session()
        
        # Execute the query
        result = None
        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            session.execute(text(query), params)
            session.commit()
            result = session.rowcount
        else:
            result = session.execute(text(query), params).fetchall()
        
        # Close the session
        session.close()
        return result

    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None


# Function to read all tables into a dictionary of DataFrames
def read_all_tables_to_dfs(database_name):
    try:
        # Create the SQLAlchemy engine
        engine = create_engine(
            f"mysql+pymysql://{os.getenv('MYSQL_USERNAME')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{database_name}"
        )
        
        # Connect to the database
        with engine.connect() as conn:
            # Get the list of all table names
            table_names = pd.read_sql("SHOW TABLES;", conn)
            table_names = table_names.iloc[:, 0].tolist()  # Extract table names from the DataFrame
            
            # Read each table into a DataFrame and store in a dictionary
            tdf = {table: pd.read_sql(f"SELECT * FROM {table};", conn) for table in table_names}
        
        return tdf

    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
