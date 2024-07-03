# SyllabusScholar

## Overview

SyllabusScholar is a web application designed to manage and analyze academic syllabi.

## Prerequisites

- Python 3.x
- Virtual environment tool (optional but recommended)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/mubaid95/SyllabusScholar.git
   cd SyllabusScholar

2. Activate Enviornment:      
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. Set-up Enviornment Variables:
   
 a) For DataBase: 
 
We have created a Online Database Using Supbase- 
https://supabase.com/

DB_NAME= your_database_name
DB_USER= your_database_username
DB_PASSWORD= your_database_password
DB_HOST= your_database_host_network
DB_PORT= your_port_number

 b) Google Data Api:

YOUTUBE_API_KEY = your_youtube_data_api_key
GOOGLE_API_KEY = your_google_data_api_key
CSE_ID= your_custom_search_api_key

c) Chat with Pdf Api:

We used Chat with pdf Api which will allow use to Extract Topics from the pdf
https://www.chatpdf.com/docs/api/backend

CHATPDF_API_KEY = your_chat_with_pdf_key

4.  Install dependencies:
   ```sh
   pip install -r requirements.txt


5. Running the Application 

  streamlit run app.py


## File Structure

.idea/: IDE-specific configurations.

dbpart/: Database-related scripts.

processing/: Data processing scripts.

static/: Static files (CSS, JS, images).

utils/: Utility functions.

.gitignore: Git ignore rules.

app.py: Main application script.

requirements.txt: Project dependencies.

## Key Functions
# app.py
main(): Initializes and starts the application.
load_config(): Loads configuration settings.
setup_routes(): Sets up the application routes.
# dbpart/
db_connection.py: Database connection management.
models.py: Database models definition.
# processing/
data_cleaning.py: Data cleaning functions.
data_analysis.py: Data analysis functions.
# utils/
helpers.py: Miscellaneous helper functions.
logger.py: Logging setup and management.


## Contributing
Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

