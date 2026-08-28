import json
import re
import feedparser

# NovaPulse Global RSS Feed Directory
FEEDS = [
    # AI & ML
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "source": "TechCrunch AI"},
    {"url": "https://venturebeat.com/category/ai/feed/", "source": "VentureBeat AI"},
    
    # Tech & Software
    {"url": "https://arstechnica.com/feed/", "source": "Ars Technica"},
    {"url": "https://www.wired.com/feed/category/gear/latest/rss", "source": "Wired Tech"},
    {"url": "https://news.ycombinator.com/rss", "source": "Hacker News"},

    # Crypto & Web3
    {"url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "source": "CoinDesk"},
    {"url": "https://cointelegraph.com/rss", "source": "CoinTelegraph"},

    # Business & Startups
    {"url": "https://techcrunch.com/category/startups/feed/", "source": "TC Startups"},
    {"url": "https://www.entrepreneur.com/latest.rss", "source": "Entrepreneur"}
]

def clean_html(raw_html):
    """Remove HTML tags and extra spaces from summary"""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return ' '.join(cleantext.split())

def extract_image(entry):
    """Extract image URL from feed media content or enclosures"""
    # 1. Media Content Tag
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url', '')
    # 2. Enclosures Tag
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        return entry.enclosures[0].get('href', '')
    # 3. Fallback High-Quality Unsplash Tech Image
    return "https://images.unsplash.com/photo-1518770660439-4636190af475?w=500&q=80"

def fetch_all_news():
    articles = []

    for feed_info in FEEDS:
        print(f"Fetching: {feed_info['source']}...")
        try:
            parsed_feed = feedparser.parse(feed_info["url"])
            
            # Extract top 4 entries per RSS feed
            for entry in parsed_feed.entries[:4]:
                summary_raw = entry.get('summary', entry.get('description', ''))
                clean_sum = clean_html(summary_raw)
                
                # Truncate summary if too long
                if len(clean_sum) > 170:
                    clean_sum = clean_sum[:167] + "..."

                date_str = entry.get('published', entry.get('updated', 'Today'))
                if len(date_str) > 16:
                    date_str = date_str[:16]

                articles.append({
                    "title": entry.get('title', 'Latest Update'),
                    "link": entry.get('link', '#'),
                    "summary": clean_sum if clean_sum else "Click read more to view full article.",
                    "source": feed_info["source"],
                    "date": date_str,
                    "image": extract_image(entry)
                })
        except Exception as e:
            print(f"Failed to fetch {feed_info['source']}: {e}")

    # Write cleaned feed array to news.json
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done! Total {len(articles)} articles updated in news.json.")

if __name__ == "__main__":
    fetch_all_news()