# # import os
# # import requests
# # from bs4 import BeautifulSoup
# # from urllib.parse import urljoin
# # from docling.document_converter import DocumentConverter


# # # Function to save image from URL
# # def save_image(img_url, headers, image_folder, md_file):
# #     """Save an image from a URL to the specified folder and log in the markdown file."""
# #     try:
# #         img_response = requests.get(img_url, headers=headers)
# #         img_response.raise_for_status()
# #         img_name = os.path.basename(img_url.split('?')[0]) or "image.jpg"
# #         img_path = os.path.join(image_folder, img_name)
# #         with open(img_path, 'wb') as f:
# #             f.write(img_response.content)
# #         md_file.write(f"![{img_name}]({img_path})\n")
# #     except requests.exceptions.RequestException as e:
# #         print(f"Error downloading image {img_url}: {e}")


# # # Function to scrape a website and extract content
# # def scrape_website(url, md_file):
# #     """Scrape the given website for text, hyperlinks, images, tables, and charts, saving to the markdown file."""
# #     try:
# #         headers = {'User-Agent': 'Mozilla/5.0'}
# #         response = requests.get(url, headers=headers)
# #         response.raise_for_status()

# #         soup = BeautifulSoup(response.text, 'html.parser')

# #         # Write webpage title to markdown
# #         page_title = soup.title.string if soup.title else "No title found"
# #         md_file.write(f"## Page Title\n\n{page_title}\n\n")

# #         # Hyperlinks
# #         md_file.write("## Hyperlinks on the page:\n\n")
# #         for link in soup.find_all('a', href=True):
# #             md_file.write(f"- [{link['href']}]({link['href']})\n")

# #         # Paragraphs
# #         md_file.write("\n## Paragraphs on the page:\n\n")
# #         for paragraph in soup.find_all('p'):
# #             md_file.write(f"{paragraph.text.strip()}\n\n")

# #         # Images
# #         md_file.write("\n## Images on the page:\n\n")
# #         image_folder = 'images_open_source'
# #         os.makedirs(image_folder, exist_ok=True)
# #         for img in soup.find_all('img'):
# #             img_url = img.get('src')
# #             if img_url:
# #                 full_img_url = urljoin(url, img_url)
# #                 save_image(full_img_url, headers, image_folder, md_file)

# #         # Tables
# #         md_file.write("\n## Tables on the page:\n\n")
# #         for table in soup.find_all('table'):
# #             rows = table.find_all('tr')
# #             for row in rows:
# #                 cells = row.find_all(['th', 'td'])
# #                 md_file.write("| " + " | ".join(cell.text.strip() for cell in cells) + " |\n")
# #             md_file.write("\n")

# #         # Charts (both image and SVG)
# #         md_file.write("\n## Charts on the page:\n\n")
# #         for chart in soup.find_all(['img', 'svg']):
# #             if chart.name == 'img':
# #                 chart_url = chart.get('src')
# #                 md_file.write(f"- Chart Image: ![Chart Image]({chart_url})\n")
# #             elif chart.name == 'svg':
# #                 md_file.write("- SVG Chart: Found inline SVG (content not displayed here).\n")

# #         print(f"Web scraping completed and saved to {md_file.name}")

# #     except requests.exceptions.RequestException as e:
# #         print("Error fetching the website:", e)


# # # Function to convert document to markdown using docling
# # def convert_document_to_markdown(url):
# #     """Convert a document to markdown using Docling and handle images if any."""
# #     try:
# #         converter = DocumentConverter()
# #         result = converter.convert(url)
        
# #         # Export the markdown content
# #         md_content = result.document.export_to_markdown()

# #         # Saving the markdown content to a file
# #         md_filename = "converted_document.md"
# #         with open(md_filename, "w", encoding="utf-8") as md_file:
# #             md_file.write(md_content)
# #             print(f"Document converted and saved to {md_filename}")
# #         return md_filename

# #     except Exception as e:
# #         print(f"Error converting document: {e}")
# #         return None


# # # Main function to handle both scraping and conversion
# # def scrape_and_convert(url, document_url=None):
# #     """Handle both scraping and document conversion."""
# #     md_filename = "scraped_and_converted_output.md"
# #     with open(md_filename, "w", encoding="utf-8") as md_file:
# #         # Web scraping section
# #         scrape_website(url, md_file)

