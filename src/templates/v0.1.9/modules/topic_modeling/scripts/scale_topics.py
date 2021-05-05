"""scale_topics.py.

Create a topic_scaled.csv file from the MALLET state file.

Combines code by Jeri E. Wieringa (https://github.com/jerielizabeth/Gospel-of-Health-Notebooks/blob/master/blogPosts/pyLDAvis_and_Mallet.ipynb)
to transform MALLET data for use with pyLDAvis and uses code derived
from pyLDAvis to calculate topic coordinates using MDS.
and topic_scaled files below.

For use with 02_model_topics.ipynb v 2.0.

Last update: 2020-06-03
"""

# pylint: disable=E1101
# pylint: disable=W1201


# Python imports
import gzip
import logging
import os
import numpy as np
import pandas as pd
import sklearn.preprocessing
# Set fallback for MDS scaling
try:
    from sklearn.manifold import MDS, TSNE
    sklearn_present = True
except ImportError:
    sklearn_present = False
from IPython.display import display, HTML
from past.builtins import basestring
from scipy.stats import entropy
from scipy.spatial.distance import pdist, squareform

from timer import Timer

def __num_dist_rows__(array, ndigits=2):
    return array.shape[0] - int((pd.DataFrame(array).sum(axis=1) < 0.999).sum())


class ValidationError(ValueError):
    """Handle validation errors."""

    pass

def _input_check(topic_term_dists, doc_topic_dists, doc_lengths, vocab, term_frequency):
    ttds = topic_term_dists.shape
    dtds = doc_topic_dists.shape
    errors = []
    def err(msg):
        """Append error message."""
        errors.append(msg)

    if dtds[1] != ttds[0]:
        err('Number of rows of topic_term_dists does not match number of columns of doc_topic_dists; both should be equal to the number of topics in the model.')

    if len(doc_lengths) != dtds[0]:
        err('Length of doc_lengths not equal to the number of rows in doc_topic_dists; both should be equal to the number of documents in the data.')

    W = len(vocab)
    if ttds[1] != W:
        err('Number of terms in vocabulary does not match the number of columns of topic_term_dists (where each row of topic_term_dists is a probability distribution of terms for a given topic).')
    if len(term_frequency) != W:
        err('Length of term_frequency not equal to the number of terms in the vocabulary (len of vocab).')

    if __num_dist_rows__(topic_term_dists) != ttds[0]:
        err('Not all rows (distributions) in topic_term_dists sum to 1.')

    if __num_dist_rows__(doc_topic_dists) != dtds[0]:
        err('Not all rows (distributions) in doc_topic_dists sum to 1.')

    if len(errors) > 0:
        return errors


def _input_validate(*args):
    res = _input_check(*args)
    if res:
        raise ValidationError('\n' + '\n'.join([' * ' + s for s in res]))


def _jensen_shannon(_P, _Q):
    _M = 0.5 * (_P + _Q)
    return 0.5 * (entropy(_P, _M) + entropy(_Q, _M))


def _pcoa(pair_dists, n_components=2):
    """Principal Coordinate Analysis.

    AKA Classical Multidimensional Scaling
    code referenced from skbio.stats.ordination.pcoa
    https://github.com/biocore/scikit-bio/blob/0.5.0/skbio/stats/ordination/_principal_coordinate_analysis.py
    """
    # pairwise distance matrix is assumed symmetric
    pair_dists = np.asarray(pair_dists, np.float64)

    # perform SVD on double centred distance matrix
    n = pair_dists.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n
    B = - H.dot(pair_dists ** 2).dot(H) / 2
    eigvals, eigvecs = np.linalg.eig(B)

    # Take first n_components of eigenvalues and eigenvectors
    # sorted in decreasing order
    ix = eigvals.argsort()[::-1][:n_components]
    eigvals = eigvals[ix]
    eigvecs = eigvecs[:, ix]

    # replace any remaining negative eigenvalues and associated eigenvectors with zeroes
    # at least 1 eigenvalue must be zero
    eigvals[np.isclose(eigvals, 0)] = 0
    if np.any(eigvals < 0):
        ix_neg = eigvals < 0
        eigvals[ix_neg] = np.zeros(eigvals[ix_neg].shape)
        eigvecs[:, ix_neg] = np.zeros(eigvecs[:, ix_neg].shape)

    return np.sqrt(eigvals) * eigvecs


def js_PCoA(distributions):
    """Perform dimension reduction.

    Works via Jensen-Shannon Divergence & Principal Coordinate Analysis
    (aka Classical Multidimensional Scaling)

    Parameters
    ----------
    distributions : array-like, shape (`n_dists`, `k`)
        Matrix of distributions probabilities.

    Returns
    -------
    pcoa : array, shape (`n_dists`, 2)

    """
    dist_matrix = squareform(pdist(distributions, metric=_jensen_shannon))
    return _pcoa(dist_matrix)


