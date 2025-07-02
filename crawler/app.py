from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def crawl_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        page_content = soup.body.get_text(separator='', strip=True)
        
        return {"status": "success", "content": page_content, "error": None}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "links": [], "error": str(e)}

@app.route('/', methods=['GET', 'POST'])
def index():
    crawled_info = None
    if request.method == 'POST':
        url = request.form['url']
        if url:
            crawled_info = crawl_website(url)
    return render_template('index.html', crawled_info=crawled_info)

if __name__ == '__main__':
    app.run(debug=True)
