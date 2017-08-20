####
# Author: Robert Eichler
####

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

#def write_clusters(db_clusters):
#    i = 0
#    for cluster in db_clusters:
#
#        filep = codecs.open("result/" + str(i) + ".txt", "w" "utf-8")
#        i = i + 1
#        map(filep.write, cluster)
#        filep.close()

"""
Inserts cluster into database

Parameters
----------

db_clusters :: array
    Containing arrays of assingned apps for each cluster

"""
def write_clusters(db_clusters):
    print("write clusters...")

    mariadb_connection = mariadb.connect(user='putter', password='total_safety', database='privacy_ranking')
    dbcursor = mariadb_connection.cursor()

    dbcursor.execute("DELETE FROM App_in_cluster;")
    dbcursor.execute("DELETE FROM Clusters;")

    #dbcursor.execute("select Apps.title_en, Apps.description from Apps")

    for i, cluster in enumerate(db_clusters):
        print("cat %d length: %d" % (i, len(cluster)))

        dbcursor.execute("INSERT INTO Clusters (Cluster_id, name)\
                            VALUES (%s, %s);",
                            (i, "Cat " + unicode(i)));
        for app in cluster:
            #print("app in cluster %d", i)
            dbcursor.execute("INSERT INTO App_in_cluster (App_id, cluster_id, similarity)\
                                VALUES (%s,%s,%s)",
                                (app, i, 1))

    mariadb_connection.commit()
    mariadb_connection.close()
    print("end write")


"""
Runs the DBSCAN algorithm on the given data

Parameters
----------

dataset :: array
    Containing app data

app_ids :: array
    Containing the IDs from dataset

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
def run_dbscan(dataset, app_ids, X, eps=0.5, min_samples=5, metric='euclidean', algorithm='auto'):
    db = DBSCAN(eps=eps, min_samples=min_samples, metric=metric, algorithm=algorithm)
    #print(db)
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
            cmembers.append(app_ids[cmem_id].encode('utf-8'))
        db_clusters.append(cmembers)

    counter = 0
    for i in range(len(db_clusters)):
        counter += len(db_clusters[i])

    write_clusters(db_clusters)

    return (n_clusters, counter)


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
    #labels = dataset.target
    #true_k = np.unique(labels).shape[0]

    n_features = 1500

    #print(labels)
    #print(true_k)

    #print("extracting features:")

    #t0 = time()

    vectorizer = TfidfVectorizer(max_df=max_df, max_features=n_features,
                                    min_df=min_df, stop_words='english',
                                    use_idf=True,
                                    strip_accents='unicode')
    print(vectorizer)
    X = vectorizer.fit_transform(dataset)
    print(vectorizer.get_feature_names())
    return X


print("loading dataset")
#fp = codecs.open("dataset.txt", "r", "utf-8")
#dataset = fp.readlines()

mariadb_connection = mariadb.connect(user='getter', password='total_safety', database='privacy_ranking')
dbcursor = mariadb_connection.cursor()
dbcursor.execute("select Apps.App_id, Apps.title_en, Apps.description from Apps limit 0, 20000;")

dataset = []
app_ids = []

for app_id, title, description in dbcursor:
    app_ids.append(app_id)
    dataset.append(title + " " + description.replace("<br>","").replace("<b>","").replace("</b>",""))

mariadb_connection.close()


doc_count = len(dataset)
print("%d documents loaded" % doc_count)

X = run_tfidf(dataset, max_df=0.01, min_df=0.005)

result = run_dbscan(dataset, app_ids, X, eps=0.45, min_samples=30,
                        metric='cosine', algorithm='brute')

print(result)

#max 0.1
#min 0.001
#eps 0.45
#samples 30
#features 3000