def js_MMDS(distributions, **kwargs):
    """Perform dimension reduction.

    Works via Jensen-Shannon Divergence & Metric Multidimensional Scaling

    Parameters
    ----------
    distributions : array-like, shape (`n_dists`, `k`)
        Matrix of distributions probabilities.

    **kwargs : Keyword argument to be passed to `sklearn.manifold.MDS()`

    Returns
    -------
    mmds : array, shape (`n_dists`, 2)

    """
    dist_matrix = squareform(pdist(distributions, metric=_jensen_shannon))
    model = MDS(n_components=2, random_state=0, dissimilarity='precomputed', **kwargs)
    return model.fit_transform(dist_matrix)


def js_TSNE(distributions, **kwargs):
    """Perform dimension reduction.

    Works via Jensen-Shannon Divergence & t-distributed Stochastic Neighbor Embedding

    Parameters
    ----------
    distributions : array-like, shape (`n_dists`, `k`)
        Matrix of distributions probabilities.

    **kwargs : Keyword argument to be passed to `sklearn.manifold.TSNE()`

    Returns
    -------
    tsne : array, shape (`n_dists`, 2)

    """
    dist_matrix = squareform(pdist(distributions, metric=_jensen_shannon))
    model = TSNE(n_components=2, random_state=0, metric='precomputed', **kwargs)
    return model.fit_transform(dist_matrix)


def _df_with_names(data, index_name, columns_name):
    if isinstance(data, pd.DataFrame):
        # we want our index to be numbered
        df = pd.DataFrame(data.values)
    else:
        df = pd.DataFrame(data)
    df.index.name = index_name
    df.columns.name = columns_name
    return df


def _series_with_name(data, name):
    if isinstance(data, pd.Series):
        data.name = name
        # ensures a numeric index
        return data.reset_index()[name]
    else:
        return pd.Series(data, name=name)


def _topic_coordinates(mds, topic_term_dists, topic_proportion):
    K = topic_term_dists.shape[0]
    mds_res = mds(topic_term_dists)
    assert mds_res.shape == (K, 2)
    mds_df = pd.DataFrame({'x': mds_res[:, 0], 'y': mds_res[:, 1], 'topics': range(1, K + 1), \
                            'cluster': 1, 'Freq': topic_proportion * 100})
    # note: cluster (should?) be deprecated soon. See: https://github.com/cpsievert/LDAvis/issues/26
    return mds_df


def get_topic_coordinates(topic_term_dists, doc_topic_dists, doc_lengths, \
            vocab, term_frequency, mds=js_PCoA, sort_topics=True):
    """Transform the topic model distributions and related corpus.

    Creates the data structures needed for topic bubbles.

    Parameters
    ----------
    topic_term_dists : array-like, shape (`n_topics`, `n_terms`)
        Matrix of topic-term probabilities. Where `n_terms`
        is `len(vocab)`.
    doc_topic_dists : array-like, shape (`n_docs`, `n_topics`)
        Matrix of document-topic probabilities.
    doc_lengths : array-like, shape `n_docs`
        The length of each document, i.e. the number of words
        in each document. The order of the numbers should be
        consistent with the ordering of the docs in `doc_topic_dists`.
    vocab : array-like, shape `n_terms`
        List of all the words in the corpus used to train the model.
    term_frequency : array-like, shape `n_terms`
        The count of each particular term over the entire corpus.
        The ordering of these counts should correspond with
        `vocab` and `topic_term_dists`.
    mds : function or a string representation of function
        A function that takes `topic_term_dists` as an input and
        outputs a `n_topics` by `2`  distance matrix. The output
        approximates the distance between topics. See :func:`js_PCoA`
        for details on the default function. A string representation
        currently accepts `pcoa` (or upper case variant), `mmds`
        (or upper case variant) and `tsne` (or upper case variant),
        if `sklearn` package is installed for the latter two.
    sort_topics : sort topics by topic proportion (percentage of
        tokens covered). Set to False to to keep original topic order.

    Returns
    -------
    topic_coordinates : A pandas dataframe containing
        scaled x and y coordinates.

    """
    # parse mds
    if isinstance(mds, basestring):
        mds = mds.lower()
        if mds == 'pcoa':
            mds = js_PCoA
        elif mds in ('mmds', 'tsne'):
            if sklearn_present:
                mds_opts = {'mmds': js_MMDS, 'tsne': js_TSNE}
                mds = mds_opts[mds]
            else:
                logging.warning('sklearn not present, switch to PCoA')
                mds = js_PCoA
        else:
            logging.warning('Unknown mds `%s`, switch to PCoA' % mds)
            mds = js_PCoA

    topic_term_dists = _df_with_names(topic_term_dists, 'topic', 'term')
    doc_topic_dists = _df_with_names(doc_topic_dists, 'doc', 'topic')
    term_frequency = _series_with_name(term_frequency, 'term_frequency')
    doc_lengths = _series_with_name(doc_lengths, 'doc_length')
    vocab = _series_with_name(vocab, 'vocab')
    _input_validate(topic_term_dists, doc_topic_dists, doc_lengths, vocab, term_frequency)

    topic_freq = (doc_topic_dists.T * doc_lengths).T.sum()
    if sort_topics:
        topic_proportion = (topic_freq / topic_freq.sum()).sort_values(ascending=False)
    else:
        topic_proportion = (topic_freq / topic_freq.sum())

    topic_order = topic_proportion.index
    topic_term_dists = topic_term_dists.iloc[topic_order]

    scaled_coordinates = _topic_coordinates(mds, topic_term_dists, topic_proportion)

    return scaled_coordinates


