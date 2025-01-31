# import streamlit as st
# import re
# import requests

# # Add a title to the app
# st.title("Content Extraction Tool")

# # Sidebar for selecting where to extract content from
# st.sidebar.header("Select the Content Extraction Source")
# option = st.sidebar.selectbox("Where do you want to extract content from?", ["Web-Site", "Pdf"])

# # Global variable to hold scraped content (to prevent multiple extractions)
# scraped_content = None

# def fetch_scraped_content(url, tool_option):
#     global scraped_content
    
#     endpoint = "http://127.0.0.1:8000/scrape-open-source/" if tool_option == "Open-Source" else "http://127.0.0.1:8000/scrape_article-enterprise/"
#     payload = {"url": url}
#     headers = {"Content-Type": "application/json"}

#     try:
#         response = requests.post(endpoint, json=payload, headers=headers)
        
#         if response.status_code == 200:
#             st.success("Content extracted successfully!")
#             try:
#                 data = response.json()
                
#                 # Clear previous content
#                 scraped_content = None

#                 # Create containers for different content types
#                 title_container = st.container()
#                 content_container = st.container()
#                 links_container = st.container()
#                 images_container = st.container()

#                 with title_container:
#                     if tool_option == "Open-Source":
#                         if 'title' in data:
#                             st.title(data['title'])
#                     else:  # Enterprise
#                         if 'objects' in data and len(data['objects']) > 0:
#                             article = data['objects'][0]
#                             if 'title' in article:
#                                 st.title(article['title'])
                
#                 with content_container:
#                     st.header("📄 Content")
#                     if tool_option == "Open-Source":
#                         # Handle paragraphs with better formatting
#                         paragraphs = data.get('paragraphs', [])
#                         if paragraphs:
#                             # Clean and filter paragraphs
#                             cleaned_paragraphs = []
#                             for paragraph in paragraphs:
#                                 # Clean up whitespace and remove empty lines
#                                 cleaned = ' '.join(paragraph.split())
#                                 # Only include paragraphs that are meaningful
#                                 if len(cleaned) > 5 and cleaned not in cleaned_paragraphs:
#                                     cleaned_paragraphs.append(cleaned)
                            
#                             # Display cleaned paragraphs
#                             for paragraph in cleaned_paragraphs:
#                                 st.write(paragraph)
#                                 st.markdown("---")
#                     else:  # Enterprise
#                         if 'objects' in data and len(data['objects']) > 0:
#                             article = data['objects'][0]
#                             if 'text' in article:
#                                 paragraphs = article['text'].split('\n')
#                                 for paragraph in paragraphs:
#                                     cleaned = ' '.join(paragraph.split())
#                                     if len(cleaned) > 5:
#                                         st.write(cleaned)
#                                         st.markdown("---")

#                 with links_container:
#                     st.header("🔗 Important Links")
#                     if tool_option == "Open-Source":
#                         links = data.get('links', [])
#                     else:  # Enterprise
#                         links = []
#                         if 'objects' in data and len(data['objects']) > 0:
#                             article = data['objects'][0]
#                             links = article.get('links', [])
                    
#                     if links:
#                         col1, col2 = st.columns(2)
#                         for idx, link in enumerate(links):
#                             if tool_option == "Open-Source":
#                                 url = link.get('url', '')
#                                 text = link.get('text', '').strip()
#                             else:  # Enterprise
#                                 url = link.get('href', '')
#                                 text = link.get('anchor', '').strip()
                            
#                             if text and len(text) > 1 and not text.isspace():
#                                 with col1 if idx % 2 == 0 else col2:
#                                     st.markdown(f"- [{text}]({url})")

#                 with images_container:
#                     st.header("🖼️ Images")
#                     if tool_option == "Open-Source":
#                         images = data.get('images', [])
#                     else:  # Enterprise
#                         images = []
#                         if 'objects' in data and len(data['objects']) > 0:
#                             article = data['objects'][0]
#                             images = article.get('images', [])
                    
