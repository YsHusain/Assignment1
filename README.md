Links 
Codelab - https://codelabs-preview.appspot.com/?file_id=1CPjFm63rJsZsrSeXeq6pHaGFEsUKeNBOc3eRcgieRF0#6

Streamlit(frontend) - https://assignment1-wz7bsajwe44wdpsvhxhxfk.streamlit.app/
Github- https://github.com/YsHusain/Assignment1

Video - https://northeastern-my.sharepoint.com/personal/shajapurwalayusuf_h_northeastern_edu/_layouts/15/stream.aspx?id=%2Fpersonal%2Fshajapurwalayusuf%5Fh%5Fnortheastern%5Fedu%2FDocuments%2FRecordings%2FCall%20with%20Dhrumil%20and%201%20other%2D20250131%5F154125%2DMeeting%20Recording%2Emp4&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2E51bfd7ea%2Da93a%2D4b04%2Da8b3%2Dfd2c12175adc 

Fast Api https://team-assignment-three.vercel.app/


Assignment 1 - Content Extractor Tool
Husain
Dhrumil Patel
Sahil Kasliwal

Introduction

This project aims to create a Content Extractor Tool that simplifies the process of extracting text, images, and tables from PDF files and webpages. It provides a streamlined solution for organizing and standardizing extracted data into Markdown format and storing it in an S3 bucket for easy retrieval. The project also includes a client-facing application with a user-friendly interface to query and interact with the processed data.

Technologies Involved:
PyPDF2, BeautifulSoup: Open-source tools for extracting content from PDFs and webpages respectively.
Adobe Acrobat and Diffbot: Enterprise tools for content extraction from pdf and webpage respectively.
Docling Tool for standardizing extracted content into Markdown format.
AWS S3: For structured storage of extracted files with metadata.
FastAPI: Backend API development for processing and storing data.
Streamlit: Frontend interface for user interaction with the tool.

 


Problem Statement
Problem Statement
Organizations often face challenges in handling unstructured data from sources like PDF files and webpages. Extracting meaningful information, standardizing it into usable formats, and storing it efficiently is critical for downstream processes such as analysis or AI model training.


Challenges Addressed:
Extracting complex data (text, images, tables) from diverse sources 
Standardizing extracted content into Markdown format while preserving structure.
Organizing files in an S3 bucket with proper metadata for efficient storage and retrieval.
Desired Outcome:
A prototype application that evaluates the feasibility of open-source tools versus enterprise services and provides a structured pipeline to extract, process, standardize, and store unstructured data.

Constraints & Requirements:
Evaluate both open-source tools (e.g., PyPDF2, BeautifulSoup) and enterprise services (e.g.,adobe and Diffbot).
Ensure compatibility with Markdown conversion tools like Docling.
Implement secure storage practices in AWS S3.
Provide a frontend interface using streamlit.


Proof of Concept
Proof of Concept

Chosen Technologies & Rationale:
PyPDF2: Efficient for text extraction from PDFs; open-source and customizable.
BeautifulSoup Reliable for webpage scraping; widely used in the industry.
Adobe Acrobat and Diffbot Offers high accuracy and scalability for enterprise  scraping needs for pdf and webpage respectively.
Initial Setup & Tests:
Implemented basic PDF parsing using PyPDF2 to extract text elements successfully.
Conducted webpage scraping using BeautifulSoup to retrieve HTML content effectively.
Tested Adobe Acrobat for pdf extraction and  docling for Markdown conversion .
Tested Diffbot for website extraction  and used docking for markdown conversion.


Anticipated Challenges & Solutions:
Challenge: Handling large PDFs or complex webpage structures.
Solution: Optimize parsing functions with batch processing techniques.


Challenge: Integrating multiple tools into one pipeline.
Solution: Use modular architecture to ensure seamless integration.






Architecture Diagram

Data Flow and Interactions
User Interaction:
Users interact with Streamlit, triggering API calls to FastAPI.
FastAPI:
Processes API calls, queries the S3 Database, and requests text extraction from Web or Pdf.
Extracts content using Pypdf and PDF.co for pdf and for website uses beautifulsoup and diffbot .
 stores data in S3.
Storage and Deployment:
Code managed on GitHub, deployed using vercel /gcp to a Public Cloud Platform.
Interactions:
User >> Streamlit App >> FastAPI App >> S3 database
Source >> Text Extraction Tools >> S3 Storage
GitHub >> >> Public Cloud Platform




Walkthrough of the Application

Step-by-Step Instructions:
Open the Streamlit application hosted on the public cloud platform.
Upload a PDF file or provide a webpage URL.
Select the desired processing method: Open-source tools or Enterprise service.
View extracted content displayed in Markdown format on the interface.
Access processed files stored in AWS S3 via provided links.
Snapshots of UI Components:
Upload Section: Allows users to upload files or input URLs.
Results Section: Displays extracted text/images/tables in Markdown format.
Metadata Section: Shows file details and S3 storage location.

Application Workflow (Data Engineering Work + Code Explanation
Data Flow Overview:
Input is received via Streamlit frontend or API endpoint.
Backend processes input using extraction libraries/tools.
PDFs: PyPDF and Adobe Acrobat.
Webpages: BeautifulSoup and Diffbot.
Standardized output is generated using Docling.
Files are organized in AWS S3 bucket with metadata tags.
Backend Architecture:
FastAPI handles API endpoints for upload, processing, and retrieval tasks.
Database interactions store metadata about processed files.


