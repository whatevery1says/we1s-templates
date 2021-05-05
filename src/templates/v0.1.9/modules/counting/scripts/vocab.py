"""vocab.py.

Functions for building a single json file (the vocab file) containing terms counts for all the documents in a json directory. It also allows you to create a `Vocab` object that can be used to access the information in the file as `Vocab.vocab`.

For use with vocab.ipynb v 2.0.

Last update: 2020-07-01
"""

import json
import os
import pandas as pd
import time
from IPython.display import display, HTML

# Build the vocab file
def build_vocab(json_dir, vocab_file):
    """Read the json folder and save vocab to a file."""
    start_time = time.time()
    print('Processing...')
    vocab = []
    no_bow = []
    json_files = [file for file in os.listdir(json_dir) if file.endswith('.json')]
    for file in json_files:
        doc_vocab = {}
        with open(os.path.join(json_dir, file), 'r') as f:
            doc = json.loads(f.read())
        doc_vocab['name'] = doc['name']
        doc_vocab['filename'] = file
        if 'bag_of_words' in doc:
            doc_vocab['term_counts'] = doc['bag_of_words']
            vocab.append(doc_vocab)
        else:
            no_bow.append(file)
    if len(no_bow) != len(json_files):
        with open(vocab_file, 'w') as f:
            f.write(json.dumps(vocab))
        print('Processed in %s seconds.' % (time.time() - start_time))
        display(HTML('<p>The vocab file was saved to ' + vocab_file + '.</p>'))
    msg = None
    if len(no_bow) > 0 and len(no_bow) < 20:
        msg = '<p style="color: red;">Warning! The following file(s) could not be processed because they did not contain `bag_of_words` fields.</p>'
        msg += '<ul>'
        for item in no_bow:
            msg += '<li>' + item + '</li>'
        msg += '</ul>'
    elif len(no_bow) > 0 and len(no_bow) >= 20:
        msg = '<p style="color: red;">Warning! 20 or more files could not be processed because they did not contain `bag_of_words` fields.</p>'
    if msg is not None:
        msg += '<p style="color: red;">You may need to run the <a href="tokenize.ipynb">tokenize</a> notebook to ensure that all your data '
        msg += 'has been tokenized. You can then try re-running this notebook.</p>'
        display(HTML(msg))

# The Vocab class
class Vocab():
    """Create a class for accessing the vocab."""

    def __init__(self, file):
        """Initialise the Vocab object."""
        with open(file, 'r') as f:
            self.vocab = json.loads(f.read())

    def get_filenames(self):
        """Return a list of filenames used to generate the vocab."""
        return [doc['filename'] for doc in self.vocab]

    def get_names(self):
        """Return a list of document names used to generate the vocab."""
        return [doc['name'] for doc in self.vocab]

    def get_document(self, value, key='name'):
        """Return a single document by filename or name."""
        if value.endswith('.json'):
            key = 'filename'
        return [x for x in self.vocab if x[key] == value][0]

    def get_documents(self, value, key='name'):
        """Return a list of document by filename or name."""
        documents = []
        for doc in value:
            if doc.endswith('.json'):
                key = 'filename'
            documents.append([x for x in self.vocab if x[key] == doc])
        return documents
    
    def get_num_docs(self):
        """Return the number of documents in the vocab."""
        return len(self.vocab)

    def get_num_terms(self, documents=None):
        """Return the number of terms in the vocab or a list of documents."""
        terms = []
        if documents == None:
            docs = self.vocab
        else:
            docs = [term for term in self.vocab if term['name'] in documents]
        for doc in docs:
            for term, count in doc['term_counts'].items():
                terms.append(term)
        return len(list(set(terms)))

    def get_num_tokens(self, documents=None):
        """Return the total number of tokens in the vocab or a list of documents."""
        tokens = []
        if documents == None:
            docs = self.vocab
        else:
            docs = [term for term in self.vocab if term['name'] in documents]
        for doc in docs:
            for term, count in doc['term_counts'].items():
                tokens.append(count)
        return sum(tokens)

    def get_terms(self, documents=None, sortby=['TERM', 'COUNT'], ascending=[True, True], as_dict=False):
        """Return a dict of terms in the vocab, or, optionally, a list of documents."""
        terms = {}
        if documents == None:
            docs = self.vocab
        else:
            docs = documents
        for doc in docs:
            for term, count in doc['term_counts'].items():
                if term in terms.keys():
                    terms[term] = terms[term] + count
                else:
                    terms[term] = count
        # Create a dataframe
        terms = [(k, v) for k, v in terms.items()]
        df = pd.DataFrame(terms, columns=['TERM', 'COUNT']) 
        df.sort_values(by=sortby, ascending=ascending, inplace=True)
        if as_dict:
            term_list = df.to_dict(orient='records')
            terms = {}
            for term in term_list:
                terms[term['TERM']] = term['COUNT']
            return terms
        else:
            return df