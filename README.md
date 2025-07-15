# News Article Summarizer

The **News Article Summarizer** is a modern web application designed to simplify news consumption by allowing users to input a news article URL, scrape its content, and generate a concise, AI-powered summary. Built with a **React JS** frontend, a **FastAPI** backend, and integrated with **Grok's API** (powered by xAI), this project combines data scraping techniques with a responsive, user-friendly interface. It stores summaries in a MongoDB database, supports PDF downloads with professional formatting, and includes robust error handling for a seamless user experience.

> **Note:** This project is an experimental proof of concept to demonstrate the integration of web scraping, AI summarization, and modern web technologies. It is functional but may not adhere to all production-grade standards. Contributions to enhance its functionality are welcome!

## Features

- **Article Content Extraction**: Utilizes web scraping techniques to extract text and images from provided news article URLs.
- **AI-Powered Summarization**: Leverages Grok's API to generate concise, structured summaries with headings, bullet points, and paragraphs.
- **Responsive UI**: A clean, intuitive interface built with React JS and styled with Tailwind CSS, optimized for desktop and mobile devices.
- **PDF Download**: Download article summaries as professionally formatted PDFs, including the original URL, image (if available), and summary, with consistent margins, headers, footers, and a "News Summarizer" watermark.
- **Duplicate URL Handling**: Automatically deletes the previous article from the database if the same URL is submitted again, ensuring only the latest summary is stored after a successful response.
- **Robust Error Handling**: Displays user-friendly error messages (e.g., for invalid URLs, failed scraping, or API errors) in an absolute-positioned alert at the top of the page, with auto-dismiss after 5 seconds or manual dismissal via a close button.
- **MongoDB Storage**: Persists article summaries in a MongoDB database for efficient retrieval and management.
- **Interactive Article Management**: Features buttons to open the original article, download the summary as a PDF, or delete the article from the database.

## Prerequisites

To run this project, ensure you have the following installed:

- **React.js** for the frontend
- **Python** (v3.8 or higher) for the backend
- **MongoDB** (local or cloud instance, e.g., MongoDB Atlas)
- **npm** for managing frontend dependencies
- **pip** for managing Python dependencies

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/news-article-summarizer.git
cd news-article-summarizer
```

### 2. Configure Environment Variables
Create a `.env` file in the `news-summarizer` directory with the following keys:

```plaintext
GROK_API_KEY=gsk_<your_grok_api_key>
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
```

- **GROK_API_KEY**: Obtain from Groq cloud for accessing the Groq API.
- **MONGODB_URI**: Your MongoDB connection string. For MongoDB Atlas, replace `<username>`, `<password>`, `<cluster>`, and `<database>` with your credentials and database name.

### 3. Backend Setup
Navigate to the news-summarizer directory:

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`.

### 4. Frontend Setup
Navigate to the frontend directory:
```bash
cd frontend
```

Install JavaScript dependencies:
```bash
npm install
```

Ensure the following libraries are installed for PDF generation:
```bash
npm install jspdf html2canvas
```

Start the React development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:5173`.

## Usage

1. Open the application in your browser at `http://localhost:5173`.
2. In the fixed input bar at the bottom, enter a valid news article URL and click **Summarize**.
3. The application will:
   - Scrape the article content using data scraping techniques.
   - Generate a summary via Grok's API.
   - Display the summary with an optional image in a responsive card.
4. For each article card, you can:
   - **Open**: Click the link icon to view the original article in a new tab.
   - **Download**: Click the download icon to save the summary as a PDF, including the URL, image (if available), and formatted summary with headers, footers, and a watermark.
   - **Delete**: Click the trash icon to remove the article from the database.
5. If you submit the same URL again, the previous article is deleted from the database after a successful new summary is generated.
6. Errors (e.g., invalid URL, failed scraping, or API issues) appear as alerts at the top of the page, auto-dismissing after 5 seconds or manually dismissible via a close button.

## Project Structure

