
# News Article Summarizer

Welcome to the **News Article Summarizer**, a simple and creative tool that allows users to input the link of any news article, fetch its content through data mining, and generate a concise summary using Grok's API powered by the LLaMA model. This project demonstrates the synergy of **React JS**, **FastAPI**, and modern AI tools to streamline news consumption.

> **Note:** This is a small experimental project designed to showcase an idea. While functional, the code may not adhere to all professional standards. Feel free to build upon it, improve it, and make it your own!



## Features

- **Fetch Article Content:** Automatically extracts text from the provided news article URL.
- **AI-Powered Summarization:** Uses prompt engineering with Grok's API (LLaMA model) to summarize articles effectively.
- **React + FastAPI Integration:** The frontend is built in React JS, and the backend is powered by FastAPI for efficient processing.



## Getting Started

### Prerequisites

Ensure you have the following installed:

- **Node.js** (for frontend)
- **Python** (for backend)
- **MongoDB** (for data storage)



### Setup Instructions

#### Step 1: Clone the Repository
```bash
git clone <repository_url>
cd news-article-summarizer


#### Step 2: Configure Environment Variables

Create a `.env` file in the project root with the following keys:

```plaintext
GROK_API_KEY=<your_grok_api_key>
MONGODB_URI=<your_mongodb_connection_string>
```



#### Step 3: Backend Setup

Navigate to the backend folder:

```bash
cd backend
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend will be running on `http://localhost:8000`.

---

#### Step 4: Frontend Setup

Navigate to the frontend folder:

```bash
cd ../frontend
```

Install the dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will be running on `http://localhost:3000`.

---

## How to Use

1. Open the application in your browser at `http://localhost:3000`.
2. Enter the URL of a news article in the input field.
3. Click "Summarize."
4. The application will fetch the content from the article and display a concise summary.

---

## Project Structure

```
news-summarizer/
│
├               # Backend API (FastAPI)
│── main.py            # FastAPI entry point
│── db.py/             # API routes
│── news.py/           # Logic for data mining and Grok API integration
│── .env               # environment file
│
│
├── frontend/              # Frontend application (React JS)
│   ├── src/               # React source files
│   ├── public/            # Static assets
│
└── README.md              # Project documentation
```

---

## Technical Details

### Backend
- **Framework:** FastAPI
- **Data Storage:** MongoDB
- **Core Functionality:** Fetch article content via web scraping and summarize it using Grok's API.

### Frontend
- **Framework:** React JS
- **Styling:** Tailwind CSS
- **Core Functionality:** User-friendly input form and display of summarized results.

---

## Known Limitations

- **Code Quality:** This project is a proof of concept and may not follow best practices in every aspect.
- **Website Restrictions:** Some websites may block scraping due to content restrictions.
- **API Usage:** The summarization depends on the availability and proper setup of the Grok API.

---

## Future Improvements

- Add **error handling** for invalid URLs or failed API requests.
- Enhance the **user interface** with additional features like dark mode and animations.
- Implement **caching** to store results for frequently summarized articles.
- Extend support for multiple languages.

---

## Contributing

Contributions are welcome! If you have ideas to improve this project or want to fix issues, feel free to fork the repository and submit a pull request.

---

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software, provided proper credit is given.

---

## Acknowledgments

- [React JS](https://react.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LLaMA Model](https://ai.meta.com/llama/)
- [MongoDB](https://www.mongodb.com/)

---

Enjoy the creativity, and happy summarizing! 🎉
```
