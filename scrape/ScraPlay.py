####
# Author: Robert Eichler
####

# Python module ScraPlay
# for scraping Google Play app data

# Good to know
# title: [0][2][0][8]
# description: [0][2][0][9] or [0][2][0][41]
# reviews: [0][2][0][22]
# rating: [0][2][0][23] or [0][2][0][16]
# permissions: [0][2][0][65]["42656262"][1] ==> incomplete!!!
#   [0][2][0][65]["42656262"][1][0]
#   [0][2][0][65]["42656262"][1][0][x][0]
#   [0][2][0][65]["42656262"][1][0][x][1][0][0]
# permission-ids: [0][2][0][65]["42656262"][1][0][x][2]
# permissions: [0][2][0][65]["42656262"][23] ==> comlete!!!
# permission-ids: [0][2][0][65]["42656262"][23][0][x][2]
# other permissions: [0][2][0][65]["42656262"][23][1] and [0][2][0][65]["42656262"][23][2]
# min-downloads: [0][2][0][65]["42656262"][5]
# max-downloads: [0][2][0][65]["42656262"][6]


# Also interesting
# costs: [0][2][0][13]
# images: [0][2][0][11] # '[4, ' => app icon
# category: [0][2][0][14]
# short description: [0][2][0][57]
# developer: [0][2][0][65]["42656262"][0]
# version: [0][2][0][65]["42656262"][7]
# min-android: [0][2][0][65]["42656262"][9]
# changelog: [0][2][0][65]["42656262"][11]

import json
import requests
import re

# hope this will not change...
htwnc = "42656262"

# https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python

"""
Remove all emoji from given text

Parameters
----------

text :: string

Returns
-------
text :: string

"""
def _remove_emojis(text):
    emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text) # no emoji


"""
Extracts image data from given JSON-Array

Parameters
----------

image :: JSON-Array

Returns
-------
data :: dict(type :: int, url :: string)

"""
def _extract_image_data(image):
    data = data = dict(type=image[0],
                        url=image[4])
    return data

"""
Extracts app title from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
title :: string

"""
def extract_title(data):
    return _remove_emojis(data[0][2][0][8])

"""
Extracts app description from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
description :: string

"""
def extract_description(data):
    return _remove_emojis(data[0][2][0][9])

"""
Extracts short app description from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
description :: string

"""
def extract_description_short(data):
    descr = data[0][2][0][57]
    descr = "No short description" if descr == None else descr
    return _remove_emojis(descr)

"""
Extracts count of reviews from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
count :: int

"""
def extract_review_count(data):
    return data[0][2][0][22]

"""
Extracts app rating from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
rating :: float

"""
def extract_rating(data):
    return data[0][2][0][23]

"""
Extracts app exact rating from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
rating :: float

"""
def extract_rating_exact(data):
    return data[0][2][0][16]

"""
Extracts app permissions from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
permissions :: array

"""
def extract_permissions(data):
    l = []

    permissions = data[0][2][0][65][htwnc][23][0]

    for permission in permissions:
        #l.append(permission[1][0][0])
        l.append(str(permission[2]))

    return l

"""
Extracts other app permissions from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
permissions :: array

"""
def extract_permissions_other(data):
    l = []

    permissions = data[0][2][0][65]["42656262"][23][1][0][1]

    for permission in permissions:
        l.append(permission[0])

    permissions = data[0][2][0][65]["42656262"][23][2]

    for permission in permissions:
        l.append(permission[0])

    return l

"""
Extracts minimum download count from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
count :: int

"""
def extract_download_count_min(data):
    count =  data[0][2][0][65][htwnc][5]
    count = 0 if count == None else count
    return count

"""
Extracts maximum download count from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
count :: int

"""
def extract_download_count_max(data):
    count = data[0][2][0][65][htwnc][6]
    count = 0 if count == None else count
    return count

"""
Extracts cost for app from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
cost :: int

"""
def extract_cost(data):
    currency = data[0][2][0][13][0][33]
    cost = data[0][2][0][13][0][34]
    c = dict(currency = currency,
                cost = cost)

    return c

"""
Extracts app icon from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
imgdata :: Dict(type :: int, url :: string)

"""
def extract_icon(data):

    images = data[0][2][0][11]

    images = filter(lambda x: x[0] == 4, images)

    img = images[0]

    imgdata = _extract_image_data(img)

    return imgdata

"""
Extracts app icon from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
images :: array{Dict(type :: int, url :: string)}

"""
def extract_images(data):

    images = data[0][2][0][11]

    images = filter(lambda x: x[0] != 4, images)

    l = []

    for img in images:
        l.append(_extract_image_data(img))

    return l

"""
Extracts category ID from given string

Parameters
----------

s :: string
    Containing category ID

Returns
-------
id :: int

"""
def _extract_cat_id(s):
    m = re.search('category\/(.*)$', s)
    return m.group(1)

"""
Extracts app category from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
category :: Dict(cat_id :: int, name :: string)

"""
def extract_category(data):
    cat = dict(cat_id = _extract_cat_id( data[0][2][0][14][0][1]),
                name = data[0][2][0][14][0][0])

    return cat

"""
Extracts developer ID from given string

Parameters
----------

s :: string
    Containing developer ID

Returns
-------
id :: string

"""
def _extract_dev_id(s):
    m = re.search('id=(.*)$', s)
    return m.group(1)

"""
Extracts app developer from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
developer :: Dict(dev_id :: string, name :: string)

"""
def extract_developer(data):

    dev = dict(dev_id = _extract_dev_id(data[0][2][0][65][htwnc][0][1]),
                name = data[0][2][0][65][htwnc][0][0])

    return dev

"""
Extracts app version from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
version :: string

"""
def extract_version(data):
    return data[0][2][0][65][htwnc][7]

"""
Extracts minimum required android version from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
version :: string

"""
def extract_android_min_version(data):
    return data[0][2][0][65][htwnc][9]

"""
Extracts app changelog from given GooglePlay data

Parameters
----------

data :: JSON-Array
    Data from GooglePlay

Returns
-------
changelog :: string

"""
def extract_changelog(data):
    return "\n".join(data[0][2][0][65][htwnc][11])

# https://play.google.com//store/apps/details?id=com.bimma.kerajinanbambu

"""
Extracts app ID from given string

Parameters
----------

s :: string
    URL which contains app ID

Returns
-------
id :: string

"""
def extract_id(s):
    m = re.search('(\w+\.[\w\.]+)$', s)
    return m.group(0)

"""
Sends post request to GooglePlay with given app ID

app_id :: string
    App to request

Returns
-------
data :: JSON-Array

"""
def request_app_data(app_id):
    url = 'https://play.google.com/store/xhr/getdoc?authuser=0'
    data = dict(ids=app_id, xhr=1)
    headers = {"accept-language": "en"} # google ignores this ._.

    r = requests.post(url, data=data, headers=headers, allow_redirects=False)
    r = json.loads(r.content[6:])
    return r
