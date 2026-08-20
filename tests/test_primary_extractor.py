import pytest
from bs4 import BeautifulSoup
from pipeline.ondemand.primary_extractor import PrimaryExtractor

def test_parse_quotes():
    extractor = PrimaryExtractor()
    raw_html = """
    <html>
        <head><title>Quotes Page</title></head>
        <body>
            <div class="quote">
                <span class="text">“The world as we have created it is a process of our thinking.”</span>
                <small class="author">Albert Einstein</small>
            </div>
            <div class="quote">
                <span class="text">“It is our choices that show what we truly are, far more than our abilities.”</span>
                <small class="author">J.K. Rowling</small>
            </div>
        </body>
    </html>
    """
    articles = extractor._parse_html_to_articles(raw_html, "https://quotes.toscrape.com/")
    assert len(articles) == 2
    assert articles[0]["title"] == "Quote by Albert Einstein"
    assert "process of our thinking" in articles[0]["content"]
    assert articles[0]["author"] == "Albert Einstein"
    assert articles[1]["title"] == "Quote by J.K. Rowling"

def test_parse_books():
    extractor = PrimaryExtractor()
    raw_html = """
    <html>
        <head><title>All products | Books to Scrape</title></head>
        <body>
            <article class="product_pod">
                <div class="image_container">
                    <a href="catalogue/a-light-in-the-attic_1000/index.html">
                        <img src="media/cache/image1.jpg" alt="A Light in the Attic" class="thumbnail"/>
                    </a>
                </div>
                <p class="star-rating Three">
                    <i class="icon-star"></i>
                </p>
                <h3>
                    <a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a>
                </h3>
                <div class="product_price">
                    <p class="price_color">£51.77</p>
                    <p class="instock availability">In stock</p>
                </div>
            </article>
        </body>
    </html>
    """
    articles = extractor._parse_html_to_articles(raw_html, "https://books.toscrape.com/")
    assert len(articles) == 1
    content = articles[0]["content"]
    assert "A Light in the Attic" in content
    assert "**Price**: £51.77" in content
    assert "**Availability**: In stock" in content
    assert "**Rating**: Three out of 5 stars" in content
    assert "**Thumbnail**: media/cache/image1.jpg" in content
    assert "**Detail Page**: catalogue/a-light-in-the-attic_1000/index.html" in content
    assert articles[0]["title"] == "All products | Books to Scrape"
    assert articles[0]["author"] == "Bright Data Scraper Studio"

def test_parse_general_fallback():
    extractor = PrimaryExtractor()
    raw_html = """
    <html>
        <head><title>Some Random Page</title></head>
        <body>
            <main>
                <h1>An interesting article</h1>
                <p>This is a general fallback parsing test. It has enough content to satisfy the trafilatura length requirement of fifty characters.</p>
            </main>
        </body>
    </html>
    """
    articles = extractor._parse_html_to_articles(raw_html, "https://example.com/article")
    assert len(articles) == 1
    assert "general fallback parsing test" in articles[0]["content"]
    assert articles[0]["title"] == "Some Random Page"