```
news-article-summarizer/
├
├── main.py                 # FastAPI entry point and API routes
├── db.py                   # MongoDB connection and database logic
├── news.py                 # Web scraping and Grok API integration
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables

├── frontend/                   # React frontend
│   ├── src/                    # React source files
│   │   ├── ArticleSummaryPage.jsx  # Main component with UI and PDF generation
│   │   └── ...                 # Other React components and utilities
│   ├── public/                 # Static assets (e.g., favicon)
│   ├── package.json            # Frontend dependencies
│   └── ...                     # Other frontend configuration files
└── README.md                   # Project documentation
```

## Technical Details

### Backend
- **Framework**: FastAPI, a high-performance Python web framework.
- **Data Scraping**: Uses libraries (e.g., `requests`, `beautifulsoup4`) to extract article text and images from URLs.
- **Summarization**: Integrates with Grok's API for AI-powered summarization, formatting output with headings, bullet points, and paragraphs.
- **Database**: MongoDB stores article data (URL, summary, image URL) with robust error handling for database operations.
- **Duplicate Handling**: If a URL is resubmitted, the backend deletes the existing article after successfully generating a new summary.
- **Error Handling**: Comprehensive error handling for network issues, invalid URLs, and API failures, returning clear HTTP error responses.

### Frontend
- **Framework**: React JS with functional components and hooks.
- **Styling**: Tailwind CSS for a modern, responsive design, ensuring compatibility across devices.
- **PDF Generation**: Uses `jsPDF` and `html2canvas` to create professionally formatted PDFs with:
  - 1-inch margins on all sides.
  - Header with "Article Summary" title and date.
  - Footer with page numbers and "Generated by News Summarizer".
  - Diagonal "News Summarizer" watermark in light gray.
  - Times New Roman font (16pt for headings, 12pt for body text).
- **UI Features**:
  - Responsive article cards with images, summaries, and action buttons (open, download, delete).
  - Fixed input bar with smooth expand/collapse animation.
  - Absolute-positioned alerts for errors and success messages, auto-dismissing after 5 seconds.
- **Error Handling**: Displays user-friendly error messages for failed API calls, scraping issues, or PDF generation failures.

## Environment Variables
The following environment variables must be set in the `/.env` file:
- **GROK_API_KEY**: Your xAI Grok API key for summarization (e.g., `gsk_xxxxxxxxxxxxxxxx`).
- **MONGODB_URI**: MongoDB connection string (e.g., `mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/<db>`).

Failure to set these variables will prevent the backend from connecting to the database or Grok API, resulting in errors.

## Known Limitations
- **Scraping Restrictions**: Some websites may block scraping due to robots.txt or anti-scraping measures, leading to failed content extraction.
- **Image Loading**: PDF image inclusion may fail if the image URL has CORS restrictions; a fallback message ("Image not available") is displayed.
- **API Dependency**: Summarization relies on Grok's API availability and rate limits.
- **Code Maturity**: As a proof of concept, the code prioritizes functionality over exhaustive edge-case handling or production-grade optimizations.

## Future Improvements
- **Enhanced Scraping**: Implement fallback scraping methods or proxy servers to handle restricted websites.
- **Caching**: Store frequently accessed articles in a cache to reduce API calls and improve performance.
- **UI Enhancements**: Add dark mode, pagination for article lists, and advanced animations.
- **Multilingual Support**: Extend summarization to support multiple languages via Grok's API.
- **Authentication**: Add user authentication to manage personalized article collections.

## Contributing
We welcome contributions to improve the News Article Summarizer! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request with a detailed description of your changes.

Please ensure your code follows the existing style and includes tests where applicable.

## License
This project is licensed under the MIT License. You are free to use, modify, and distribute this software, provided proper credit is given. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- [React JS](https://react.dev/) for the frontend framework.
- [FastAPI](https://fastapi.tiangolo.com/) for the backend API.
- [Grok API](https://console.groq.com/) by xAI for AI-powered summarization.
- [MongoDB](https://www.mongodb.com/) for data storage.
- [Tailwind CSS](https://tailwindcss.com/) for responsive styling.
- [jsPDF](https://github.com/parallax/jsPDF) and [html2canvas](https://html2canvas.hertzen.com/) for PDF generation.

## Contact
For questions, suggestions, or issues, please open an issue on the GitHub repository or contact the maintainers.

---

Enjoy summarizing news articles with ease and professionalism! 🎉
