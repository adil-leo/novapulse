import xml.etree.ElementTree as ET
import urllib.request
import json

# AI & Tech RSS Feeds
FEEDS = [
    "https://news.ycombinator.com/rss",
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml"
]

def get_news():
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for url in FEEDS:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                for item in root.findall('.//item')[:5]: # Top 5 news per site
                    title = item.find('title').text if item.find('title') is not None else ''
                    link = item.find('link').text if item.find('link') is not None else ''
                    pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    
                    if title and link:
                        articles.append({
                            'title': title,
                            'link': link,
                            'date': pubDate[:16] if pubDate else ''
                        })
        except Exception as e:
            print(f"Error reading {url}: {e}")

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print("Success: news.json generated!")

if __name__ == '__main__':
    get_news()