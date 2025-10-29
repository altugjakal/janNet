# janNet: Lightweight Search Engine

janNet is a lightweight, experimental search engine project designed for specialised use and testing. It indexes and searches a curated set of URLs and domains from a list.

## Flow

**Crawl**

Scrapes anchors and adds them to the queue.

Removes stopwords and assigns base importance with respect to the html tag.

Stores keywords and urls(paired with the base importance) in a .csv file.

**Search**

Extracts non-stop words from the query.

Searches the reverse index using the cleaned query terms.

Applies a penalty to URLs with greater depth.

Increases temporary importance exponentially for each repeated keyword.

Sorts result according to the output importance.

**Summariser**

MIGHT GET REMOVED: Summarises the bodies of the returned web pages using a lightweight LLM.

## Features

janNet uses the library NLTK to remove stopwords and word stemming.

- **CSV-based Indexing:** Uses CSV files to store and manage URLs, domains, and keyword indexes.
- **Keyword Search:** Search for relevant URLs by keywords using a simple matching algorithm.
- **Crawling & Indexing:** Crawl URLs and extract keywords to build and update the search index.
