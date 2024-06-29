import psycopg2
from psycopg2 import Error
import os
import streamlit as st

def connect():
    try:
        db_config = {
            'dbname': st.secrets["database"]["DB_NAME"],
            'user': st.secrets["database"]["DB_USER"],
            'password': st.secrets["database"]["DB_PASSWORD"],
            'host': st.secrets["database"]["DB_HOST"],
            'port': st.secrets["database"]["DB_PORT"]
        }
        conn = psycopg2.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None