# #         # Document conversion section (if URL for document is provided)
# #         if document_url:
# #             convert_document_to_markdown(document_url)
# #             # Here you could append the document content to the markdown file, or save separately
# #             md_file.write("\n## Converted Document Content:\n\n")
# #             with open("converted_document.md", "r", encoding="utf-8") as doc_file:
# #                 md_file.write(doc_file.read())

# #     print(f"Scraped and converted content saved to {md_filename}")


# # # Example: Use the function to scrape a webpage and convert a document
# # scrape_and_convert("https://www.northeastern.edu", "https://arxiv.org/pdf/2408.09869")

# import os
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# from docling.document_converter import DocumentConverter


# # Function to save image from URL
# def save_image(img_url, headers, image_folder, md_file):
#     """Save an image from a URL to the specified folder and log in the markdown file."""
#     try:
#         img_response = requests.get(img_url, headers=headers)
#         img_response.raise_for_status()
#         img_name = os.path.basename(img_url.split('?')[0]) or "image.jpg"
#         img_path = os.path.join(image_folder, img_name)

#         # Save image locally
#         with open(img_path, 'wb') as f:
#             f.write(img_response.content)

#         # Write image reference to markdown (use relative path)
#         md_file.write(f"![{img_name}]({image_folder}/{img_name})\n")
#     except requests.exceptions.RequestException as e:
#         print(f"Error downloading image {img_url}: {e}")


# # Function to scrape a website and extract content
# def scrape_website(url, md_file):
#     """Scrape the given website for text, hyperlinks, images, tables, and charts, saving to the markdown file."""
#     try:
#         headers = {'User-Agent': 'Mozilla/5.0'}
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()

#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Write webpage title to markdown
#         page_title = soup.title.string if soup.title else "No title found"
#         md_file.write(f"## Page Title\n\n{page_title}\n\n")

#         # Hyperlinks
#         md_file.write("## Hyperlinks on the page:\n\n")
#         for link in soup.find_all('a', href=True):
#             md_file.write(f"- [{link['href']}]({link['href']})\n")

#         # Paragraphs
#         md_file.write("\n## Paragraphs on the page:\n\n")
#         for paragraph in soup.find_all('p'):
#             md_file.write(f"{paragraph.text.strip()}\n\n")

#         # Images
#         md_file.write("\n## Images on the page:\n\n")
#         image_folder = 'images_open_source'
#         os.makedirs(image_folder, exist_ok=True)
#         for img in soup.find_all('img'):
#             img_url = img.get('src')
#             if img_url:
#                 full_img_url = urljoin(url, img_url)
#                 save_image(full_img_url, headers, image_folder, md_file)

#         # Tables
#         md_file.write("\n## Tables on the page:\n\n")
#         for table in soup.find_all('table'):
#             rows = table.find_all('tr')
#             for row in rows:
#                 cells = row.find_all(['th', 'td'])
#                 md_file.write("| " + " | ".join(cell.text.strip() for cell in cells) + " |\n")
#             md_file.write("\n")

#         # Charts (both image and SVG)
#         md_file.write("\n## Charts on the page:\n\n")
#         for chart in soup.find_all(['img', 'svg']):
#             if chart.name == 'img':
#                 chart_url = chart.get('src')
#                 md_file.write(f"- Chart Image: ![Chart Image]({chart_url})\n")
#             elif chart.name == 'svg':
#                 md_file.write("- SVG Chart: Found inline SVG (content not displayed here).\n")

#         print(f"Web scraping completed and saved to {md_file.name}")

#     except requests.exceptions.RequestException as e:
#         print("Error fetching the website:", e)


# # Function to convert document to markdown using docling
# def convert_document_to_markdown(url):
#     """Convert a document to markdown using Docling and handle images if any."""
#     try:
#         converter = DocumentConverter()
#         result = converter.convert(url)
        
#         # Export the markdown content
#         md_content = result.document.export_to_markdown()

#         # Saving the markdown content to a file
#         md_filename = "converted_document.md"
#         with open(md_filename, "w", encoding="utf-8") as md_file:
#             md_file.write(md_content)
#             print(f"Document converted and saved to {md_filename}")
#         return md_filename

#     except Exception as e:
#         print(f"Error converting document: {e}")
#         return None


