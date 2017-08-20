####
# Author: Robert Eichler
####

# Combinding clusters from dbscan with classifier
# and
# combinding number clusters from dbscan with kmeans
# and
# number of google categories with kmeans

import db_connection

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans

from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import AdaBoostClassifier

import numpy as np
import pandas as pd

import collections

"""
Fits the classifier with the given clusters and predicts the noise
Then inserting cluster into database

Parameters
----------

assigned :: array-like or sparse matrix, shape=(n_samples, n_features)
    Training instances to cluster
    Assigned apps

assigned_ids :: array
    List of assigned app IDs

assigned_clusters :: array
    List of assigned labels of assigned apps

na_X :: array-like or sparse matrix, shape=(n_samples, n_features)
    Training instances to cluster
    Not assigned apps

na_app_ids :: array
    List of not assigned app IDs

"""
def run_classifier(assigned, assigned_ids, assigned_clusters, na_X, na_app_ids):

    #classifier = DecisionTreeClassifier()
    classifier = KNeighborsClassifier(5)
    #classifier = BernoulliNB(alpha=1.0, binarize=0.5)
    #classifier = MLPClassifier(alpha=1)
    #classifier = AdaBoostClassifier()

    classifier.fit(assigned, np.asarray(assigned_clusters))

    result = classifier.predict(na_X)

    #foo = collections.Counter(result)

    db_connection.add_clusters(np.unique(assigned_clusters))
    db_connection.add_app_to_cluster(assigned_ids, assigned_clusters)
    db_connection.add_app_to_cluster(na_app_ids, result)


"""
Runs K-Means on the given dataset
Then inserting cluster into database

Parameters
----------

dataset :: array
    Containing app data

app_ids :: array
    Containing the ids from dataset

X :: array-like or spares matrix, shape=(n_samples, n_features)
    Training instances to cluster

n_cluster :: int
    Number of clusters

"""
def run_kmeans(dataset, app_ids, X, n_clusters):
    km = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=100, n_init=1,
                    verbose=False);

    result = km.fit(X)

    db_connection.add_clusters(np.unique(result.labels_))
    db_connection.add_app_to_cluster(app_ids, result.labels_)

"""
Runs DBSCAN on the given data

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

(assigned, assigned_ids, assigned_clusters, na_X, na_app_ids)
    :: (array-like or sparse matrix, array, array, array-like or sparse matrix, array)

assigned: features of assigned apps
assigned_ids: IDs of assigned apps
assigned_clusters: ID of cluster for every assigned app
na_X: features of not assigned apps
na_app_ids: IDs of not assigned apps

"""
def run_dbscan(dataset, app_ids, X, eps=0.5, min_samples=5, metric='euclidean', algorithm='auto'):
    db = DBSCAN(eps=eps, min_samples=min_samples, metric=metric, algorithm=algorithm)

    print(app_ids[1])

    db = db.fit(X)
    cluster_labels = db.labels_
    n_clusters = len(set(db.labels_)) - (1 if -1 in cluster_labels else 0)

    clabels = np.unique(cluster_labels)

    not_assigned_docs = np.ones((len(dataset),), dtype=bool)

    assigned_docs = np.zeros((len(dataset),), dtype=bool)

    for i in range(clabels.shape[0]):
        if clabels[i] < 0:
            continue
        cmem_ids = np.where(cluster_labels == clabels[i])[0]

        for cmem_id in cmem_ids:
            assigned_docs[cmem_ids] = True
            not_assigned_docs[cmem_ids] = False

    assigned_clusters = filter(lambda x: x>-1, cluster_labels)

    indices = np.where(assigned_docs)[0]
    assigned = X[indices,:]

    bar = np.array(app_ids)

    assigned_ids = bar[assigned_docs]
    print(assigned_ids[1])

    print(assigned.shape[0])
    print(len(assigned_ids))
    print(len(assigned_clusters))

    na_app_ids = bar[not_assigned_docs]

    indices = np.where(not_assigned_docs)[0]
    na_X = X[indices,:]

    return (assigned, assigned_ids, assigned_clusters, na_X, na_app_ids)

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
    X = vectorizer.fit_transform(dataset)
    return X


print("loading dataset")

mariadb_connection = db_connection.connect_getter()
dbcursor = mariadb_connection.cursor()
dbcursor.execute("select Apps.App_id, Apps.title_en, Apps.description from Apps limit 0,20000;")

dataset = []
app_ids = []

for app_id, title, description in dbcursor:
    app_ids.append(app_id)
    dataset.append(title + " " + description.replace("<br>","").replace("<b>","").replace("</b>",""))


dbcursor.execute("SELECT COUNT(Category_id) AS CNT FROM Categories;")

n_categories = dbcursor.fetchone()[0]

mariadb_connection.close()

print(app_ids[1])


doc_count = len(dataset)
print("%d documents loaded" % doc_count)

X = run_tfidf(dataset, max_df=0.01, min_df=0.005)
#X = run_tfidf(dataset, max_df=0.05, min_df=0.03)

#0.30
(assigned, assigned_ids, assigned_clusters, na_X, na_app_ids) = run_dbscan(dataset, app_ids, X, eps=0.45, min_samples=30,
                                                                    metric='cosine', algorithm='brute')

#exit()
# First clustering
db_connection.set_clustering_id(0) #3
run_classifier(assigned, assigned_ids, assigned_clusters, na_X, na_app_ids)

# Second clustering
db_connection.set_clustering_id(1) #4
run_kmeans(dataset, app_ids, X, len(np.unique(assigned_clusters)))

# Third clustering
db_connection.set_clustering_id(2) #5
run_kmeans(dataset, app_ids, X, n_categories)
