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

def write_clusters(db_clusters):
    i = 0
    for cluster in db_clusters:

        filep = codecs.open("result/" + str(i) + ".txt", "w" "utf-8")
        i = i + 1
        map(filep.write, cluster)
        filep.close()

def run_dbscan(dataset, X, eps=0.5, min_samples=5, metric='euclidean', algorithm='auto'):
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
            cmembers.append(dataset[cmem_id].encode('utf-8'))
        db_clusters.append(cmembers)

    counter = 0
    for i in range(len(db_clusters)):
        counter += len(db_clusters[i])

    write_clusters(db_clusters)

    return (n_clusters, counter)

def run_tfidf(dataset, max_df=0.5, min_df=2):
    #labels = dataset.target
    #true_k = np.unique(labels).shape[0]

    n_features = 100000

    #print(labels)
    #print(true_k)

    #print("extracting features:")

    #t0 = time()

    vectorizer = TfidfVectorizer(max_df=max_df, max_features=n_features,
                                    min_df=min_df, stop_words='english',
                                    use_idf=True)
    print(vectorizer)
    X = vectorizer.fit_transform(dataset)
    return X


print("loading dataset")
fp = codecs.open("dataset.txt", "r", "utf-8")

dataset = fp.readlines()

doc_count = len(dataset)
print("%d documents loaded" % doc_count)

X = run_tfidf(dataset, max_df=0.1, min_df=23)

result = run_dbscan(dataset, X, eps=0.4, min_samples=5,
                        metric='cosine', algorithm='brute')

fp.close()

print(result)


