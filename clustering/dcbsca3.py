####
# Author: Robert Eichler
####

import db_connection

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN

from sklearn.neighbors import KNeighborsClassifier

import numpy as np
import pandas as pd

from scipy.sparse import vstack, hstack

import collections

"""
Load app data from database

Parameters
----------

limit :: int

Returns
-------
(dataset, app_ids) :: (array, array)

"""
def load_dataset(limit = 20000):
    mariadb_connection = db_connection.connect_getter()
    dbcursor = mariadb_connection.cursor()
    dbcursor.execute("SELECT Apps.App_id, Apps.title_en, Apps.description from Apps limit 0,%s", (limit,))

    dataset = []
    app_ids = []

    for app_id, title, description in dbcursor:
        app_ids.append(app_id)
        dataset.append(title + " " + description.replace("<br>","").replace("<b>","").replace("</b>",""))

    mariadb_connection.close()

    return (dataset, app_ids)

"""
Runs the TF-IDF feature extraction on the given dataset

Parameters
----------

dataset :: array
    Containing app data

max_df :: float or int

min_df :: float or int

see http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html

Returns
-------
features :: array-like or sparse matrix

"""
def run_tfidf(dataset, max_df=0.5, min_df=2):
    n_features = 1500
    #n_features = 10000
    vectorizer = TfidfVectorizer(max_df=max_df, max_features=n_features,
                                    min_df=min_df, stop_words='english',
                                    use_idf=True,
                                    strip_accents='unicode')
    #print(vectorizer)
    X = vectorizer.fit_transform(dataset)
    #print(vectorizer.get_feature_names())
    return X

"""
Runs the DBSCAN algorithm on the given data

Parameters
----------

X :: array-like or sparse matrix, shape=(n_samples, n_features)
    Training instances to cluster

eps :: float

min-samples :: int

metric :: String or None

algorithm :: string

see http://scikit-learn.org/stable/modules/generated/sklearn.cluster.dbscan.html

Returns
-------

labels :: array

"""
def run_dbscan(X, eps=0.5, min_samples=30, metric='cosine', algorithm='brute'):
    db = DBSCAN(eps=eps, min_samples=min_samples, metric=metric, algorithm=algorithm)

    db = db.fit(X)

    return db.labels_

"""
Fits the classifier with the given clusters and predicts the noise

Parameters
----------

assigned_X :: array-like or spares matrix, shape=(n_samples, n_features)
    Training instances to cluster

assagned_ids :: array
    List of assigned app IDs

labels :: array
    List of assigned labes of assigned apps

not_assigned_X :: array
    Training instances to cluster
    Not assigned apps

not_assigned_ids :: array
    List of not assigned app IDs

Returns
-------
labels :: array

Predicted labels for noise

"""
def run_classifier(assigned_X, assigned_ids, labels, not_assigned_X, not_assigned_ids):
    classifier = KNeighborsClassifier(5, metric="cosine", algorithm="brute").fit(assigned_X, labels)

    result = classifier.predict(not_assigned_X)

    return result

"""
Extract from array by given function and values for decision

data :: array
    Data to extract from

with_data :: array
    Data for decision to extract an indice or not

f :: function
    Function for decsision to extract an indice or not

Returns
-------
extracted :: array

"""
def reduce_data(data, with_data, f):
    #data = np.array(data)
    tmp = map(f, with_data)
    indices = np.where(tmp)[0]

    result = []
    # not beatiful but works...
    try:
        result = data[indices,:]
    except:
        result = data[indices]

    return result;

