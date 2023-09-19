from flask import Flask, render_template, request, flash
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to a secure secret key

# Define a user agent to simulate a web browser
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

def extract_all_urls_from_sitemap(sitemap_url):
    url_list = []

    def extract_recursive(sitemap_url):
        try:
            # Send an HTTP GET request with the user agent
            headers = {"User-Agent": user_agent}
            response = requests.get(sitemap_url, headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the XML content of the sitemap
                soup = BeautifulSoup(response.text, "xml")

                # Find all URL elements within the sitemap
                url_elements = soup.find_all("loc")

                # Extract and add the URLs to the list
                urls = [url.text for url in url_elements]
                url_list.extend(urls)

                # Look for sub-sitemap references (sitemapindex)
                sitemapindex_elements = soup.find_all("sitemap")
                for sitemapindex_element in sitemapindex_elements:
                    sub_sitemap_url = sitemapindex_element.find("loc").text
                    extract_recursive(sub_sitemap_url)
        except requests.exceptions.RequestException as e:
            pass

    extract_recursive(sitemap_url)
    return url_list

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        domain = request.form.get("domain")
        if domain:
            # Ensure the domain is properly formatted
            if not domain.startswith("http://") and not domain.startswith("https://"):
                domain = "https://" + domain  # Add HTTPS if missing

            sitemap_url = urljoin(domain, "sitemap.xml")
            url_list = extract_all_urls_from_sitemap(sitemap_url)

            if url_list:
                total_urls = len(url_list)
                return render_template("index.html", url_list=url_list, total_urls=total_urls)
            else:
                flash("Failed to retrieve the sitemap or extract URLs.", "error")
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)