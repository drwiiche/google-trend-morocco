import xml.etree.ElementTree as ET
import requests
import hashlib
import os

def fetch_rss(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def parse_rss(xml_content):
    root = ET.fromstring(xml_content)
    items = []

    namespaces = {
        'ht': 'https://trends.google.com/trending/rss'
    }

    for item in root.findall('./channel/item'):
        title = item.find('title').text
        approx_traffic = item.find('ht:approx_traffic', namespaces).text if item.find('ht:approx_traffic', namespaces) else 'N/A'
        pub_date = item.find('pubDate').text
        
        news_items = []
        for news_item in item.findall('ht:news_item', namespaces):
            news_title = news_item.find('ht:news_item_title', namespaces).text
            news_url = news_item.find('ht:news_item_url', namespaces).text
            news_items.append(f"- **{news_title}**: [Link]({news_url})")
        
        news_items_combined = "\n".join(news_items)
        
        item_hash = hashlib.md5((title + pub_date).encode()).hexdigest()
        
        items.append({
            'Title': title,
            'Approx Traffic': approx_traffic,
            'Publication Date': pub_date,
            'News Items': news_items_combined,
            'Hash': item_hash
        })
    
    return items

def update_markdown(new_items, markdown_file, processed_file):
    # Create the markdown file if it doesn't exist
    if not os.path.exists(markdown_file):
        with open(markdown_file, 'w', encoding='utf-8') as md:
            md.write("# END\n\n")

    if os.path.exists(processed_file):
        with open(processed_file, 'r', encoding='utf-8') as f:
            processed_hashes = set(f.read().splitlines())
    else:
        processed_hashes = set()

    with open(markdown_file, 'r+', encoding='utf-8') as md:
        content = md.read()
        md.seek(0, 0)

        new_entries = []
        for item in new_items:
            if item['Hash'] not in processed_hashes:
                new_entries.append(f"### {item['Title']} ({item['Approx Traffic']}, {item['Publication Date']})\n\n{item['News Items']}\n\n")
                processed_hashes.add(item['Hash'])

        if new_entries:
            md.write("\n".join(new_entries) + "\n" + content)

    with open(processed_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(processed_hashes))

# Configuration
rss_url = 'https://trends.google.com/trending/rss?geo=MA'
markdown_file = 'trending_news.md'
processed_file = 'processed_hashes.txt'

# Fetch, parse, and update
rss_content = fetch_rss(rss_url)
new_items = parse_rss(rss_content)
update_markdown(new_items, markdown_file, processed_file)
