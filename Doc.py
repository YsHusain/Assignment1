import requests
import json
import yaml
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
 
# Configure logging
logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)
 
def fetch_html(url, output_dir):
    """Fetch HTML content from a URL and save it to a file."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    }
 
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch {url}. HTTP status code: {response.status_code}")
 
    # Save raw HTML to a file
    raw_html_path = Path(output_dir) / "website.html"
    raw_html_path.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_html_path, "w", encoding="utf-8") as f:
        f.write(response.text)
 
    _log.info(f"HTML content fetched and saved to: {raw_html_path}")
    return raw_html_path, response.text  # Return raw HTML content for image extraction
 
def extract_images_from_html(html_content, output_dir, base_url):
    """Extract and download images from the HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")
    images_dir = Path(output_dir) / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
 
    image_counter = 0
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")
        if img_url:
            # Handle relative URLs
            if not img_url.startswith("http"):
                img_url = requests.compat.urljoin(base_url, img_url)
 
            try:
                # Download the image
                response = requests.get(img_url, stream=True)
                response.raise_for_status()
 
                # Save the image
                image_extension = Path(img_url).suffix or ".png"
                image_filename = images_dir / f"image_{image_counter}{image_extension}"
                with open(image_filename, "wb") as img_file:
                    img_file.write(response.content)
                image_counter += 1
 
                _log.info(f"Image saved: {image_filename}")
            except Exception as e:
                _log.warning(f"Failed to download image: {img_url}. Error: {e}")
 
    if image_counter == 0:
        _log.info("No images found in the HTML content.")
    else:
        _log.info(f"{image_counter} images downloaded.")
 
def process_html_with_docling(input_html_path, output_dir):
    """Process HTML content with Docling and save as Markdown, JSON, and YAML."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
 
    # Initialize DocumentConverter for HTML processing
    doc_converter = DocumentConverter(
        allowed_formats=[InputFormat.HTML]  # Restrict processing to HTML format
    )
 
    # Process the HTML file
    result = doc_converter.convert(input_html_path)
 
    if not result:
        _log.error("Failed to process the HTML file with Docling.")
        return
 
    # Save processed content in Markdown format
    markdown_path = output_dir / "website_content.md"
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(result.document.export_to_markdown())
    _log.info(f"Processed content saved as Markdown: {markdown_path}")
 
    # Save structured content in JSON format
    json_path = output_dir / "website_content.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result.document.export_to_dict(), f, indent=2)
    _log.info(f"Processed content saved as JSON: {json_path}")
 
    # Save structured content in YAML format
    yaml_path = output_dir / "website_content.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(result.document.export_to_dict(), f)
    _log.info(f"Processed content saved as YAML: {yaml_path}")
 
def main():
    # URL to fetch and process
    url = "https://graduate.northeastern.edu/"
    output_dir = "website_output"
 
    try:
        # Step 1: Fetch HTML content
        html_path, html_content = fetch_html(url, output_dir)
 
        # Step 2: Extract images from HTML
        extract_images_from_html(html_content, output_dir, url)
 
        # Step 3: Process HTML with Docling
        process_html_with_docling(html_path, output_dir)
 
        _log.info("HTML content successfully processed and saved.")
    except Exception as e:
        _log.error(f"An error occurred: {str(e)}")
 
if __name__ == "__main__":
    main()
 