# # Main function to handle both scraping and conversion
# def scrape_and_convert(url, document_url=None):
#     """Handle both scraping and document conversion."""
#     md_filename = "scraped_and_converted_output.md"
#     with open(md_filename, "w", encoding="utf-8") as md_file:
#         # Web scraping section
#         scrape_website(url, md_file)

#         # Document conversion section (if URL for document is provided)
#         if document_url:
#             convert_document_to_markdown(document_url)
#             # Here you could append the document content to the markdown file, or save separately
#             md_file.write("\n## Converted Document Content:\n\n")
#             with open("converted_document.md", "r", encoding="utf-8") as doc_file:
#                 md_file.write(doc_file.read())

#     print(f"Scraped and converted content saved to {md_filename}")


# # Example: Use the function to scrape a webpage and convert a document
# scrape_and_convert("https://www.northeastern.edu", "https://arxiv.org/pdf/2408.09869")

import os
import requests
import ssl
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from docling.document_converter import DocumentConverter

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Function to save image from URL
def save_image(img_url, headers, image_folder, md_file):
    try:
        img_response = requests.get(img_url, headers=headers)
        img_response.raise_for_status()
        img_name = os.path.basename(img_url.split('?')[0]) or "image.jpg"
        img_path = os.path.join(image_folder, img_name)
        with open(img_path, 'wb') as f:
            f.write(img_response.content)
        md_file.write(f"![{img_name}]({image_folder}/{img_name})\n")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image {img_url}: {e}")

# Function to scrape a website and extract content
def scrape_website(url, md_file):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        page_title = soup.title.string if soup.title else "No title found"
        md_file.write(f"## Page Title\n\n{page_title}\n\n")

        md_file.write("## Hyperlinks on the page:\n\n")
        for link in soup.find_all('a', href=True):
            md_file.write(f"- [{link['href']}]({link['href']})\n")

        md_file.write("\n## Paragraphs on the page:\n\n")
        for paragraph in soup.find_all('p'):
            md_file.write(f"{paragraph.text.strip()}\n\n")

        md_file.write("\n## Images on the page:\n\n")
        image_folder = 'images_open_source'
        os.makedirs(image_folder, exist_ok=True)
        for img in soup.find_all('img'):
            img_url = img.get('src')
            if img_url:
                full_img_url = urljoin(url, img_url)
                save_image(full_img_url, headers, image_folder, md_file)

        md_file.write("\n## Tables on the page:\n\n")
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['th', 'td'])
                md_file.write("| " + " | ".join(cell.text.strip() for cell in cells) + " |\n")
            md_file.write("\n")

        md_file.write("\n## Charts on the page:\n\n")
        for chart in soup.find_all(['img', 'svg']):
            if chart.name == 'img':
                chart_url = chart.get('src')
                md_file.write(f"- Chart Image: ![Chart Image]({chart_url})\n")
            elif chart.name == 'svg':
                md_file.write("- SVG Chart: Found inline SVG (content not displayed here).\n")

        print(f"Web scraping completed and saved to {md_file.name}")

    except requests.exceptions.RequestException as e:
        print("Error fetching the website:", e)

# Function to convert document to markdown using docling
def convert_document_to_markdown(url):
    try:
        converter = DocumentConverter()
        result = converter.convert(url)
        
        md_content = result.document.export_to_markdown()

        md_filename = "converted_document.md"
        with open(md_filename, "w", encoding="utf-8") as md_file:
            md_file.write(md_content)
            print(f"Document converted and saved to {md_filename}")
        return md_filename

    except Exception as e:
        print(f"Error converting document: {e}")
        return None

# Main function to handle both scraping and conversion
def scrape_and_convert(url, document_url=None):
    md_filename = "scraped_and_converted_output.md"
    with open(md_filename, "w", encoding="utf-8") as md_file:
        scrape_website(url, md_file)

        if document_url:
            converted_md_file = convert_document_to_markdown(document_url)
            if converted_md_file and os.path.exists(converted_md_file):
                with open(converted_md_file, "r", encoding="utf-8") as doc_file:
                    md_file.write("\n## Converted Document Content:\n\n")
                    md_file.write(doc_file.read())
            else:
                print("Converted document not found, skipping append step.")

    print(f"Scraped and converted content saved to {md_filename}")

# Example: Use the function to scrape a webpage and convert a document
scrape_and_convert("https://www.northeastern.edu", "https://arxiv.org/pdf/2408.09869")
