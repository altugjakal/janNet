from src.jannet.core.process.reverse_index import ReverseIndexCommunicator

ri_client = ReverseIndexCommunicator()
query = ['this', 'is', 'a']
ri_client.search(query)