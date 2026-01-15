
from core.hybrid import HybridSearch
from utils.regex import  get_domain
from flask import jsonify, Blueprint
from utils.misc import site_details


search_bp = Blueprint('search_bp', __name__)
HybridSearch = HybridSearch(return_limit=8)


@search_bp.route("/<term>")
def search_route(term):
    # keep here indexes are always updated
    results, contents = HybridSearch.combined_search(term=term)
    site_data = []

    for result, content in zip(results, contents):
        title, description, site_content = site_details(result, content)


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


