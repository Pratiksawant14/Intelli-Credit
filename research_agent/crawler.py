"""
Custom crawler for research using feedparser (Google News RSS) and newspaper3k.
"""
import urllib.parse
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict

def fetch_evidence_for_entity(name: str, keywords: List[str] = []) -> List[Dict]:
    """
    Crawls Google News RSS for the given company name and keywords.
    Auto-limits to roughly the last 6 months (via RSS 'when:6m' query param or date parsing).
    
    Returns a list of dictionaries with title, date, source, url, and snippet content.
    """
    evidence_list = []
    
    # Construct the query
    query_parts = [f'"{name}"']
    if keywords:
        kw_str = " OR ".join(keywords)
        query_parts.append(f"({kw_str})")
        
    # Append 6 months limit to Google News query
    query_parts.append("when:6m")
    
    full_query = " AND ".join(query_parts)
    encoded_query = urllib.parse.quote(full_query)
        
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    feed = feedparser.parse(rss_url)
    
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    for entry in feed.entries:
        # Check date
        try:
            from email.utils import parsedate_to_datetime
            pub_date = parsedate_to_datetime(entry.published)
            # Remove timezone for simple comparison 
            pub_date = pub_date.replace(tzinfo=None)
            if pub_date < six_months_ago:
                continue
            date_str = pub_date.strftime("%Y-%m-%d")
        except:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")

        evidence_list.append({
            "title": entry.title,
            "date": date_str,
            "source": entry.source.title if hasattr(entry, 'source') else "Google News",
            "url": entry.link,
            "content": entry.summary # Usually contains an HTML snippet, could be cleaned
        })
        
    return evidence_list
