# Counting

## About This Module

This module contains notebooks for counting various aspects of project data. The notebooks allow you to count project documents (`count_documents.ipynb`), to count the number of documents containing a specific token (`docs_by_search_term.ipynb`), to calculate token frequencies (`frequency.ipynb`), to calculate tf-idf scores (`tfidf.ipynb`), to calculate various collocation metrics (`collocation.ipynb`), and to grab summary statistics of documents, tokens, etc in the project (`vocab.ipynb`). The `vocab.ipynb` notebook requires that your json data files contain a `bag_of_words` field with term counts. If you did not generate this field when you imported your data, you can do so using `tokenize.ipynb`, which leverages <a href="https://spacy.io" target="_blank">spaCy's</a> tokenizer. The `docs_by_search_term.ipynb`, `frequency.ipynb`, `tfidf.ipynb`, and `collocation.ipynb` notebooks use a custom tokenizer based on the tokenizer available in <a href="https://www.nltk.org/" target="_blank">NLTK</a>. This differs from the tokenizer WE1S uses in its preprocessing and topic modeling pipelines, which only tokenizes unigrams. As a result, some features of these notebooks will not work if you do not have access to full-text data.

Notebooks in this module allow users to configure their text input field -- in other words, you can tell the code where to look to find the text you want to process. You have three options for this: the `content` field, the `bag_of_words` field, or the `features` field. The code expects data in these fields to be in the following formats:

* `content`: Full, plain-text data, stored as a string in each document.
* `bag_of_words`: A bag of words dictionary, where each key is a unique unigram, and each value is a count of the number of times that token appears in the document. The `import` module allows users to create the `bag_of_words` field and add it to their project data. Data is alphabetized by default, meaning the bags are not reconstructable.
* `features`: This field is inserted by the WE1S preprocessor using spaCy, and the recommended `content_field` to use if working with WE1S public data. It is a list of lists that contains information of the following kinds about each token in the document: `["TOKEN", "NORM", "LEMMA", "POS", "TAG", "STOPWORD", "ENTITIES"]`. NORM is a lowercased version of the token. LEMMA is the dictionary headword (so the lemma of "going" is "go"). POS is the part of speech according to spaCy's <a href="https://spacy.io/api/annotation#pos-tagging" target="_blank">taxonomy</a>. TAG is the equivalent in the Penn-Treebank system. ENTITIES is a named entity as classified <a href="https://spacy.io/api/annotation#named-entities" target="_blank">here</a>. Lemmas, POS, tags, and entities are all predicted by spaCy using its language model. STOPWORD is whether or not the lower case form of a token is classed as a stop word in a stoplist. For WE1S data, this is the WE1S Standard Stoplist. spaCy has its own stoplist, and users can also supply their own. Alphabetized by default.

If your json documents do not have a `content` field (if you are using publicly released WE1S data, for instance), and you are using the `bag_of_words` or `features` field as your text input, you will not be able to use some of the functions available in some notebooks in this module. You will also only be able to count unigrams (since all word bags or features tables are alphabetized and thus bigrams and trigrams are not reconstructable).

## User Guide

What follows are brief summaries of each notebook in this module. The notebooks themselves are flexible and have a wide range of functionality. For this reason, they are heavily documented and provide information about how to use them and what their different sections mean. Please refer to the notebooks for instructions about how to use the notebooks.

### `docs_by_search_term.ipynb`

This notebook allows you to count the number of documents in a project containing a specific word or phrase. You can also save document metadata to a dataframe, which you can explore in the notebook or download to your own machine. This notebook also allows you to download the documents containing this word or phrase themselves as either json or txt files.

### `frequency.ipynb`

This notebook provides methods for calculating raw and/or relative frequency values for ngrams (uni-, bi-, and/or trigrams are accepted) within a single document or across all of the project's documents.

### `tfidf.ipynb`

