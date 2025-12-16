# janNet: Lightweight Search Engine

janNet is a lightweight, experimental search engine project designed for specialised use and testing. It indexes and searches a curated set of URLs and domains from a list.

## Flow

**Crawl**

Scrapes anchors and adds them to the queue.

Vectorises webpage content using an embedding model.

Stores vectors in a sqlite database for later use.

**Search**

Aplies cosine similarity to vectors in the database

Applies a penalty to URLs with greater depth.

Sorts result according to the output similarity to the search term.

