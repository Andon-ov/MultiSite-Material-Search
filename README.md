# 🛠️ MultiSite Material Search

**MultiSite Material Search** is a Django-based web application that allows users to search and aggregate building materials from multiple Bulgarian online stores. It uses `requests` and `BeautifulSoup` to scrape product data directly from websites, without relying on Scrapy.

---

## 🚀 Features

- 🔍 Search for products across multiple stores:
  - Praktiker
  - Masterhaus
  - Mr. Bricolage
  - ABC Stroitelni Materiali
  - Toplivo.bg
- ⚡ Parallel scraping using `ThreadPoolExecutor`
- 🧠 Smart filtering by keyword match
- 📊 Sorting by price or title
- 🖼️ Display of product images, prices, and direct links

---

## 📦 Installation

### 1. Clone the repository

    git clone https://github.com/Andon-ov/MultiSite-Material-Search.git
    cd MultiSite-Material-Search 
    

### 2. Create a virtual environment
#### On Linux/macOS:
  
    python3 -m venv venv
    source venv/bin/activate

#### On Windows:

    python -m venv venv
    .\venv\Scripts\activate
   
### 3. Install dependencies

    pip install -r requirements.txt

### 4. Run migrations and start the server

    python manage.py migrate
    python manage.py runserver

### 5. 🖥️ Usage
Once the server is running, open your browser and go to: 
        http://127.0.0.1:8000/
        
Enter a search query and choose your preferred sorting method. The app will fetch and display results from all supported stores.

### 6. 📁 Project Structure

    ├── manage.py
    ├── material_search/         # Django project settings
    ├── search_app/              # Core search application
    │   ├── views.py             # Scraping and rendering logic
    │   ├── forms.py             # Search form
    │   ├── templates/           # HTML templates
    │   └── urls.py              # URL routing
    ├── requirements.txt         # Python dependencies
    └── README.md

### 7. 🧠 Future Improvements

- Add caching for faster repeated searches
- Mobile-friendly UI
- Cloud deployment (e.g. Render, Railway)
- Fallback logic for blocked requests

### 8. 📜 License


This project is licensed under the [MIT License.](https://en.wikipedia.org/wiki/MIT_License)

### 9. 🤝 Author 
Built with ❤️ by Andon-ov