Tf-idf, or term frequency - inverse document frequency, is a common way of measuring the importance of tokens both within a given document and across your project as a whole. You calculate a token's tf-idf score by multipling its relative frequency within a given document by the inverse of the number of documents that token appears in throughout the corpus. See TF-IDF from scratch in python on real world dataset for a more in-depth explanation of the math.

Generally speaking, tokens with higher tf-idf scores (those closer to 1) are more important to a given document or corpus. At the document level, "distinctive" is a rough synonym for "important;" tf-idf provides a way to discover the tokens that are most distinctive within each document in your project. At the corpus or project level, a higher average tf-idf score means that a token is more frequently a distinctive word for documents within your corpus, i.e., it is potentially an important token for understanding your corpus overall.

### `collocation.ipynb`

Collocation is another way of discussing co-occurrence; in natural language processing, the term "collocation" usually refers to phrases of two or more tokens that commonly occur together in a given context. You can use this notebook to understand how common certain bi- and trigrams are in your project. Generally speaking, the more tokens you have in your project, and the larger your project data is, the more meaningful these metrics will be.

This notebook allows you to calculate five different collocation metrics:  1) Likelihood ratio; 2) Mutual information (MI) scores; 2) Pointwise mutual information (PMI) scores; 4) Student's t-test; and 5) Chi-squared test. See below for more information on each metric.

Collocation metrics are only useful when you can tokenize on bi- and trigrams. Therefore, this notebook assumes your documents include full-text data, and that this data is stored as a string in the `content` field of each document.

#### Likelihood Ratio

Likelihood ratios reflect the likelihood, within a given corpus (i.e., all documents in the project), of a specific bi- or trigram occurring (technically it tells us the likelihood that any two or three given words exist in a dependent relationship). The higher a likelihood score, the more strongly associated the words composing the bi- or trigram are with one another, roughly speaking. Likelihood ratios usually perform better than t-tests or chi-squared tests (see below) on sparse data (i.e., bigrams and trigrams), and so are often used in natural language processing. The code below is an implementation of Dunning's log likelihood test.

For more on likelihood ratios in natural language processing, see <a href="https://nlp.stanford.edu/fsnlp/promo/colloc.pdf" target="_blank">Foundations of Statistical Natural Language Processing</a>, pages 161-164, and <a href="https://stackoverflow.com/questions/48715547/how-to-interpret-python-nltk-bigram-likelihood-ratios" target="_blank">How to Interpret Python NLTK Bigram-Likelihood Ratios</a>.

#### Mutual Information (MI) Score

The MI score is a measure of the strength of association between any given token in a project and all of the project's tokens. An MI score measures how much more likely the words of a bi- or trigram are to co-occur within your project than they are to occur by themselves. A higher score indicates a higher strength of association. For more on this concept, see <a href="https://wordbanks.harpercollins.co.uk/other_doc/statistics.html#:~:text=The%20Mutual%20Information%20score%20expresses,between%20words%20x%20and%20y" target="_blank">this guide</a> on the mutual information scores and t-tests (see below) in corpus linguistics.

The code in this notebook implements NLTK's version of mutual information. See NLTK documentation <a href="https://www.nltk.org/_modules/nltk/metrics/association.html" target="_blank">here</a>.

MI scores are sensitive to unique words, which can make results less meaningful because often unique words will occur much less frequently throughout a corpus. Therefore, we recommend employing a frequency filter when calculating MI scores; the notebook includes this capability.

#### Pointwise Mutual Information (PMI) Score

PMI scores build on MI scores. Like MI scores, PMI scores measure the association between any given token in a project and all of the project's tokens. A PMI score measures how much more likely the words of a bi- or trigram are to co-occur within your project than they are to occur by themselves. A higher score indicates a higher strength of association. It differs from an MI score in that it refers to single comparisons, while MI scores are a measure of the average PMI scores over all comparisons. For more on this concept, see Gerlof Bouma's widely cited paper, <a href="https://pdfs.semanticscholar.org/1521/8d9c029cbb903ae7c729b2c644c24994c201.pdf" target="_blank">Normalized (Pointwise) Mutual Information in Collocation Extraction</a>.