#                     if images:
#                         cols = st.columns(2)
#                         for idx, img in enumerate(images):
#                             if tool_option == "Open-Source":
#                                 img_src = img.get('src', '')
#                                 img_alt = img.get('alt', '')
#                             else:  # Enterprise
#                                 img_src = img.get('url', '')
#                                 img_alt = img.get('title', '')
                            
#                             if img_src and img_src.startswith(('http://', 'https://')):
#                                 try:
#                                     with cols[idx % 2]:
#                                         st.image(
#                                             img_src,
#                                             caption=img_alt,
#                                             use_container_width= True
#                                         )
#                                 except Exception as e:
#                                     st.error(f"Could not load image: {img_src}")

#                 # Store the processed content
#                 scraped_content = data

#             except ValueError as e:
#                 st.error(f"Error parsing response as JSON: {e}")
#                 st.write("Response content:", response.text)
#         else:
#             st.error(f"Error: {response.text}")

#     except requests.exceptions.RequestException as e:
#         st.error(f"Request failed: {e}")

# # Function to call FastAPI for PDF processing
# def fetch_pdf_content(uploaded_file):
#     endpoint = "http://127.0.0.1:8000/process-pdf/"
#     files = {"file": uploaded_file.getvalue()}
    
#     try:
#         response = requests.post(endpoint, files=files)
        
#         # Check if response is successful
#         if response.status_code == 200:
#             st.success("PDF content extracted successfully!")
#             try:
#                 # Parse the response as JSON
#                 data = response.json()

#                 # Display extracted content
#                 paragraphs = data.get('paragraphs', [])
#                 st.write("Extracted Paragraphs:")
#                 for paragraph in paragraphs:
#                     st.write(paragraph)

#                 # Assuming data contains a 'file_name' with the result
#                 file_name = data.get('file_name', None)
#                 if file_name:
#                     st.download_button("Download Extracted Content", data=file_name, file_name=file_name)

#             except ValueError as e:
#                 st.error(f"Error parsing response as JSON: {e}")
#                 st.write("Response content is not valid JSON. Here's the raw response:", response.text)
#         else:
#             st.error(f"Error: {response.text}")

#     except requests.exceptions.RequestException as e:
#         st.error(f"Request failed: {e}")

# # URL Validation
# def is_valid_url(url):
#     pattern = r'^(https?://)?([a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+)(:[0-9]+)?(/.*)?$'
#     return re.match(pattern, url) is not None

# # Main screen content based on sidebar selection
# if option == "Web-Site":
#     st.sidebar.subheader("Choose the Extraction Tool for Web-Site")
#     tool_option = st.sidebar.selectbox("Which tool would you prefer?", ["Open-Source", "Enterprise"])

#     url = st.sidebar.text_input("Enter URL here:")
#     if st.sidebar.button("Extract Content"):
#         if url:
#             if is_valid_url(url):
#                 fetch_scraped_content(url, tool_option)
#             else:
#                 st.error("Invalid URL! Please enter a valid URL starting with 'http://' or 'https://'.")
#         else:
#             st.error("Please enter a URL.")

# elif option == "Pdf":
#     st.sidebar.subheader("Upload a PDF File")
#     uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
    
#     if st.sidebar.button("Extract PDF Content"):
#         if uploaded_file:
#             fetch_pdf_content(uploaded_file)
#         else:
#             st.error("Please upload a PDF file.")

# import streamlit as st
# import re
# import requests
# import boto3
# import os
# from datetime import datetime
# from dotenv import load_dotenv
# import json

# # Load environment variables
# load_dotenv()

# # Initialize S3 client
# s3_client = boto3.client(
#     "s3",
#     aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#     aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
#     region_name=os.getenv("AWS_REGION")
# )
# AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

# # Add a title to the app
# st.title("Content Extraction Tool")

# # Sidebar for selecting where to extract content from
# st.sidebar.header("Select the Content Extraction Source")
# option = st.sidebar.selectbox("Where do you want to extract content from?", ["Web-Site", "Pdf"])

