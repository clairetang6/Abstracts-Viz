# Pubviz
Visualize a scientist's journal articles using abstract similarity.

Check it out at [pubviz.com](http://pubviz.com)!  

This project uses [d3.js](http://d3js.org/) to visualize a scientist's papers. Each node represents a paper, and edges link papers that have similar topics.

![The resulting graph for nobel laureate Eric Kandel!](kandel.png) 

This web app is built using [Python3](https://docs.python.org/3/) and [aiohttp](http://aiohttp.readthedocs.org/en/stable/), enabling asynchronous calls to the [PubMed](http://www.ncbi.nlm.nih.gov/pubmed) API to get the full text of a scientist's abstracts.

The text of the abstracts is then processed using [nltk](http://www.nltk.org/), [scikit-learn](http://scikit-learn.org/stable/), and [scipy](http://www.scipy.org/) to compute a similarity matrix, which is then visualized as a force-directed graph.






