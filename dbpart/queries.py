import requests
import json
import streamlit as st
from dbpart import myconnection
from utils import helpers
import logging

# Function to check login credentials against PostgreSQL
def fetch_subject_topics(subject_id):
    conn = myconnection.connect()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT processed_strings FROM subjects WHERE id = %s", (subject_id,))
            result = cursor.fetchone()
            conn.close()

            if result is not None and result[0] is not None:
                processed_strings = result[0]
                if isinstance(processed_strings, list):
                    return processed_strings
                elif isinstance(processed_strings, str):
                    try:
                        return json.loads(processed_strings)
                    except json.JSONDecodeError as json_error:
                        logging.error(f"JSON Decode Error for subject_id {subject_id}: {json_error}")
                        logging.error(f"Raw data: {processed_strings}")
                        return None
                else:
                    logging.error(f"Unexpected data type for processed_strings: {type(processed_strings)}")
                    return None
            else:
                logging.warning(f"No processed_strings found for subject_id {subject_id}")
                return None
        except Exception as e:
            logging.error(f"Database error in fetch_subject_topics for subject_id {subject_id}: {e}")
            return None
    else:
        logging.error("Failed to connect to database in fetch_subject_topics")
        return None

def check_login(username, password):
    conn = myconnection.connect()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]  # Return user ID
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    else:
        return None

# Function to register a user
def register_user(username, password):
    conn = myconnection.connect()
    if conn:
        try:
            cursor = conn.cursor()
            # Check if the username already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                conn.close()
                return "Username already exists"
            # Insert the new user
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            conn.close()
            return "User registered successfully"
        except Exception as e:
            print(f"Error: {e}")
            return "Error registering user"
    else:
        return "Error connecting to database"

# Function to fetch uploaded subjects for a user
def fetch_uploaded_subjects(user_id):
    conn = myconnection.connect()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, subject_name, uploaded_date FROM subjects WHERE user_id = %s", (user_id,))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"Error: {e}")
            return []
    else:
        return []

# Function to save user progress
def save_progress(user_id, progress):
    conn = myconnection.connect()
    if conn:
        try:
            cursor = conn.cursor()
            for topic, completed in progress.items():
                cursor.execute("""
                    INSERT INTO user_progress (user_id, topic, completed)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, topic) DO UPDATE
                    SET completed = EXCLUDED.completed
                """, (user_id, topic, completed))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving progress: {e}")
            return False
    return False

# Function to load user progress
def load_progress(user_id):
    conn = myconnection.connect()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT topic, completed FROM user_progress WHERE user_id = %s", (user_id,))
            results = cursor.fetchall()
            conn.close()
            return {topic: bool(completed) for topic, completed in results}
        except Exception as e:
            print(f"Error loading progress: {e}")
            return {}
    return {}

# Function to upload subject and processed strings to PostgreSQL database
def upload_subject(user_id, subject_name, result):
    conn = myconnection.connect()
    if conn:
        try:
            cursor = conn.cursor()
            processed_strings_json = json.dumps(result)  # Always convert to JSON string
            cursor.execute("INSERT INTO subjects (user_id, subject_name, processed_strings) VALUES (%s, %s, %s)",
                           (user_id, subject_name, processed_strings_json))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error in upload_subject: {e}")
            return False
    return False

# Function to fetch first two video links from YouTube search
def get_first_two_video_links(query, api_key):
    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&q={query}&part=snippet&type=video&maxResults=2"
    try:
        response = requests.get(url)
        data = response.json()
        video_links = []
        for item in data['items']:
            video_links.append(f"https://www.youtube.com/watch?v={item['id']['videoId']}")
        return video_links
    except Exception as e:
        print(f"Error fetching video links: {e}")
        return []

# Function to fetch YouTube video details including thumbnail and title using API key
def fetch_youtube_details(video_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/videos?key={api_key}&id={video_id}&part=snippet"
    try:
        response = requests.get(url)
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            snippet = data['items'][0]['snippet']
            if 'maxres' in snippet['thumbnails']:
                thumbnail_url = snippet['thumbnails']['maxres']['url']
            elif 'high' in snippet['thumbnails']:
                thumbnail_url = snippet['thumbnails']['high']['url']
            else:
                thumbnail_url = snippet['thumbnails']['medium']['url']
            title = snippet['title']
            return thumbnail_url, title
        else:
            return None, None
    except Exception as e:
        print(f"Error fetching YouTube video details: {e}")
        return None, None

# Function to embed YouTube video using YouTube Player API
def embed_youtube_video(video_link):
    youtube_id = video_link.split('=')[-1]
    st.markdown(
        f'<iframe width="640" height="360" src="https://www.youtube.com/embed/{youtube_id}" frameborder="0" allowfullscreen></iframe>',
        unsafe_allow_html=True)

# Function to perform Google search using Custom Search API and retrieve first search result link
def google_search(query, api_key, cse_id, num_results=1):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id,
        'num': num_results
    }
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        search_results = response.json()
        return search_results['items'][0]['link'] if 'items' in search_results else None
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to set background image
def set_background(png_file):
    bin_str = helpers.get_base64(png_file)
    page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
        }}
        </style>
        '''
    st.markdown(page_bg_img, unsafe_allow_html=True)