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

def run_tfidf(dataset, max_df=0.5, min_df=2):
    #labels = dataset.target
    #true_k = np.unique(labels).shape[0]

    n_features = 100

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

min_dfs = []
epss = []
loss = []
nofc = []

for eps in range(1, 11):
    eps = eps/10.0
    for miny in range(0, 42):
        #miny = miny/10.0
        X = run_tfidf(dataset, max_df=0.1, min_df=miny)

        result = run_dbscan(dataset, X, eps=eps, min_samples=5,
                                metric='cosine', algorithm='brute')

        print(result)
        min_dfs.append(miny)
        epss.append(eps)
        loss.append(doc_count - result[1])
        nofc.append(result[0])
        print(doc_count - result[1])

import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import axes3d

fig = plt.figure()
ax = fig.gca(projection='3d')

#surf = ax.plot(epss, mins, loss, cmap=cm.coolwarm,
#                linewidth=0, antialiased=False)

ax.plot_trisurf(min_dfs, epss, loss, cmap=cm.coolwarm)

ax.set_xlabel('min_dfs')
ax.set_ylabel('eps')
ax.set_zlabel('document loss')

#fig.colorbar(surf, shrink=0.5, aspect=5)
#plt.show()


###### bild 2


fig = plt.figure()
ax = fig.gca(projection='3d')

#surf = ax.plot(epss, mins, loss, cmap=cm.coolwarm,
#                linewidth=0, antialiased=False)

ax.plot_trisurf(min_dfs, epss, nofc, cmap=cm.coolwarm)

ax.set_xlabel('min_dfs')
ax.set_ylabel('eps')
ax.set_zlabel('n clusters')

#fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()
