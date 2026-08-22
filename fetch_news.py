import xml.etree.ElementTree as ET
import urllib.request
import json
import re

FEEDS = [
    "https://news.ycombinator.com/rss",
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml"
]

FALLBACK_IMG = "https://images.unsplash.com/photo-1518770660439-4636190af475?w=500&q=80"

def extract_image(item_elem):
    # Check media:content or enclosure
    for elem in item_elem.iter():
        if elem.tag.endswith('content') or elem.tag.endswith('thumbnail'):
            url = elem.attrib.get('url')
            if url: return url
        if elem.tag == 'enclosure':
            url = elem.attrib.get('url')
            if url and 'image' in elem.attrib.get('type', ''): return url
            
    # Check img tag inside description
    desc = item_elem.find('description')
    if desc is not None and desc.text:
        img_match = re.search(r'<img [^>]*src="([^"]+)"', desc.text)
        if img_match: return img_match.group(1)
        
    return FALLBACK_IMG

def get_news():
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for url in FEEDS:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                for item in root.findall('.//item')[:6]:
                    title = item.find('title').text if item.find('title') is not None else ''
                    link = item.find('link').text if item.find('link') is not None else ''
                    pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    img = extract_image(item)
                    
                    if title and link:
                        articles.append({
                            'title': title,
                            'link': link,
                            'date': pubDate[:16] if pubDate else 'Latest',
                            'image': img
                        })
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print("News updated with images!")

if __name__ == '__main__':
    get_news()