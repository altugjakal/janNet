# janNet: Specialized Search Engine

janNet is a lightweight(not anymore), experimental search engine project designed for specialised use and testing. It indexes and searches a curated set of URLs and domains from a list.

## Flow
The bot crawls through the web.
Each word is assigned an importance with respect to their location in the document
and their TF-IDF score.
Document is then turned into a vector of 384 dimensions and stored in a database.

On search, the term is turned into a vector of same size.
The term vector is compared to other vectors in the database, resulting in a closeness-score (cosine similarity).
And then a copy of the input term is spliced into words to be seacrhed in the index. Repetitive words cause the cumulation
of importance scores of the words in the word-index.



