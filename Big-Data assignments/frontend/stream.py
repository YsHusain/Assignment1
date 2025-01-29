import streamlit as st
import re
import requests

# Add a title to the app
st.title("Content Extraction Tool")

# Sidebar for selecting where to extract content from
st.sidebar.header("Select the Content Extraction Source")
option = st.sidebar.selectbox("Where do you want to extract content from?", ["Web-Site", "Pdf"])

# Global variable to hold scraped content (to prevent multiple extractions)
scraped_content = None

# Function to call FastAPI for web scraping
def fetch_scraped_content(url, tool_option):
    global scraped_content
    
    # Only fetch if the content hasn't been scraped yet
    if scraped_content:
        st.info("Content already fetched!")
        return
    
    endpoint = "http://127.0.0.1:8000/scrape-open-source/" if tool_option == "Open-Source" else "http://127.0.0.1:8000/scrape_article-enterprise/"
    payload = {"url": url}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        
        # Check if response is successful
        if response.status_code == 200:
            st.success("Content extracted successfully!")
            try:
                # Parse the response as JSON
                data = response.json()
                scraped_content = data  # Save the content for future use

                # De-duplicate content in the scraped data
                unique_links = set(data.get('links', []))  # Removing duplicate links
                unique_paragraphs = set(data.get('paragraphs', []))  # Removing duplicate paragraphs
                
                # Display cleaned-up content
                st.write("Unique Links:", unique_links)
                st.write("Unique Paragraphs:", unique_paragraphs)
                
                # Assuming data contains a 'file_name' with the result
                file_name = data.get('file_name', None)
                if file_name:
                    st.download_button("Download Scraped Content", data=file_name, file_name=file_name)

                # Display images if any
                images = data.get('images', [])
                if images:
                    st.subheader("Images:")
                    for img_url in images:
                        st.image(img_url)  # Display image from URL
                # st.image("../backend/downloaded_images/0bbcd0a6f4bcd81ccb1049a52736406e.jpg")
                
            except ValueError as e:
                st.error(f"Error parsing response as JSON: {e}")
                st.write("Response content is not valid JSON. Here's the raw response:", response.text)
        else:
            st.error(f"Error: {response.text}")

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")

# Function to call FastAPI for PDF processing
def fetch_pdf_content(uploaded_file):
    endpoint = "http://127.0.0.1:8000/process-pdf/"
    files = {"file": uploaded_file.getvalue()}
    
    try:
        response = requests.post(endpoint, files=files)
        
        # Check if response is successful
        if response.status_code == 200:
            st.success("PDF content extracted successfully!")
            try:
                # Parse the response as JSON
                data = response.json()

                # Display extracted content
                paragraphs = data.get('paragraphs', [])
                st.write("Extracted Paragraphs:")
                for paragraph in paragraphs:
                    st.write(paragraph)

                # Assuming data contains a 'file_name' with the result
                file_name = data.get('file_name', None)
                if file_name:
                    st.download_button("Download Extracted Content", data=file_name, file_name=file_name)

            except ValueError as e:
                st.error(f"Error parsing response as JSON: {e}")
                st.write("Response content is not valid JSON. Here's the raw response:", response.text)
        else:
            st.error(f"Error: {response.text}")

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")

# URL Validation
def is_valid_url(url):
    pattern = r'^(https?://)?([a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+)(:[0-9]+)?(/.*)?$'
    return re.match(pattern, url) is not None

# Main screen content based on sidebar selection
if option == "Web-Site":
    st.sidebar.subheader("Choose the Extraction Tool for Web-Site")
    tool_option = st.sidebar.selectbox("Which tool would you prefer?", ["Open-Source", "Enterprise"])

    url = st.sidebar.text_input("Enter URL here:")
    if st.sidebar.button("Extract Content"):
        if url:
            if is_valid_url(url):
                fetch_scraped_content(url, tool_option)
            else:
                st.error("Invalid URL! Please enter a valid URL starting with 'http://' or 'https://'.")
        else:
            st.error("Please enter a URL.")

elif option == "Pdf":
    st.sidebar.subheader("Upload a PDF File")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
    
    if st.sidebar.button("Extract PDF Content"):
        if uploaded_file:
            fetch_pdf_content(uploaded_file)
        else:
            st.error("Please upload a PDF file.")
