
from core.hybrid_oop import HybridSearch
from utils.regex import  get_domain
from flask import jsonify, Blueprint
from utils.misc import site_details


search_bp = Blueprint('search_bp', __name__)
HybridSearch = HybridSearch(return_limit=8)


@search_bp.route("/<term>")
def search_route(term):
    # keep here indexes are always updated
    results = HybridSearch.combined_search(term=term)
    site_data = []
    contents = []

    for result in results:
        title, description, content = site_details(result)


        site_data.append({
            'url': result,
            'content': content,
            'title': title,
            'description': description,
            'domain': get_domain(result),
            'favicon': f"https://www.google.com/s2/favicons?domain={get_domain(result)}"

        })

    return jsonify({
        'results': site_data,
        'contents': contents
    })


