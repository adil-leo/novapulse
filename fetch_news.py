import xml.etree.ElementTree as ET
import urllib.request
import json
import re
import html

FEEDS = {
    "Google News": "https://news.google.com/rss/search?q=AI+technology&hl=en-US&gl=US&ceid=US:en",
    "NYTimes Tech": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "BBC Tech": "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "The Verge": "https://www.theverge.com/rss/index.xml"
}

FALLBACK_IMGS = [
    "https://images.unsplash.com/photo-1518770660439-4636190af475?w=500&q=80",
    "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500&q=80",
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=500&q=80"
]

def clean_text(raw_html):
    if not raw_html: return ""
    cleantext = re.sub(r'<.*?>', '', raw_html)
    return html.unescape(cleantext).strip()

def extract_image(item_elem, desc_text):
    for elem in item_elem.iter():
        if 'content' in elem.tag or 'thumbnail' in elem.tag:
            url = elem.attrib.get('url')
            if url: return url
        if elem.tag == 'enclosure':
            url = elem.attrib.get('url')
            if url: return url
            
    img_match = re.search(r'<img [^>]*src=["\']([^"\']+)["\']', desc_text)
    if img_match: return img_match.group(1)
    return ""

def get_news():
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    img_counter = 0

    for source, url in FEEDS.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                for item in root.findall('.//item')[:8]: # 8 items per source (Total ~32 articles)
                    title = item.find('title').text if item.find('title') is not None else ''
                    link = item.find('link').text if item.find('link') is not None else ''
                    pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    
                    raw_desc = ""
                    desc_elem = item.find('description')
                    if desc_elem is not None and desc_elem.text:
                        raw_desc = desc_elem.text
                    
                    summary_text = clean_text(raw_desc)
                    summary = summary_text[:140] + "..." if len(summary_text) > 140 else summary_text
                    
                    img = extract_image(item, raw_desc)
                    if not img:
                        img = FALLBACK_IMGS[img_counter % len(FALLBACK_IMGS)]
                        img_counter += 1
                        
                    if title and link:
                        articles.append({
                            'title': clean_text(title),
                            'link': link,
                            'date': pubDate[:16] if pubDate else 'Recent',
                            'summary': summary if summary else "Click to read full coverage on this breaking tech story.",
                            'source': source,
                            'image': img
                        })
        except Exception as e:
            print(f"Error fetching {source}: {e}")

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"Success: {len(articles)} articles updated!")

if __name__ == '__main__':
    get_news()