####
# Author: Robert Eichler
####

# KAMA = Kombiniere alles mit allen
# (ENG: Combining everything with everything)
# This script was used to mine a good amount of features for DBSCAN

from __future__ import print_function

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.pipeline import make_pipeline

from sklearn.cluster import DBSCAN

import numpy as np
import pandas as pd

from time import time

import codecs

import mysql.connector as mariadb

"""
Runs the DBSCAN algorithm on the given data

Parameters
----------

dataset :: array
    Containing app data

X :: array-like or sparse matrix, shape=(n_samples, n_features)
    Training instances to cluster

eps :: float

min-samples :: int

metric :: String or None

algorithm :: string

see http://scikit-learn.org/stable/modules/generated/sklearn.cluster.dbscan.html

Returns
-------

(n_clusters, counter) :: (int, int)

"""
def run_dbscan(dataset, X, eps=0.5, min_samples=5, metric='euclidean', algorithm='auto'):
    db = DBSCAN(eps=eps, min_samples=min_samples, metric=metric, algorithm=algorithm)
    print(db)
    db = db.fit(X)
    cluster_labels = db.labels_
    n_clusters = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)

    clabels = np.unique(cluster_labels)

    db_clusters = []
    for i in range(clabels.shape[0]):
        if clabels[i] < 0:
            continue
        cmem_ids = np.where(cluster_labels == clabels[i])[0]
        cmembers = []
        for cmem_id in cmem_ids:
            cmembers.append(dataset[cmem_id])
        db_clusters.append(cmembers)

    counter = 0
    for i in range(len(db_clusters)):
        counter += len(db_clusters[i])

    return (n_clusters, counter)

"""
Runs the TF-IDF feature extraction on the given dataset

Parameters
----------

dataset :: array
    Containing app data

max_df :: float or int

min_df :: float or int

n_features :: int
    max number of features

see http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html

Returns
-------
features :: array-like or sparse matrix

"""
def run_tfidf(dataset, max_df=0.5, min_df=2, n_features = 100000):
    vectorizer = TfidfVectorizer(max_df=max_df, max_features=n_features,
                                    min_df=min_df, stop_words='english',
                                    use_idf=True)
    print(vectorizer)
    X = vectorizer.fit_transform(dataset)
    return X

features = []
apps = []
loss = []
nofc = []

# Combining everything
for app in range(1, 51): # 51

    app = 500 * app

    print("loading dataset")

    mariadb_connection = mariadb.connect(user='getter', password='total_safety', database='privacy_ranking')
    dbcursor = mariadb_connection.cursor()
    dbcursor.execute("select Apps.title_en, Apps.description from Apps limit 0, %s;", (app,) )

    dataset = []

    for title, description in dbcursor:
        dataset.append(title + " " + description)

    mariadb_connection.close()

    doc_count = len(dataset)
    print("%d documents loaded" % doc_count)

    for feature in range(1, 11):
        feature = 100 * feature
        X = run_tfidf(dataset, max_df=0.1, min_df=23, n_features = feature)

        result = run_dbscan(dataset, X, eps=0.4, min_samples=5,
                                metric='cosine', algorithm='brute')

        print(result)
        apps.append(app)
        features.append(feature)
        loss.append((doc_count - result[1]) * 100.0 / doc_count)
        nofc.append(result[0])
        print(doc_count - result[1])


print("finished")
print("plotting...")

# Plotting the results
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import axes3d

# Figure 1
fig = plt.figure()
ax = fig.gca(projection='3d')

# Logscale
ax.plot_trisurf(apps, np.log10(features), loss, cmap=cm.coolwarm)

ax.set_xlabel('n apps')
ax.set_ylabel('n features')
yticks = [10**0, 10**1, 10**2, 10**3, 10**4, 10**5, 10**6]
ax.set_yticks(np.log10(yticks))
ax.set_yticklabels(yticks)
ax.set_zlabel('document loss')

# Figure 2
fig = plt.figure()
ax = fig.gca(projection='3d')

# Logscale
ax.plot_trisurf(apps, np.log10(features), nofc, cmap=cm.coolwarm)

ax.set_xlabel('n apps')
ax.set_ylabel('n features')
yticks = [10**0, 10**1, 10**2, 10**3, 10**4, 10**5, 10**6]
ax.set_yticks(np.log10(yticks))
ax.set_yticklabels(yticks)
ax.set_zlabel('n clusters')

# Plotting
plt.show()
