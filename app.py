import streamlit as st
from dbpart import queries
from processing import extract, process
from utils import helpers
import requests
import re
import hashlib
import os
from dotenv import load_dotenv


def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        main_page()
    else:
        st.sidebar.title("Welcome")
        page = st.sidebar.radio("Choose an option", ["Login", "Register"])
        if page == "Login":
            login_page()
        else:
            register_page()


def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_id = queries.check_login(username, hashlib.sha256(password.encode('utf-8')).hexdigest())
        if user_id is not None:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['user_id'] = user_id
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")


def register_page():
    st.title("Register")
    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if new_password != confirm_password:
            st.error("Passwords do not match")
        elif not new_username or not new_password:
            st.error("Username and password cannot be empty")
        else:
            if queries.register_user(new_username, hashlib.sha256(new_password.encode('utf-8')).hexdigest()):
                st.success("Registration successful! You can now login.")
            else:
                st.error("Registration failed. Username might already exist.")


def process_uploaded_file(uploaded_file):
    file_type = uploaded_file.type
    if file_type == "application/pdf":
        with open("uploaded_file.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

        api_key = os.getenv('CHATPDF_API_KEY')
        url = 'https://api.chatpdf.com/v1/sources/add-file'
        headers = {'x-api-key': api_key}

        with open('uploaded_file.pdf', 'rb') as file:
            files = {'file': file}
            response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            source_id = response.json()['sourceId']
            chat_url = 'https://api.chatpdf.com/v1/chats/message'
            request_body = {
                "sourceId": source_id,
                "messages": [
                    {
                        "role": "user",
                        "content": "Give list of topics and subtopics. If there is a comma in between, consider them a new topic. And don't write anything else and remove Numbers and dash ( - )"
                    }
                ]
            }

            response = requests.post(chat_url, headers=headers, json=request_body)

            if response.status_code == 200:
                content = response.json()['content']
                topics = content.split('\n')

                arr = []
                for topic in topics:
                    if len(topic) < 2:
                        continue
                    subtopics = topic.split(',')
                    for subtopic in subtopics:
                        cleaned_subtopic = re.sub(r'[^\w\s]', '', subtopic.strip())
                        if cleaned_subtopic:
                            arr.append(cleaned_subtopic)

                return arr if arr else None
            else:
                st.error(f"Failed to extract topics. Status code: {response.status_code}")
        else:
            st.error(f"Failed to upload PDF. Status code: {response.status_code}")
    elif file_type in ["image/jpeg", "image/jpg"]:
        with open("uploaded_image.jpg", "wb") as f:
            f.write(uploaded_file.getbuffer())
        lines = extract.extract_text_from_image_easyocr("uploaded_image.jpg")
        s_string = process.get_important_lines(lines)
        return process.process_strings(s_string)
    return None


def on_topic_select():
    st.session_state.selected_topic = st.session_state.topic_selector


def display_topic_content(topic, youtube_api_key, google_api_key, cse_id):
    st.subheader(f"Results for: {topic}")
    first_link = queries.google_search(topic, google_api_key, cse_id)
    video_links = queries.get_first_two_video_links(topic, youtube_api_key)

    if first_link:
        st.markdown(f"Read an article: \n[{first_link}]({first_link})")
    else:
        st.markdown(f"No search results found for {topic}")

    st.markdown("YouTube Videos:")
    for video_link in video_links:
        queries.embed_youtube_video(video_link)
        thumbnail_url, title = queries.fetch_youtube_details(video_link.split('=')[-1], youtube_api_key)
        for i in range(5):
            st.write("\n")


def main_page():
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    google_api_key = os.getenv('GOOGLE_API_KEY')
    cse_id = os.getenv('CSE_ID')

    helpers.set_background('static/1176274.jpg')

    st.title("PDF/Image Syllabus Processor")

    user_id = st.session_state.get('user_id')
    if user_id is None:
        st.error("User ID not found. Please login.")
        return

    action = st.radio("Choose an action", ["Upload new file", "View saved subjects"])

    if action == "Upload new file":
        uploaded_file = st.file_uploader("Choose a PDF or JPG file", type=["pdf", "jpg", "jpeg"])
        if uploaded_file is not None:
            if st.button("Process File"):
                st.session_state.result = process_uploaded_file(uploaded_file)
                st.success("File processed successfully!")
                st.session_state.current_action = "Upload new file"
    else:  # View saved subjects
        uploaded_subjects = queries.fetch_uploaded_subjects(user_id)
        if uploaded_subjects:
            selected_subject = st.selectbox("Select a subject", [subject[1] for subject in uploaded_subjects])
            subject_id = next(subject[0] for subject in uploaded_subjects if subject[1] == selected_subject)
            if 'current_action' not in st.session_state or st.session_state.current_action != "View saved subjects" or st.session_state.get(
                    'current_subject') != selected_subject:
                st.session_state.result = queries.fetch_subject_topics(subject_id)
                st.session_state.current_subject = selected_subject
                st.session_state.current_action = "View saved subjects"
        else:
            st.write("No saved subjects found.")
            return

    if 'result' in st.session_state:
        if st.session_state.result is None:
            st.error("Failed to fetch topics for this subject. Please try again or contact support.")
        elif len(st.session_state.result) == 0:
            st.write("No topics found for this subject.")
        else:
            progress = queries.load_progress(user_id)
            total_topics = len(st.session_state.result)
            completed_topics = sum(progress.get(topic, False) for topic in st.session_state.result)

            st.sidebar.subheader("Mark Topics as Completed")
            progress_bar = st.sidebar.progress(completed_topics / total_topics)
            progress_text = st.sidebar.empty()
            progress_text.markdown(f"Progress: **{completed_topics}/{total_topics}** topics completed")

            for index, topic in enumerate(st.session_state.result):
                checkbox_key = f"{topic}_{index}"
                is_completed = st.sidebar.checkbox(topic, value=progress.get(topic, False), key=checkbox_key)
                if progress.get(topic, False) != is_completed:
                    progress[topic] = is_completed
                    completed_topics = sum(progress.get(topic, False) for topic in st.session_state.result)
                    progress_bar.progress(completed_topics / total_topics)
                    progress_text.markdown(f"Progress: **{completed_topics}/{total_topics}** topics completed")

                    # Save progress immediately
                    if queries.save_progress(user_id, progress):
                        take=1
                    else:
                        st.sidebar.error("Failed to save progress. Please try again.")

            if 'selected_topic' not in st.session_state or st.session_state.selected_topic not in st.session_state.result:
                st.session_state.selected_topic = st.session_state.result[0]

            selected_topic = st.selectbox("Select a topic", st.session_state.result, key='topic_selector',
                                          index=st.session_state.result.index(st.session_state.selected_topic))

            if selected_topic != st.session_state.selected_topic:
                st.session_state.selected_topic = selected_topic
                st.experimental_rerun()

            if st.session_state.selected_topic:
                display_topic_content(st.session_state.selected_topic, youtube_api_key, google_api_key, cse_id)

            if action == "Upload new file" and uploaded_file is not None:
                st.subheader("Upload New Subject")
                new_subject_name = st.text_input("Subject Name")
                if st.button("Upload Subject"):
                    if new_subject_name:
                        if queries.upload_subject(user_id, new_subject_name, st.session_state.result):
                            st.success(f"Subject '{new_subject_name}' uploaded successfully!")
                        else:
                            st.error("Failed to upload subject. Please try again.")
    else:
        st.write("Please upload a file or select a saved subject to proceed.")



if __name__ == "__main__":
    main()