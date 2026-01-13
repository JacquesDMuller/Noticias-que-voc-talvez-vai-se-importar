# -*- coding: utf-8 -*-
"""
News Crawler Engine
Adapted from Meridiano's utils.py - No AI dependencies
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import feedparser
import requests
import trafilatura
from bs4 import BeautifulSoup

from feeds_list import FEEDS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Constants
REQUEST_TIMEOUT = 15
MAX_ARTICLES_PER_FEED = 5
MAX_ARTICLES_PER_CATEGORY = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Blacklist keywords for sensitive content filtering
BLACKLIST_KEYWORDS = [
    # Morte - todas as formas
    "morte",
    "morto",
    "morta",
    "mortos",
    "mortas",
    "morre",      # conjugação: ele/ela morre
    "morrem",     # conjugação: eles/elas morrem
    "morreu",     # conjugação: ele/ela morreu
    "morreram",   # conjugação: eles/elas morreram
    "morrer",     # infinitivo
    # Violência e crimes
    "assassinato",
    "assassinatos",
    "assassinado",
    "assassinada",
    "homicídio",
    "homicidio",
    "sangue",
    "estupro",
    "estuprada",
    "estuprador",
    "corpo encontrado",
    "tiroteio",
    "baleado",
    "baleada",
    "esfaqueado",
    "esfaqueada",
    "facadas",
    "atropelado",
    "atropelada",
    "atropelamento",
    # Acidentes fatais
    "afogado",
    "afogada",
    "afogados",
    "afogamento",
    "incêndio",
    "incendio",
    # Tragédias
    "tragédia",
    "tragedia",
    "massacre",
    "chacina",
    "violência",
    "violencia",
    "suicídio",
    "suicidio",
]


def contains_blacklisted_content(title: str, summary: str) -> bool:
    """
    Check if the article title or summary contains blacklisted keywords.
    
    Args:
        title: Article title
        summary: Article summary/excerpt
        
    Returns:
        True if blacklisted content is found, False otherwise
    """
    text_to_check = f"{title} {summary}".lower()
    
    for keyword in BLACKLIST_KEYWORDS:
        if keyword.lower() in text_to_check:
            logger.info(f"  ⚠ Filtered out (blacklist): '{title[:50]}...'")
            return True
    
    return False


def fetch_feed(feed_url: str) -> list:
    """
    Parse an RSS feed and return list of entries.
    
    Args:
        feed_url: URL of the RSS feed
        
    Returns:
        List of feed entries with title, link, date, author
    """
    try:
        logger.info(f"Fetching feed: {feed_url}")
        feed = feedparser.parse(feed_url)
        
        if feed.bozo and not feed.entries:
            logger.warning(f"Feed parsing error: {feed_url} - {feed.bozo_exception}")
            return []
        
        entries = []
        for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
            # Parse publication date
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime(*entry.updated_parsed[:6]).isoformat()
            else:
                pub_date = datetime.now().isoformat()
            
            title = entry.get("title", "Sem título")
            summary = clean_html(entry.get("summary", ""))
            
            # Apply blacklist filter
            if contains_blacklisted_content(title, summary):
                continue
            
            entries.append({
                "title": title,
                "link": entry.get("link", ""),
                "date": pub_date,
                "author": entry.get("author", entry.get("dc_creator", "Redação")),
                "summary": summary,
            })
        
        return entries
        
    except Exception as e:
        logger.error(f"Error fetching feed {feed_url}: {e}")
        return []


def clean_html(html_text: str) -> str:
    """Remove HTML tags and clean up text."""
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:300] if len(text) > 300 else text


def fetch_article_content_and_image(url: str) -> dict:
    """
    Fetches HTML, extracts main content using Trafilatura,
    and extracts the og:image URL using BeautifulSoup.
    
    Adapted from Meridiano's utils.py
    
    Returns:
        dict: {'content': str|None, 'og_image': str|None, 'title': str|None}
    """
    content = None
    og_image = None
    title = None
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        html_content = response.text
        
        # Extract text content with trafilatura
        content = trafilatura.extract(
            html_content, 
            include_comments=False, 
            include_tables=False,
            include_images=False
        )
        
        # Parse HTML for og:image and title
        soup = BeautifulSoup(html_content, "lxml")
        
        # Extract og:image
        og_image_tag = soup.find("meta", property="og:image")
        if og_image_tag and og_image_tag.get("content"):
            og_image = og_image_tag["content"]
            og_image = urljoin(url, og_image)
        
        # Fallback: try twitter:image
        if not og_image:
            twitter_img = soup.find("meta", attrs={"name": "twitter:image"})
            if twitter_img and twitter_img.get("content"):
                og_image = twitter_img["content"]
                og_image = urljoin(url, og_image)
        
        # Extract title from og:title or <title>
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]
        elif soup.title:
            title = soup.title.string
        
        return {"content": content, "og_image": og_image, "title": title}
        
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout fetching {url}")
        return {"content": None, "og_image": None, "title": None}
    except requests.exceptions.RequestException as e:
        logger.warning(f"Request error fetching {url}: {e}")
        return {"content": None, "og_image": None, "title": None}
    except Exception as e:
        logger.error(f"Error processing {url}: {e}")
        return {"content": content, "og_image": None, "title": None}


def calculate_read_time(text: str, wpm: int = 200) -> int:
    """Calculate estimated reading time in minutes."""
    if not text:
        return 1
    word_count = len(text.split())
    minutes = max(1, round(word_count / wpm))
    return minutes


def extract_excerpt(content: str, max_length: int = 200) -> str:
    """Extract a clean excerpt from content."""
    if not content:
        return ""
    # Clean and truncate
    excerpt = content.strip()
    if len(excerpt) > max_length:
        excerpt = excerpt[:max_length].rsplit(' ', 1)[0] + "..."
    return excerpt


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")
    except:
        return ""


def sort_articles_by_date(articles: list, descending: bool = True) -> list:
    """
    Sort articles by publication date.
    
    Args:
        articles: List of article dicts with 'date' field
        descending: If True, most recent first; if False, oldest first
        
    Returns:
        Sorted list of articles
    """
    def parse_date(article):
        try:
            return datetime.fromisoformat(article.get("date", ""))
        except (ValueError, TypeError):
            return datetime.min
    
    return sorted(articles, key=parse_date, reverse=descending)


def crawl_category(category_id: str, category_data: dict) -> list:
    """
    Crawl all feeds for a category and return enriched articles.
    
    Args:
        category_id: Category identifier (e.g., 'tech', 'ciencia')
        category_data: Dict with 'name', 'description', 'feeds'
        
    Returns:
        List of article dicts with full metadata
    """
    articles = []
    seen_urls = set()
    
    for feed_url in category_data["feeds"]:
        entries = fetch_feed(feed_url)
        
        for entry in entries:
            # Skip duplicates
            if entry["link"] in seen_urls:
                continue
            seen_urls.add(entry["link"])
            
            # Fetch article content and image
            logger.info(f"  Processing: {entry['title'][:50]}...")
            article_data = fetch_article_content_and_image(entry["link"])
            
            # Apply blacklist filter again with full content
            full_content = article_data.get("content") or ""
            if contains_blacklisted_content(entry["title"], full_content):
                continue
            
            # Build article object
            article = {
                "id": hash(entry["link"]) & 0xFFFFFFFF,  # Positive 32-bit hash
                "title": entry["title"],
                "link": entry["link"],
                "date": entry["date"],
                "author": entry["author"],
                "category": category_id,
                "category_name": category_data["name"],
                "image_url": article_data["og_image"],
                "excerpt": extract_excerpt(article_data["content"]) or entry["summary"],
                "content": article_data["content"],
                "read_time": calculate_read_time(article_data["content"]),
                "domain": get_domain(entry["link"]),
                "has_image": article_data["og_image"] is not None,
            }
            
            articles.append(article)
            
            # Respect rate limiting
            time.sleep(0.5)
            
            # Limit articles per category
            if len(articles) >= MAX_ARTICLES_PER_CATEGORY:
                break
        
        if len(articles) >= MAX_ARTICLES_PER_CATEGORY:
            break
    
    # Sort articles by date (most recent first)
    articles = sort_articles_by_date(articles, descending=True)
    
    return articles


def select_capa_articles(all_articles: list, count: int = 6) -> list:
    """
    Select top articles for the front page (Capa).
    Prioritizes articles WITH images from major sources.
    """
    # First: articles with images from Capa category
    capa_with_images = [
        a for a in all_articles 
        if a["category"] == "capa" and a["has_image"]
    ]
    
    # Second: any article with images
    other_with_images = [
        a for a in all_articles 
        if a["category"] != "capa" and a["has_image"]
    ]
    
    # Combine and limit
    selected = capa_with_images[:count]
    if len(selected) < count:
        selected.extend(other_with_images[:count - len(selected)])
    
    # If still not enough, add articles without images
    if len(selected) < count:
        remaining = [a for a in all_articles if a not in selected]
        selected.extend(remaining[:count - len(selected)])
    
    # Sort selected capa articles by date (most recent first)
    selected = sort_articles_by_date(selected, descending=True)
    
    return selected[:count]


def crawl_all_feeds() -> dict:
    """
    Main crawling function. Fetches all feeds and returns structured data.
    
    Returns:
        Dict with 'capa', 'categories', and 'metadata'
    """
    logger.info("=" * 50)
    logger.info("Starting news crawl...")
    logger.info("=" * 50)
    
    start_time = time.time()
    all_articles = []
    categories_data = {}
    
    for category_id, category_info in FEEDS.items():
        logger.info(f"\n📰 Category: {category_info['name']}")
        logger.info("-" * 30)
        
        articles = crawl_category(category_id, category_info)
        all_articles.extend(articles)
        
        categories_data[category_id] = {
            "name": category_info["name"],
            "description": category_info["description"],
            "articles": articles,
            "count": len(articles),
        }
        
        logger.info(f"  ✓ Found {len(articles)} articles")
    
    # Select featured articles for Capa
    capa_articles = select_capa_articles(all_articles)
    
    elapsed = time.time() - start_time
    
    result = {
        "capa": capa_articles,
        "categories": categories_data,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(all_articles),
            "crawl_duration_seconds": round(elapsed, 2),
            "version": "1.1.0",
        }
    }
    
    logger.info("\n" + "=" * 50)
    logger.info(f"✅ Crawl complete! {len(all_articles)} articles in {elapsed:.1f}s")
    logger.info("=" * 50)
    
    return result


def save_json(data: dict, output_path: str):
    """Save data to JSON file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 Saved to: {output_path}")


if __name__ == "__main__":
    # Quick test
    data = crawl_all_feeds()
    save_json(data, "../docs/data/latest.json")
