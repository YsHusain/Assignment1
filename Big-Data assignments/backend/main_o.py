from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = FastAPI()

# Predefined URL to scrape
PREDEFINED_URL = "https://www.northeastern.edu/"

# Define the file generation and scraping function
def save_image(img_url, headers, image_folder, md_file):
    """Save an image from a URL to the specified folder and log in the markdown file."""
    try:
        img_response = requests.get(img_url, headers=headers)
        img_response.raise_for_status()
        img_name = os.path.basename(img_url.split('?')[0]) or "image.jpg"
        img_path = os.path.join(image_folder, img_name)
        with open(img_path, 'wb') as f:
            f.write(img_response.content)
        md_file.write(f"![{img_name}]({img_path})\n")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image {img_url}: {e}")

def scrape_website(url):
    """Scrape the given website for text, hyperlinks, images, tables, and charts, saving to a markdown file."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        md_filename = "scraped_output.md"
        with open(md_filename, "w", encoding="utf-8") as md_file:
            md_file.write(f"# Scraped Data from {url}\n\n")
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

            md_file.write("\nScraping completed!\n")
        return md_filename

    except requests.exceptions.RequestException as e:
        print("Error fetching the website:", e)
        return None

# Endpoint to scrape the predefined website, generate the file, and return the file for download
@app.post("/scrape/")
async def scrape_and_download():
    """Scrape the predefined website, generate the file, and return the file."""
    file_name = scrape_website(PREDEFINED_URL)
    if file_name:
        file_path = os.path.join(os.getcwd(), file_name)
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    else:
        raise HTTPException(status_code=400, detail="Error scraping the website.")
