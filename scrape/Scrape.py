####
# Author: Robert Eichler
####

import ScraPlay

import traceback

import mysql.connector as mariadb
from mysql.connector import IntegrityError
from textblob import TextBlob

# Read "other permissions" and create dictionary
# We only have permission names in german from google result not IDs
o_permissions = dict()
mariadb_connection = mariadb.connect(user='getter', password='total_safety', database='privacy_ranking')
dbcursor = mariadb_connection.cursor()
dbcursor.execute("select Permission_id, name from Permissions where Permission_id >= 1000;")

for perm_id, name in dbcursor:
    o_permissions[name] = perm_id

mariadb_connection.close()

"""
Insert new developer into database

Parameters
----------

data :: JSON-Array
    GooglePlay Data

dbcursor :: cursor
    Database cursor

"""
def add_developer(data, dbcursor):
    dev = ScraPlay.extract_developer(data)
    try:
        dbcursor.execute("INSERT INTO Developers (Developer_id, name)\
                            VALUES (%s, %s);",
                            (dev["dev_id"], dev["name"]))
    except IntegrityError:
        pass

    return dev["dev_id"]

"""
Insert new category into database

Parameters
----------

data :: JSON-Array
    GooglePlay Data

dbcursor :: cursor
    Database cursor

"""
def add_category(data, dbcursor):
    cat = ScraPlay.extract_category(data)
    try:
        dbcursor.execute("INSERT INTO Categories (Category_id, name)\
                        VALUES (%s, %s);",
                        (cat["cat_id"], cat["name"]))
    except IntegrityError:
        pass

    return cat["cat_id"]

"""
Insert new app into database

Parameters
----------

app_id :: int

data :: JSON-Array
    GooglePlay Data

dbcursor :: cursor
    Database cursor

"""
def add_app(app_id, data, dbcursor):
    title = ScraPlay.extract_title(data)
    developer_id = ScraPlay.extract_developer(data)["dev_id"]
    description = ScraPlay.extract_description(data)
    short_description = ScraPlay.extract_description_short(data)
    rating = ScraPlay.extract_rating(data)
    downloads_min = ScraPlay.extract_download_count_min(data)
    downloads_max = ScraPlay.extract_download_count_max(data)
    reviews = ScraPlay.extract_review_count(data)
    cost = ScraPlay.extract_cost(data)
    icon = ScraPlay.extract_icon(data)["url"]
    category = ScraPlay.extract_category(data)["cat_id"]
    version = ScraPlay.extract_version(data)
    min_android = ScraPlay.extract_android_min_version(data)
    changelog = ScraPlay.extract_changelog(data)

    title_en = title

    try:
        title_en = unicode(TextBlob(title).translate(to="en"))
    except:
        pass

    try:
        description = unicode(TextBlob(description).translate(to="en"))
    except Exception:
        traceback.print_exc()
        pass

    try:
        dbcursor.execute("INSERT INTO Apps (App_id, title, title_en, developer_id, description,\
                                            short_description, rating, min_downloads,\
                                            max_downloads, reviews, cost, currency, icon,\
                                            app_category, version, min_android, changelog)\
                        VALUES (%s, %s, %s, %s, %s,\
                                %s, %s, %s,\
                                %s, %s, %s, %s, %s,\
                                %s, %s, %s, %s);",
                        (app_id, title, title_en, developer_id, description,
                            short_description, rating, downloads_min,
                            downloads_max, reviews, cost["cost"], cost["currency"], icon,
                            category, version, min_android, changelog)
                        )
    except IntegrityError:
        traceback.print_exc()
        #exit()
        pass

"""
Insert new images into database

Parameters
----------

app_id :: int
    App ID to which the images belong

data :: JSON-Array
    GooglePlay Data

dbcursor :: cursor
    Database cursor

"""
def add_images(app_id, data, dbcursor):
    images = ScraPlay.extract_images(data)

    for img in images:
        try:
            dbcursor.execute("INSERT INTO Images (App_id, url)\
                                VALUES (%s, %s)",
                                (app_id, img["url"]))
        except IntegrityError:
            pass

"""
Insert new app permissions into database

Parameters
----------

app_id :: int
    App ID to which the permissions belong

data :: JSON-Array
    GooglePlay Data

dbcursor :: cursor
    Database cursor

"""
def add_permissions(app_id, data, dbcursor):
    permissions = ScraPlay.extract_permissions(data)

    for perm in permissions:
        try:
            dbcursor.execute("INSERT INTO App_permissions (App_id, Permission_id)\
                                VALUES (%s, %s);",
                                (app_id, perm))
        except IntegrityError:
            traceback.print_exc()
            #exit()
            pass

"""
Insert new other app permissions into database

Parameters
----------

app_id :: int
    App ID to which the permissions belong

data :: JSON-Array
    GooglePlay Data

dbcursor :: cursor
    Database cursor

"""
def add_other_permissions(app_id, data, dbcursor):
    permissions = ScraPlay.extract_permissions_other(data)

    for perm in permissions:
        # Check if permission is nown
        try:
            perm_id = o_permissions[perm]
        except KeyError: # if not, add it to database
            perm_id = len(o_permissions) + 1001
            dbcursor.execute("INSERT INTO Permissions (Permission_id, name)\
                                VALUES (%s, %s);",
                                (perm_id, perm))
            o_permissions[perm] = perm_id

        # Insert to App_permissions
        try:
            dbcursor.execute("INSERT INTO App_permissions (App_id, Permission_id)\
                                VALUES (%s, %s);",
                                (app_id, perm_id))
        except IntegrityError:
            pass

"""
Reads app IDs from file in folder URLs
Requests GooglePlay data for IDs

Parameters
----------

fileNumerb :: int
    Number of file (number in file name)

dbcursor :: cursor
    Database cursor

"""
def start(fileNumerb, dbcursor):
    print("start %s" % fileNumerb)

    with open('URLs/%s.txt' % fileNumerb) as file:
        url = file.readlines()
        for link in url:
            try:
                app_id = ScraPlay.extract_id(link)
                #app_id = "com.coliferlab.picasatool.lictwo"
                #app_id = "com.king.candycrushsaga"
                #app_id = "com.bimma.kerajinanbambu"
                #app_id = "com.mukicloud.proudpet"
                print(app_id)
                data = ScraPlay.request_app_data(app_id)

                if (len(data[0]) <= 2):
                    print("DEAD: %s" % app_id)
                    continue

                add_developer(data, dbcursor)
                add_category(data, dbcursor)

                add_app(app_id, data, dbcursor)

                add_images(app_id, data, dbcursor)

                add_permissions(app_id, data, dbcursor)
                add_other_permissions(app_id, data, dbcursor)

                #exit()
            except IntegrityError:
                break
            except:
                traceback.print_exc()
                exit()


mariadb_connection = mariadb.connect(user='putter', password='total_safety', database='privacy_ranking')
dbcursor = mariadb_connection.cursor()

start("80", dbcursor)
start("81", dbcursor)
start("82", dbcursor)


mariadb_connection.commit()
mariadb_connection.close()