# # URL Validation
# def is_valid_url(url):
#     pattern = r'^(https?://)?([a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+)(:[0-9]+)?(/.*)?$'
#     return re.match(pattern, url) is not None

# # def display_content(data, tool_option):
# #     """Display the extracted content in a structured way"""
# #     # Title
# #     if 'title' in data:
# #         st.title(data['title'])
    
# #     # Content/Text
# #     st.header("📄 Content")
# #     if tool_option == "Open-Source":
# #         if 'paragraphs' in data:
# #             for paragraph in data['paragraphs']:
# #                 st.write(paragraph)
# #                 st.markdown("---")
# #     else:  # Enterprise
# #         if 'text' in data:
# #             paragraphs = data['text'].split('\n')
# #             for paragraph in paragraphs:
# #                 if paragraph.strip():
# #                     st.write(paragraph)
# #                     st.markdown("---")
    
# #     # Links
# #     if 'links' in data:
# #         st.header("🔗 Important Links")
# #         col1, col2 = st.columns(2)
# #         for idx, link in enumerate(data['links']):
# #             with col1 if idx % 2 == 0 else col2:
# #                 st.markdown(f"- [{link['text']}]({link['url']})")
    
# #     # Images
# #     if 'images' in data:
# #         st.header("🖼️ Images")
# #         cols = st.columns(2)
# #         for idx, img in enumerate(data['images']):
# #             try:
# #                 with cols[idx % 2]:
# #                     st.image(
# #                         img['src'],
# #                         caption=img.get('alt', img.get('title', '')),
# #                         use_container_width=True
# #                     )
# #             except Exception as e:
# #                 st.error(f"Could not load image: {img['src']}")

# # def fetch_scraped_content(url, tool_option):
# #     """Fetch and display content from the API"""
# #     endpoint = "http://127.0.0.1:8000/scrape-open-source/" if tool_option == "Open-Source" else "http://127.0.0.1:8000/scrape_article-enterprise/"
    
# #     try:
# #         with st.spinner('Extracting content...'):
# #             response = requests.post(
# #                 endpoint,
# #                 json={"url": url},
# #                 headers={"Content-Type": "application/json"}
# #             )
            
# #             if response.status_code == 200:
# #                 st.success("Content extracted successfully!")
# #                 data = response.json()
# #                 display_content(data, tool_option)
                
# #                 # Add download button for JSON content
# #                 st.download_button(
# #                     label="Download Extracted Content (JSON)",
# #                     data=response.text,
# #                     file_name=f"extracted_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
# #                     mime="application/json"
# #                 )
# #             else:
# #                 st.error(f"Error: {response.text}")
    
# #     except requests.exceptions.RequestException as e:
# #         st.error(f"Request failed: {e}")
# #     except Exception as e:
# #         st.error(f"Error: {str(e)}")

# def display_content(data, tool_option):
#     """Display the extracted content in a structured way"""
#     # Title
#     if 'title' in data:
#         st.title(data['title'])
    
#     # Content/Text
#     st.header("📄 Content")
#     if 'paragraphs' in data:
#         for paragraph in data['paragraphs']:
#             if paragraph.strip():  # Only display non-empty paragraphs
#                 st.write(paragraph)
#                 st.markdown("---")
    
#     # Links
#     if 'links' in data and data['links']:
#         st.header("🔗 Important Links")
#         col1, col2 = st.columns(2)
#         for idx, link in enumerate(data['links']):
#             with col1 if idx % 2 == 0 else col2:
#                 if 'text' in link and 'url' in link:
#                     st.markdown(f"- [{link['text']}]({link['url']})")
    
#     # Images
#     if 'images' in data and data['images']:
#         st.header("🖼️ Images")
#         cols = st.columns(2)
#         for idx, img in enumerate(data['images']):
#             try:
#                 with cols[idx % 2]:
#                     caption = img.get('caption', '') or img.get('alt', '')
#                     st.image(
#                         img['src'],
#                         caption=caption,
#                         use_container_width=True
#                     )
#             except Exception as e:
#                 st.error(f"Could not load image: {str(e)}")
#                 print(f"Image loading error: {str(e)}")
#                 print(f"Image data: {img}")

