# Abstracts-Viz
Visualize a scientist's journal articles using abstract similarity.

This project uses [d3.js](http://d3js.org/) to visualize a scientist's papers. Each node represents a paper, and edges link papers that have similar topics.

The backend for this little web app uses [Flask](http://flask.pocoo.org/) to call the [PubMed](http://www.ncbi.nlm.nih.gov/pubmed) API and get the full text of a scientist's abstracts.

The text of the abstracts is then processed using [nltk](http://www.nltk.org/), [scikit-learn](http://scikit-learn.org/stable/), and [scipy](http://www.scipy.org/) to compute a similarity matrix, which is then visualized as a force-directed graph.






