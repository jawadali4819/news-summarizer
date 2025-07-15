import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import logging
from urllib.parse import urlparse
from groq import Groq
from typing import Dict, Optional, List




class NewsSummarizer:
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        """Initialize the NewsSummarizer with Groq API key and model."""
        if not api_key:
            raise ValueError("API key is required.")
        
        self.client = Groq(api_key=api_key)
        self.model_name = model_name
        self.logger = self._setup_logger()
        # Configure default request settings
        self.request_timeout = 30  # Increased timeout to 30 seconds
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def _setup_logger(self) -> logging.Logger:
        """Set up and configure logging for the NewsSummarizer class."""
        # Create a logger specific to this class
        logger = logging.getLogger(__name__)
        
        # Only set up handler if none exists
        if not logger.handlers:
            # Create console handler
            handler = logging.StreamHandler()
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Add formatter to handler
            handler.setFormatter(formatter)
            
            # Add handler to logger
            logger.addHandler(handler)
            
            # Set level
            logger.setLevel(logging.INFO)
        
        return logger
    
    def validate_url(self, input_text: str) -> str:
        """
        Extract and validate a URL from input text.
        
        Args:
            input_text (str): Text containing a URL
        
        Returns:
            str: Validated URL
            
        Raises:
            ValueError: If URL is invalid or malformed
        """
        # First, check if input is already a valid URL
        try:
            result = urlparse(input_text)
            if all([result.scheme, result.netloc]):
                return input_text
        except Exception:
            pass

        # Try to extract URL using regex
        url_pattern = re.compile(
            r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
            re.IGNORECASE
        )
        
        match = url_pattern.search(input_text)
        if match:
            url = match.group(0)
            # Ensure URL starts with http or https
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Additional validation
            try:
                result = urlparse(url)
                if all([result.scheme, result.netloc]):
                    return url
            except Exception as e:
                self.logger.error(f"URL validation error: {e}")
                raise ValueError(f"Invalid URL structure: {url}")
            
            return url
            
        self.logger.error(f"No valid URL found in input: {input_text}")
        raise ValueError("Invalid input. Please provide a valid URL.")

    def extract_article_content(self, url: str, max_words: int = 2900) -> Dict[str, Optional[str]]:
        """Extract article content with improved error handling and retries."""
        from time import sleep
        
        for attempt in range(self.max_retries):
            try:
                # Validate URL
                url = self.validate_url(url)

                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    ),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Connection": "keep-alive",
                }

                # Create a session for better connection handling
                with requests.Session() as session:
                    session.headers.update(headers)
                    
                    # Configure retry strategy
                    retry_strategy = requests.adapters.Retry(
                        total=3,  # number of retries
                        backoff_factor=0.5,  # wait 0.5, 1, 2 seconds between retries
                        status_forcelist=[500, 502, 503, 504]  # retry on these status codes
                    )
                    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
                    session.mount("http://", adapter)
                    session.mount("https://", adapter)

                    # Fetch webpage with increased timeout
                    response = session.get(url, timeout=self.request_timeout)
                    response.raise_for_status()

                    # Rest of the content extraction logic remains the same
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Extract main image (enhanced)
                    image_tag = soup.find("meta", property="og:image")
                    main_image = urljoin(url, image_tag["content"]) if image_tag and "content" in image_tag.attrs else None
                    if not main_image:
                        first_img = soup.find("img")
                        main_image = urljoin(url, first_img["src"]) if first_img and "src" in first_img.attrs else None

                    # Content extraction with improved selectors
                    article_text = self._extract_content(soup)
                    
                    if not article_text:
                        if attempt < self.max_retries - 1:
                            self.logger.warning(f"No content found, retrying... (attempt {attempt + 1})")
                            sleep(self.retry_delay)
                            continue
                        else:
                            raise ValueError("No meaningful text could be extracted from the article.")

                    # Clean and limit text
                    clean_text = " ".join(article_text)
                    clean_text = re.sub(r"\s+", " ", clean_text).strip()
                    clean_text_words = clean_text.split()[:max_words]
                    clean_text = " ".join(clean_text_words)

                    return {"text": clean_text, "image": main_image, "link": url}

            except requests.Timeout:
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Timeout occurred, retrying... (attempt {attempt + 1})")
                    sleep(self.retry_delay)
                    continue
                else:
                    raise TimeoutError(f"Failed to fetch article after {self.max_retries} attempts: Connection timeout")
                    
            except requests.RequestException as e:
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Request failed, retrying... (attempt {attempt + 1})")
                    sleep(self.retry_delay)
                    continue
                else:
                    raise ConnectionError(f"Failed to fetch article after {self.max_retries} attempts: {str(e)}")

        return {"error": "Failed to extract article content after all retries"}

    def _extract_content(self, soup: BeautifulSoup) -> List[str]:
        """Helper method to extract content from BeautifulSoup object."""
        unwanted_keywords = ["advertisement", "sponsored", "copyright", "related", "disclaimer"]
        content_selectors = [
            'div.article-main',
            'article .article-body',
            'article .story-body',
            'div.article-body',
            'div.article-content',
            'div.content',
            'div.post-content',
            'main',
            'article',
            'div[role="main"]',
            '.article-text',
            '.story-content'
        ]

        article_text = []
        for selector in content_selectors:
            content_blocks = soup.select(selector)
            for content_block in content_blocks:
                paragraphs = content_block.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if (text and 
                        len(text.split()) > 5 and 
                        not any(kw in text.lower() for kw in unwanted_keywords)):
                        article_text.append(text)
                
                if article_text:
                    self.logger.info(f"Content found using selector: {selector}")
                    return article_text

        # Fallback to all paragraphs if no content found
        if not article_text:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if (text and 
                    len(text.split()) > 10 and 
                    not any(kw in text.lower() for kw in unwanted_keywords)):
                    article_text.append(text)

        return article_text













    def summarize_text(self, text: str, min_length: int = 400, max_length: int = 800) -> str:
        """
        Generate a summary of the given text using Groq.
        
        :param text: Input text to summarize
        :param min_length: Minimum summary length
        :param max_length: Maximum summary length
        :return: Generated summary
        """
        prompt = f"""
        You are an AI expert in summarization. Generate a structured and precise summary of the given text, adhering to these guidelines:

        1. **Content**: Cover key details—Who, What, When, Where, Why, and How. Include essential events, dates, and entities. Exclude irrelevant or redundant information.
        2. **Structure**: 
        - **Introduction**: Brief topic overview.
        - **Key Points**: Major events or findings.
        - **Implications**: Broader impacts.
        - **Conclusion**: Final wrap-up.
        3. **Tone**: Neutral, factual, and professional. Use any provided quotes, stats, or references accurately.
        4. **Length**: Keep summaries between 300–800 words for long texts or proportionally shorter for brief inputs.

        ### Input Text:
        {text}

        ### **Output Guidelines**  
        - Begin each section with a bolded heading.  
        - Use bullet points or numbered lists for concise details where appropriate.  
        - Ensure the summary is logically structured, easy to read, and complete.
        """


        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a news summarization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=(max_length * 2),  # Adjust based on input size
                top_p=1.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {e}"













    def remove_redundancies(self, text: str) -> str:
        """
        Remove redundant or unnecessary information from the text while preserving its core content.
        
        :param text: Input text to check for redundancies
        :return: Cleaned text with redundant information removed
        """
        try:
            prompt = f"""
            You are an expert in text deduplication. Review the given text and perform the following tasks:

            ### **Deduplication Guidelines**

            1. **Redundancy Removal:**
            - Identify and remove completely repeated sentences or paragraphs
            - Keep the most concise and informative version of repeated content

            2. **Content Preservation:**
            - Maintain the original text's core meaning and key information
            - Do NOT reduce the overall length of the text unnecessarily
            - Only remove text that adds no additional value

            3. **Formatting:**
            - Preserve the original structure (paragraphs, headings)
            - Ensure smooth flow and readability after removing redundancies

            4. **Special Instructions:**
            - If no significant redundancies are found, return the original text EXACTLY as provided
            - Do not artificially shorten the text
            - Maintain a neutral, factual, and professional tone
            - Output must be in English

            5. **Mandatory Structure:**
            - Always create the output with two sections:
              - **Headline**: Provide an impactful summary headline that shows the most important information in it (20 - 50 words).
              - **Body**: Organize detailed paragraphs logically, retaining key information from the original text.
              - You must include both sections in the output.

            ### **Input Text:**
            {text}
            """

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert in text deduplication and optimization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=len(text) * 2,  # Provide ample tokens to process the entire text
                top_p=1.0
            )
            
            deduplicated_text = response.choices[0].message.content.strip()
            
            # Ensure we don't return an empty text
            if not deduplicated_text:
                return text
            
            return deduplicated_text
        
        except Exception as e:
            self.logger.error(f"Error during deduplication: {e}")
            return text  # Return original text if deduplication fails











    def process_article(self, input_text: str) -> Dict[str, Optional[str]]:
        """
        Process the entire article workflow: extraction, summarization, and deduplication.
        
        :param input_text: URL or text of the article
        :return: Dictionary with extracted text, summary, and image
        """
        try:
            # Log the start of processing
            self.logger.info(f"Starting article processing for input: {input_text[:100]}...")
            
            
            extraction_result = self.extract_article_content(input_text)
            
            # Check for extraction errors
            if "error" in extraction_result:
                self.logger.error(f"Extraction error: {extraction_result['error']}")
                return extraction_result
            
            # Generate summary
            self.logger.info("Generating article summary...")
            summary = self.summarize_text(extraction_result["text"])
            
            
            result = {
                "summary": summary,
                "link": extraction_result.get("link"),
                "image": extraction_result.get("image"),
                
            }
            
            self.logger.info("Article processing completed successfully")
            return result
            
        except ValueError as ve:
            error_msg = f"Validation error: {str(ve)}"
            self.logger.error(error_msg)
            return {
                "error": error_msg, 
                "processing_status": "failed",
                "validation_method": "llm"
            }
            
        except Exception as e:
            error_msg = f"Unexpected error during article processing: {str(e)}"
            self.logger.error(error_msg)
            return {
                "error": error_msg,
                "processing_status": "failed",
                "error_type": type(e).__name__,
                "validation_method": "llm"
            }