# def fetch_scraped_content(url, tool_option):
#     """Fetch and display content from the API"""
#     endpoint = "http://127.0.0.1:8000/scrape-open-source/" if tool_option == "Open-Source" else "http://127.0.0.1:8000/scrape_article-enterprise/"
    
#     try:
#         with st.spinner('Extracting content...'):
#             response = requests.post(
#                 endpoint,
#                 json={"url": url},
#                 headers={"Content-Type": "application/json"}
#             )
            
#             if response.status_code == 200:
#                 st.success("Content extracted successfully!")
#                 data = response.json()
                
#                 # Debug information
#                 st.write(f"Number of images found: {len(data.get('images', []))}")
                
#                 display_content(data, tool_option)
                
#                 # Add download button for JSON content
#                 st.download_button(
#                     label="Download Extracted Content (JSON)",
#                     data=json.dumps(data, indent=2),
#                     file_name=f"extracted_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
#                     mime="application/json"
#                 )
#             else:
#                 st.error(f"Error: {response.text}")
#                 print(f"API Error Response: {response.text}")
    
#     except requests.exceptions.RequestException as e:
#         st.error(f"Request failed: {e}")
#         print(f"Request Exception: {str(e)}")
#     except Exception as e:
#         st.error(f"Error: {str(e)}")
#         print(f"General Exception: {str(e)}")

# def fetch_pdf_content(uploaded_file):
#     """Process uploaded PDF file"""
#     endpoint = "http://127.0.0.1:8000/process-pdf/"
    
#     try:
#         with st.spinner('Processing PDF...'):
#             files = {"file": uploaded_file.getvalue()}
#             response = requests.post(endpoint, files=files)
            
#             if response.status_code == 200:
#                 st.success("PDF processed successfully!")
#                 data = response.json()
                
#                 # Display extracted content
#                 if 'paragraphs' in data:
#                     st.header("📄 Extracted Text")
#                     for paragraph in data['paragraphs']:
#                         st.write(paragraph)
#                         st.markdown("---")
                
#                 # Add download button
#                 st.download_button(
#                     label="Download Extracted Content",
#                     data=response.text,
#                     file_name=f"pdf_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
#                     mime="application/json"
#                 )
#             else:
#                 st.error(f"Error: {response.text}")
    
#     except requests.exceptions.RequestException as e:
#         st.error(f"Request failed: {e}")
#     except Exception as e:
#         st.error(f"Error: {str(e)}")

# # Main screen content based on sidebar selection
# if option == "Web-Site":
#     st.sidebar.subheader("Choose the Extraction Tool for Web-Site")
#     tool_option = st.sidebar.selectbox("Which tool would you prefer?", ["Open-Source", "Enterprise"])

#     url = st.sidebar.text_input("Enter URL here:")
#     if st.sidebar.button("Extract Content"):
#         if url:
#             if is_valid_url(url):
#                 fetch_scraped_content(url, tool_option)
#             else:
#                 st.error("Invalid URL! Please enter a valid URL starting with 'http://' or 'https://'.")
#         else:
#             st.error("Please enter a URL.")

# elif option == "Pdf":
#     st.sidebar.subheader("Upload a PDF File")
#     uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
    
#     if st.sidebar.button("Extract PDF Content"):
#         if uploaded_file:
#             fetch_pdf_content(uploaded_file)
#         else:
#             st.error("Please upload a PDF file.")

import streamlit as st
import re
import requests
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

# Add a title to the app
st.title("Content Extraction Tool")

# Sidebar for selecting where to extract content from
st.sidebar.header("Select the Content Extraction Source")
option = st.sidebar.selectbox("Where do you want to extract content from?", ["Web-Site", "Pdf"])

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