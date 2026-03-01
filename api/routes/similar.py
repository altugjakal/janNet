from core.requery import Requery
from managers.db_manager import get_vdb, get_db
from utils.parsing import get_domain, html_to_clean
from flask import jsonify, Blueprint, request
from utils.misc import site_details


similar_bp = Blueprint('similar_bp', __name__)
Requery = Requery(db=get_db(), vdb=get_vdb())


@similar_bp.route("/")
def similar_route():
    url = request.args.get('url')
    results, contents = Requery.find_similar(url)
    site_data = []

    for result, content in zip(results, contents):
        title, description, site_content = site_details(result, content)
        cleaned_content = html_to_clean(site_content)


        site_data.append({
            'url': result,
            'content': cleaned_content,
            'title': title,
            'description': description,
            'domain': get_domain(result),
            'favicon': f"https://www.google.com/s2/favicons?domain={get_domain(result)}"

        })



    return jsonify({
        'results': site_data
    })


