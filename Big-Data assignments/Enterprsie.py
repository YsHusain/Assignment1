import requests
import os
import json
from dotenv import load_dotenv

# API configuration
API_TOKEN = os.getenv('DIFFBOT_API_TOKEN')
URL_TO_SCRAPE = 'https://books.toscrape.com/'
API_ENDPOINT = f'https://api.diffbot.com/v3/article'

def scrape_and_save_article():
    params = {
        'token': API_TOKEN,
        'url': URL_TO_SCRAPE
    }
    
    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('objects'):
            raise ValueError("No article content found")
            
        article = data['objects'][0]
        
        # Create structured data for JSON
        article_data = {
            'title': 'Article from Northeastern University',
            'content': article.get('text', ''),
            'images': []
        }
        
        # Handle images
        image_dir = "downloaded_images_enterprise"
        os.makedirs(image_dir, exist_ok=True)
        
        for idx, image in enumerate(article.get('images', []), 1):
            image_url = image.get('url')
            if not image_url:
                continue
                
            try:
                img_response = requests.get(image_url, stream=True)
                img_response.raise_for_status()
                
                extension = image_url.split('.')[-1].split('?')[0]
                filename = f"image_{idx}.{extension}"
                filepath = os.path.join(image_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                # Add image info to JSON data
                article_data['images'].append({
                    'id': idx,
                    'url': image_url,
                    'local_path': filepath
                })
                
            except requests.RequestException as e:
                print(f"Failed to download image {idx}: {e}")
        
        # Save as JSON file
        with open('article_data.json', 'w', encoding='utf-8') as f:
            json.dump(article_data, f, indent=4)
            
        print("Article successfully scraped and saved as JSON")
        
    except requests.RequestException as e:
        print(f"API request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def convert_json_to_markdown(json_file_path):
    try:
        # Load JSON data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
        
        # Create markdown content
        markdown_content = f"# {article_data['title']}\n\n"
        markdown_content += f"## Content\n\n{article_data['content']}\n\n"
        markdown_content += "## Images\n\n"
        
        # Add images
        for image in article_data['images']:
            markdown_content += f"![Image {image['id']}]({image['local_path']})\n"
        
        # Save markdown content to a file
        with open("converted_article.md", "w", encoding='utf-8') as f:
            f.write(markdown_content)
        
        print("Markdown content saved to 'converted_article.md'")
        
    except FileNotFoundError:
        print("JSON file not found")
    except json.JSONDecodeError:
        print("Invalid JSON format")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # First, scrape and save the article
    scrape_and_save_article()
    
    # Then, convert the saved JSON to markdown
    convert_json_to_markdown('article_data.json')


