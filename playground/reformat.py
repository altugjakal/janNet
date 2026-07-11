from src.jannet.utils.misc import extract_words


def search(term, ri_client):
    term = extract_words(term)

    result = ri_client.search(term)

    for element in result:
        pass