"""
Finds to large clusters then splits them up

Parameters
----------

X :: array-like or sparse matrix, shape=(n_samples, n_features)

app_ids :: array
    List of apps

labels :: array
    List of labels

"""
def reduce_clusters(X, app_ids, labels):

    sizes = collections.Counter(labels)

    # Reduce until all lagre clusters are eliminated
    # or eps is to small
    eps = 0.40
    reduced = True
    while reduced:

        reduced = False

        max_key = 0

        out_keys = []

        # Search for all lagre clusters
        # here I have to find a good qualifier in the near future (maybe)
        for key in sizes:
            if (int(key) > max_key):
                max_key = int(key)

            if (sizes[key] > 1000):
                reduced = True
                out_keys.append(int(key))

        if (not reduced):
            break

        print(out_keys)

        out_X = []
        out_ids = []

        # Filter to large clusters
        for key in out_keys:
            f = lambda x: x == key
            cluster_X = reduce_data(X, labels, f)
            cluster_ids = reduce_data(app_ids, labels, f)
            out_X.append(cluster_X)
            out_ids.append(cluster_ids)

            f = lambda x: x != key
            X = reduce_data(X, labels, f)
            app_ids = reduce_data(app_ids, labels, f)
            labels = filter(f, labels)

        not_X = None
        not_ids = []

        # For each large cluster run DBSCAN again with smaller eps
        for i in range(len(out_X)):
            labs = run_dbscan(out_X[i], eps=eps)

            # Filter assigned apps
            f = lambda x: x > -1
            assigned_X = reduce_data(out_X[i], labs, f)
            assigned_ids = reduce_data(out_ids[i], labs, f)
            assigned_labels = map(lambda x: x + (max_key + 1), filter(f, labs))
            max_key += len(np.unique(assigned_labels))

            # Add assiged apps back
            X = vstack([X, assigned_X])
            app_ids = np.append(app_ids, assigned_ids)
            labels.extend(assigned_labels)

            # Filter not assigned apps
            f = lambda x: x == -1
            not_assigned_X = reduce_data(out_X[i], labs, f)
            not_assigned_ids = reduce_data(out_ids[i], labs, f)
            #not_X.extend(not_assigned_X)
            if (not_X == None):
                not_X = not_assigned_X
            else:
                not_X = vstack([not_X, not_assigned_X])

            not_ids.extend(not_assigned_ids)

        # Here I try to make the noise to a new large cluster to split them
        # up next time if needed
        result = [-1 for x in range(not_X.shape[0])]


        # Merge all together
        X = vstack([X, not_X])
        app_ids = np.append(app_ids, not_ids)
        labels.extend(result)

        print(not_X.shape)


        sizes = collections.Counter(labels)

        if (eps >= 0.9):
            break
        print(eps)
        #eps -= 0.05
        eps += 0.05

    return (X, app_ids, labels)

"""
Since we use in our app the position of the category at the categories page,
we need to have cluster ids start at 0 with no gaps

Through the elimination of to large clusters gaps turn up

Parameters
----------

labels :: array
    Cluster labels

Returns
-------
labels :: array

"""
def rename_labels(labels):
    d = collections.Counter(labels)
    l = []
    for key in d:
        l.append(key)

    l = sorted(l)
    new = dict()
    for i, label in enumerate(l):
        new[label] = i

    labels_new = []
    for label in labels:
        labels_new.append(new[label])

    return labels_new

# Load dataset
(dataset, app_ids) = load_dataset()

doc_count = len(dataset)
print("%d documents loaded" % doc_count)

X = run_tfidf(dataset, max_df=0.01, min_df=0.005)
#X = run_tfidf(dataset, max_df=3, min_df=1)

labels = run_dbscan(X, eps=0.45)

# Filter assigned and not assigned apps
f = lambda x: x > -1
assigned_ids = reduce_data(np.array(app_ids), labels, f)
assigned_X = reduce_data(X, labels, f)
assigned_labels = filter(f, labels)

f = lambda x: x == -1
not_assigned_ids = reduce_data(np.array(app_ids), labels, f)
not_assigned_X = reduce_data(X, labels, f)

result = run_classifier(assigned_X, assigned_ids, assigned_labels, not_assigned_X, not_assigned_ids)

assigned_X = vstack([assigned_X, not_assigned_X])
assigned_ids = np.append(assigned_ids, not_assigned_ids)
assigned_labels.extend(result)

# Assign the noise
(X, app_ids, labels) = reduce_clusters(assigned_X, assigned_ids, assigned_labels)

labels = rename_labels(labels)

# Insert into database
db_connection.set_clustering_id(8)
db_connection.add_clusters(np.unique(labels))
db_connection.add_app_to_cluster(app_ids, labels)
