import streamlit as st
import re
import requests
import boto3
import os
from datetime import datetime
import json

# URL Validation
def is_valid_url(url):
    pattern = r'^(https?://)?([a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+)(:[0-9]+)?(/.*)?$'
    return re.match(pattern, url) is not None

def display_content(data, tool_option):
    """Display the extracted content in a structured way"""
    # Title
    if 'title' in data:
        st.title(data['title'])
    
    # Content/Text
    st.header("📄 Content")
    if 'paragraphs' in data:
        for paragraph in data['paragraphs']:
            if paragraph.strip():  # Only display non-empty paragraphs
                st.write(paragraph)
                st.markdown("---")
    
    # Links
    if 'links' in data and data['links']:
        st.header("🔗 Important Links")
        col1, col2 = st.columns(2)
        for idx, link in enumerate(data['links']):
            with col1 if idx % 2 == 0 else col2:
                if 'text' in link and 'url' in link:
                    st.markdown(f"- [{link['text']}]({link['url']})")
    
    # Images
    if 'images' in data and data['images']:
        st.header("🖼️ Images")
        cols = st.columns(2)
        for idx, img in enumerate(data['images']):
            try:
                with cols[idx % 2]:
                    caption = img.get('caption', '') or img.get('alt', '')
                    st.image(
                        img['src'],
                        caption=caption,
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Could not load image: {str(e)}")

def fetch_scraped_content(url, tool_option):
    """Fetch and display content from the API"""
    endpoint = "http://127.0.0.1:8000/scrape-open-source/" if tool_option == "Open-Source" else "http://127.0.0.1:8000/scrape-article-enterprise/"
    
    try:
        with st.spinner('Extracting content...'):
            response = requests.post(
                endpoint,
                json={"url": url},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                st.success("Content extracted successfully!")
                data = response.json()
                
                # Debug information
                st.write(f"Number of images found: {len(data.get('images', []))}")
                
                display_content(data, tool_option)
                
                # Add download button for JSON content
                st.download_button(
                    label="Download Extracted Content (JSON)",
                    data=json.dumps(data, indent=2),
                    file_name=f"extracted_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.error(f"Error: {response.text}")
                print(f"API Error Response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        print(f"Request Exception: {str(e)}")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        print(f"General Exception: {str(e)}")

def fetch_pdf_content(uploaded_file, tool_option):
    """Process uploaded PDF file using either enterprise or opensource processor"""
    endpoint = "http://127.0.0.1:8000/process-pdf/enterprise" if tool_option == "Enterprise" else "http://127.0.0.1:8000/process-pdf/opensource"
    
    try:
        with st.spinner('Processing PDF...'):
            files = {"file": uploaded_file}
            response = requests.post(endpoint, files=files)
            
            if response.status_code == 200:
                st.success("PDF processed successfully!")
                data = response.json()
                
                if tool_option == "Enterprise":
                    # Display enterprise processor results
                    st.write("### Output Files:")
                    st.write(f"- ZIP Output: {data['output_zip']}")
                    st.write(f"- Markdown Output: {data['markdown_output']}")
                    
                    # Try to read and display markdown content
                    try:
                        with open(data['markdown_output'], 'r', encoding='utf-8') as f:
                            markdown_content = f.read()
                            st.markdown(markdown_content)
                            
                            # Add download buttons
                            with open(data['output_zip'], 'rb') as zip_file:
                                st.download_button(
                                    label="Download ZIP Output",
                                    data=zip_file,
                                    file_name=f"extracted_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                    mime="application/zip"
                                )
                            
                            st.download_button(
                                label="Download Markdown",
                                data=markdown_content,
                                file_name=f"extracted_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown"
                            )
                    except Exception as e:
                        st.error(f"Error reading output files: {str(e)}")
                
                else:  # Open Source
                    # Display extracted content statistics
                    st.write("### Extracted Content Statistics:")
                    stats = data['extracted_content']
                    st.write(f"- Text sections: {stats['text_count']}")
                    st.write(f"- Images found: {stats['images_count']}")
                    st.write(f"- Tables detected: {stats['tables_count']}")
                    st.write(f"- Output directory: {stats['output_directory']}")
                    
                    # Display some extracted text if available
                    if 'text' in stats and stats['text']:
                        st.write("### Sample Extracted Text:")
                        st.write(stats['text'][:1000] + "..." if len(stats['text']) > 1000 else stats['text'])
                    
                    # Add download button for the complete results
                    st.download_button(
                        label="Download Results (JSON)",
                        data=json.dumps(data, indent=2),
                        file_name=f"pdf_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            else:
                st.error(f"Error: {response.text}")
                print(f"API Error Response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        print(f"Request Exception: {str(e)}")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        print(f"General Exception: {str(e)}")

# Main screen content based on sidebar selection
def main():
    # Add a title to the app
    st.title("Content Extraction Tool")
    # Sidebar for selecting where to extract content from
    st.sidebar.header("Select the Content Extraction Source")
    option = st.sidebar.selectbox("Where do you want to extract content from?", ["Web-Site", "Pdf"])

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
        st.sidebar.subheader("Choose the PDF Processing Tool")
        tool_option = st.sidebar.selectbox("Which tool would you prefer?", ["Open-Source", "Enterprise"])
        
        uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
        
        if st.sidebar.button("Process PDF"):
            if uploaded_file:
                fetch_pdf_content(uploaded_file, tool_option)
            else:
                st.error("Please upload a PDF file.")


if __name__ == "__main__":
    main()