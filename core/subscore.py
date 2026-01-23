import urllib
import urllib.parse
from utils.regex import get_tld, get_domain
from math import log1p
from utils.config import Config

class SubScore:


    @staticmethod
    def get_url_rank( url, importance):
        url_obj = urllib.parse.urlparse(url)


        paths = [p for p in url_obj.path.split('/') if p]
        subdomains = url_obj.netloc.split('.')[:-2]
        params = url_obj.query.split('&') if url_obj.query else []

        path_depth = len(paths)
        param_count = len(params)
        subdomain_count = len(subdomains)

        total_depth = path_depth + param_count + subdomain_count

        path_length_penalty = 1 / (1 + total_depth * 0.15)

        domain = get_domain(url)
        tld = get_tld(domain)
        if tld in Config.EDU_TLDS:
            tld_multiplier = Config.EDU_MULT
        elif tld in Config.AUTHORITIVE_TLDS:
            tld_multiplier = Config.AUTHORITIVE_MULT
        else:
            tld_multiplier = Config.GENERIC_MULT

        base_score = log1p(importance) * path_length_penalty * tld_multiplier
        return base_score

    @staticmethod
    def get_ca_rank(url, score):
        pass
