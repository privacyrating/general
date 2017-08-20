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
    classifier = KNeighborsClassifier(5).fit(assigned_X, labels)

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
    tmp = map(f, with_data)
    indices = np.where(tmp)[0]

    result = []
    # not beatiful but works...
    try:
        result = data[indices,:] # >= 2d array
    except:
        result = data[indices] # 1d array

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

    eps = 0.40

    # Reduce until all large clusters are eliminated
    # or a maximum iteration is reached
    reduced = 0
    count = counter = 0
    while reduced > -1:

        print("start")
        print(X.shape)
        print(app_ids.shape)
        print(len(labels))

        reduced = -1

        max_key = 0

        # Search for a large cluster
        # here I have to find a good qualifier in the near future
        max_value = 0
        for key in sizes:
            if (int(key) > max_key):
                max_key = int(key)

            if (sizes[key] > max_value):
                if (counter == 0):
                    count += 1
                if (sizes[key] > 1000):
                    reduced = int(key)
                    max_value = sizes[key]

        print(reduced)
        if (reduced == -1):
            break

        # Filter to large cluster
        f = lambda x: x != reduced
        tmp_X = reduce_data(X, labels, f)
        tmp_ids = reduce_data(app_ids, labels, f)
        tmp_labels = filter(f, labels)

        f = lambda x: x == reduced
        cluster_X = reduce_data(X, labels, f)
        cluster_ids = reduce_data(app_ids, labels, f)

        # Run DBSCAN with to large cluster
        if (counter == count):
            if (eps <= 0.35): #0.16
                break
            eps -= 0.05
            print("eps: ", eps)
            count = counter = 0
        else:
            counter += 1

        labels = run_dbscan(cluster_X, eps=0.40)

        clustersizes = collections.Counter(labels)

        # Filter assigned and not assigned apps
        f = lambda x: x > -1
        assigned_X = reduce_data(cluster_X, labels, f)
        assigned_ids = reduce_data(cluster_ids, labels, f)
        assigned_labels = map(lambda x: x + (max_key + 1),filter(f, labels))

        X = vstack([tmp_X, assigned_X])
        app_ids = np.append(tmp_ids, assigned_ids)
        tmp_labels.extend(assigned_labels)


        f = lambda x: x == -1
        not_assigned_X = reduce_data(cluster_X, labels, f)
        not_assigned_ids = reduce_data(cluster_ids, labels, f)

        labels = tmp_labels


        # Run classifier
        result = run_classifier(X, app_ids, labels, not_assigned_X, not_assigned_ids)


        # Merge all together
        X = vstack([X, not_assigned_X])
        app_ids = np.append(app_ids, not_assigned_ids)
        labels.extend(result)

        sizes = collections.Counter(labels)

        print(X.shape)
        print(app_ids.shape)
        print(len(labels))

        print("eps: ", eps)
        print("count: ", count)
        print("counter: ", counter)
        print(sizes)

        print(reduced)
        print(max_value)

        #reduced = -1

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

    print("labels: ", d)
    print("l: ", l)

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

labels = run_dbscan(X, eps=0.45)

# Filter assigned and not assigned apps
f = lambda x: x > -1
assigned_ids = reduce_data(np.array(app_ids), labels, f)
assigned_X = reduce_data(X, labels, f)
assigned_labels = filter(f, labels)


f = lambda x: x == -1
not_assigned_ids = reduce_data(np.array(app_ids), labels, f)
not_assigned_X = reduce_data(X, labels, f)

# Assign the noise
result = run_classifier(assigned_X, assigned_ids, assigned_labels, not_assigned_X, not_assigned_ids)

assigned_X = vstack([assigned_X, not_assigned_X])
assigned_ids = np.append(assigned_ids, not_assigned_ids)
assigned_labels.extend(result)

# Eliminate to large clusters
(X, app_ids, labels) = reduce_clusters(assigned_X, assigned_ids, assigned_labels)

labels = rename_labels(labels)

# Insert into database
db_connection.set_clustering_id(6)
db_connection.add_clusters(np.unique(labels))
db_connection.add_app_to_cluster(app_ids, labels)
