
from core.search import search
from utils.regex import  get_domain
from flask import jsonify, Blueprint
from utils.misc import site_details
from core.v_search import vector_search


search_bp = Blueprint('search_bp', __name__)

@search_bp.route("/<term>")
def search_route(term):
    # keep here indexes are always updated
    results = vector_search(term)
    site_data = []
    contents = []

    for result in results:
        title, description, content = site_details(result)
        contents.append(content)

        site_data.append({
            'url': result,
            'title': title,
            'description': description,
            'domain': get_domain(result),
            'favicon': f"https://www.google.com/s2/favicons?domain={get_domain(result)}"

        })

    return jsonify({
        'results': site_data
    })


