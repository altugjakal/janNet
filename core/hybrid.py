from core.v_search import vector_search
from core.search import search

def hybrid(term, vector_weight=0.4, kw_weight=0.6, return_limit=5):


    keyword_scores = search(term)
    vector_scores = vector_search(term)
    
    
    def normalize(scores):
        if not scores:
            return {}
        mx = max(scores.values())
        mn = min(scores.values())
        if mx == mn:
            return {url: 1.0 for url in scores}
        return {url: (s - mn) / (mx - mn) for url, s in scores.items()}
    
    keyword_scores = normalize(keyword_scores)
    vector_scores = normalize(vector_scores)
    
    
    all_urls = set(keyword_scores.keys()) | set(vector_scores.keys())
    
    combined_scores = {}
    for url in all_urls:
        kw = keyword_scores.get(url, 0)
        vec = vector_scores.get(url, 0)
        combined_scores[url] = kw_weight * kw + vector_weight * vec
    
    
    sorted_urls = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    
    
    print(f"\nHybrid search for '{term}' (KW: {kw_weight}, Vec: {vector_weight})")
    print(f"Found: {len(keyword_scores)} keyword, {len(vector_scores)} vector, {len(all_urls)} total")
    print("\nTop results:")
    for i, (url, score) in enumerate(sorted_urls[:return_limit], 1):
        kw = keyword_scores.get(url, 0)
        vec = vector_scores.get(url, 0)
        print(f"{i}. {url}")
        print(f"   Combined: {score:.3f} (KW: {kw:.3f}, Vec: {vec:.3f})")
    
    return [url for url, score in sorted_urls[:return_limit]]