Like MI scores, PMI scores are sensitive to unique words, which can make results less meaningful because often unique words will occur much less frequently throughout a corpus. Therefore, we recommend employing a frequency filter when calculating MI scores; the notebook includes this capability.

#### Student's T-test

The student's t-test is perhaps one of the most widely used methods of hypothesis testing. This implementation of the t-test assumes that the words in any bi- or trigram are independent, and it measures how likely the words are to appear together in your project. Like the PMI score, a higher t-test score indicates a higher likelihood that the words in the bi- or trigram occur together in your project than that they occur separately. However, t-tests and chi-square tests (see below) have been shown to not perform as well with sparse data like bigrams and trigrams.

You can find a good general discussion of what a t-test is <a href="https://towardsdatascience.com/inferential-statistics-series-t-test-using-numpy-2718f8f9bf2f" target="_blank">here</a>.

#### Chi-Square Test

The chi-square test is another test of statistical significance. Like a t-test, a chi-squared test assumes that the words in any bi- or trigram are independent. But unlike a t-test, a chi-squared test does not assume a normal distribution. The code below uses an implementation of Pearson's chi-square test of association. As with PMI and t-test scores, a higher chi-squared test score indicates a greater degree of likelihood, i.e., a higher likelihood that the words in a given bi- or trigram occur together in your project.

Decent explanations of the chi-squared test can be found <a href="https://www.analyticsvidhya.com/blog/2019/11/what-is-chi-square-test-how-it-works/" target="_blank">here</a> and <a href="https://towardsdatascience.com/chi-square-test-for-feature-selection-in-machine-learning-206b1f0b8223" target="_blank">here</a>.

### `tokenize.ipynb`

Normally text analysis tools have to divide a text into countable "tokens" (most frequently words). This process is called tokenization. This cell allows you to pre-tokenize your data so that other tools do not need to take this step. It generates a dictionary of token-count pairs such as `{"cat": 3, "dog": 2}` for each of your JSON files. This dictionary is appended to the JSON file in the `bag_of_words` field.

This notebook offers two tokenization methods. The default method is strips all non-alphanumeric characters and then divides the text into tokens on white space. Alternatively, you can use the <a href="https://spacy.io/" target="_blank">spaCy</a> Natural Language Processing library to tokenize based on spaCy's language model. spaCy extracts linguistic `features` from your text, not only tokens but parts of speech and named entities. This is instrinsically slower and may require a lot of memory for large texts. To use WE1S's custom spaCy tokenizer, set `method='we1s'`. If your text has been previously processed by spaCy and there is a `features` table in your JSON file, the tokenizer will attempt to use it to build the `bag_of_words` dictionary.

Errors will be logged to the path you set for the log_file.

### `vocab.ipynb`

This notebook allows you to build a single json vocab file containing term counts for all the documents in your project's json directory. It also allows you to access information about the vocab in a convenient manner. If your data does not already have `bag_of_words` fields, you should run `tokenize.ipynb` first.

## Module Structure

:material-folder-outline: counting<br>
┣ :material-folder-outline: scripts<br>
 ┃ ┣ :material-language-python: count_docs.py<br>
 ┃ ┣ :material-language-python: count_tokens.py<br>
 ┃ ┣ :material-language-python: tokenizer.py<br>
 ┃ ┣ :material-language-python: vocab.py<br>
 ┣ :jupyter-jupyter-logo: collocation.ipynb<br>
 ┣ :jupyter-jupyter-logo: count_documents.ipynb<br>
 ┣ :jupyter-jupyter-logo: docs_by_search_term.ipynb<br>
 ┣ :jupyter-jupyter-logo: frequency.ipynb<br>
 ┣ :jupyter-jupyter-logo: tfidf.ipynb<br>
 ┣ :material-file-outline: README.md<br>
 ┣ :jupyter-jupyter-logo: tokenize.ipynb<br>
 ┗ :jupyter-jupyter-logo: vocab.ipynb