def extract_params(statefile):
    """Extract the alpha and beta values from the statefile.

    Parameters:
    - statefile (str): Path to statefile produced by MALLET.
    
    Returns:
    - tuple: alpha (list), beta
    """
    with gzip.open(statefile, 'r') as state:
        params = [x.decode('utf8').strip() for x in state.readlines()[1:3]]
    return (list(params[0].split(":")[1].split(" ")), float(params[1].split(":")[1]))


def state_to_df(statefile):
    """Transform state file into pandas dataframe.

    The MALLET statefile is tab-separated, and the first two rows contain the alpha and beta hypterparamters.

    Parameters:
    - statefile (str): Path to statefile produced by MALLET.
    
    Returns:
    - datframe: topic assignment for each token in each document of the model.
    """
    return pd.read_csv(statefile,
                        compression='gzip',
                        sep=' ',
                        skiprows=[1, 2]
                        )


def pivot_and_smooth(df, smooth_value, rows_variable, cols_variable, values_variable):
    """Turn the pandas dataframe into a data matrix.

    Parameters:
    - df (dataframe): aggregated dataframe
    - smooth_value (float): value to add to the matrix to account for the priors
    - rows_variable (str): name of dataframe column to use as the rows in the matrix
    - cols_variable (str): name of dataframe column to use as the columns in the matrix
    - values_variable(str): name of the dataframe column to use as the values in the matrix
    
    Returns:
    - dataframe: pandas matrix that has been normalized on the rows.
    """
    matrix = df.pivot(index=rows_variable, columns=cols_variable, values=values_variable).fillna(value=0)
    matrix = matrix.values + smooth_value

    normed = sklearn.preprocessing.normalize(matrix, norm='l1', axis=1)

    return pd.DataFrame(normed)


def convert_mallet_data(state_file):
    """Convert Mallet data to a structure compatible with pyLDAvis.

    Parameters:
    - output_state_file (string): Mallet state file

    Returns:
    - data: dict containing pandas dataframes for the pyLDAvis prepare method.
    """
    params = extract_params(state_file)
    alpha = [float(x) for x in params[0][1:]]
    beta = params[1]
    df = state_to_df(state_file)
    # Ensure that NaN is a string
    df['type'] = df.type.astype(str)
    # Get document lengths from statefile
    docs = df.groupby('#doc')['type'].count().reset_index(name='doc_length')
    # Get vocab and term frequencies from statefile
    vocab = df['type'].value_counts().reset_index()
    vocab.columns = ['type', 'term_freq']
    vocab = vocab.sort_values(by='type', ascending=True)
    phi_df = df.groupby(['topic', 'type'])['type'].count().reset_index(name='token_count')
    phi_df = phi_df.sort_values(by='type', ascending=True)
    phi = pivot_and_smooth(phi_df, beta, 'topic', 'type', 'token_count')
    theta_df = df.groupby(['#doc', 'topic'])['topic'].count().reset_index(name='topic_count')
    theta = pivot_and_smooth(theta_df, alpha, '#doc', 'topic', 'topic_count')
    data = {'topic_term_dists': phi,
            'doc_topic_dists': theta,
            'doc_lengths': list(docs['doc_length']),
            'vocab': list(vocab['type']),
            'term_frequency': list(vocab['term_freq'])
        }
    return data

def get_model_vars(models, model_dir):
    """Method for getting model_vars if a Mallet object does not exist.
    
    Parameters:
    - models (list): A list of model numbers
    - model_dir (str): Path to the directory containing the models
    
    Returns:
    - model_vars (dict): A dict containing the model numbers and the names of their output_state files
    """
    model_vars = {}
    for topic_num in models:
        topic_num = str(topic_num)
        subdir = model_dir + '/topics' + topic_num
        model_vars[topic_num] = {'model_state': 'topic-state' +topic_num + '.gz'}
    return model_vars

def scale(models, model_dir):
    """Iterate through the models and generated topic_scaled.csv files.
    
    Parameters:
    - models (list): A list of model numbers
    - model_dir (str): Path to the directory containing the models    
    """
    timer = Timer()
    for topic_num, metadata in models.items():
        # Progress monitor
        print('Processing topics' + topic_num + '...')
        # Define file paths
        model_state_path = model_dir + '/topics' + topic_num + '/' + metadata['model_state']
        topic_scaled_path = model_dir + '/topics' + topic_num + '/topic_scaled.csv'
        # Convert the mallet output_state file to a pyLDAvis data object
        converted_data = convert_mallet_data(model_state_path)
        # Get the topic coordinates in a dataframe
        topic_coordinates = get_topic_coordinates(**converted_data)
        # Save the topic coordinates to a CSV file
        topic_coordinates.to_csv(topic_scaled_path, index=False, header=False)
    display(HTML('<h4>Done!</h4>'))
    print('Time elapsed: %s' % timer.get_time_elapsed())
