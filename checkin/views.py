from __future__ import print_function

from pprint import pprint
from wsgiref import headers

from .models import Publics
from .forms import PublicsForm

import pandas as pd
import requests
from django.shortcuts import render
import os
import datetime
from dateutil.tz import tzutc
import json
import time
import numpy as np
import math
from tqdm import tqdm
from pprint import pprint

# for visualization
import plotly.graph_objs as go
import chart_studio.plotly as py
from plotly.subplots import make_subplots

# =======================================================================================
def get_timeseries(params, print_params=None, print_count=None):
    if print_params is None or print_params == 'yes':
        pprint(params)

    response = requests.get('https://api.aylien.com/news/time_series', params=params, headers=headers).json()

    if 'errors' in response or 'error' in response:
        pprint(response)

    # convert to dataframe
    timeseries_data = pd.DataFrame(response['time_series'])

    # convert back to datetime
    timeseries_data['published_at'] = pd.to_datetime(timeseries_data['published_at'])

    timeseries_data['published_at'] = timeseries_data['published_at'].dt.date

    if print_count is None or print_count == 'yes':
        print('Number of stories returned : ' + str(format(timeseries_data['count'].sum(), ",d")))

    return timeseries_data


# =======================================================================================
def get_stories(params, print_params=None, print_count=None, print_story=None):
    if print_params is None or print_params == 'yes':
        pprint(params)

    fetched_stories = []
    stories = None
    while stories is None or len(stories) > 0:
        try:
            response = requests.get('https://api.aylien.com/news/stories', params=params, headers=headers).json()
        except Exception as e:
            continue

        if 'errors' in response or 'error' in response:
            pprint(response)

        stories = response['stories']

        if len(stories) > 0:
            print(stories[0]['title'])
            print(stories[0]['links']['permalink'])

        params['cursor'] = response['next_page_cursor']

        fetched_stories += stories

        if (print_story is None or print_story == 'yes') and len(stories) > 0:
            pprint(stories[0]['title'])

        if print_count is None or print_count == 'yes':
            print("Fetched %d stories. Total story count so far: %d" % (len(stories), len(fetched_stories)))

    return fetched_stories


# =======================================================================================
def get_top_ranked_stories(params, no_stories, print_params=None, print_count=None):
    if print_params is None or print_params == 'yes':
        pprint(params)

    fetched_stories = []
    stories = None
    while stories is None or len(stories) > 0 and len(fetched_stories) < no_stories:
        try:
            response = requests.get('https://api.aylien.com/news/stories', params=params, headers=headers).json()
        except Exception as e:
            continue

        if 'errors' in response or 'error' in response:
            pprint(response)

        stories = response['stories']

        if len(stories) > 0:
            print(stories[0]['title'])
            print(stories[0]['links']['permalink'])

        params['cursor'] = response['next_page_cursor']

        fetched_stories += stories

        if print_count is None or print_count == 'yes':
            print("Fetched %d stories. Total story count so far: %d" % (len(stories), len(fetched_stories)))

    return fetched_stories


# =======================================================================================
def get_clusters(params={}):
    # pprint(params)

    response = requests.get('https://api.aylien.com/news/clusters', params=params, headers=headers).json()

    if 'errors' in response or 'error' in response:
        pprint(response)

    return response


# =======================================================================================
# pull trends data to identify most frequently occuring entities or keywords
def get_trends(params={}):
    # pprint(params)

    response = requests.get('https://api.aylien.com/news/trends', params=params, headers=headers).json()

    if 'errors' in response or 'error' in response:
        pprint(response)

    return response


# =======================================================================================
def get_cluster_from_trends(params, print_params=None):
    if print_params is None or print_params == 'yes':
        pprint(params)

    """
    Returns a list of up to 100 clusters that meet the parameters set out.
    """
    response = requests.get('https://api.aylien.com/news/trends', params=params, headers=headers).json()

    if 'errors' in response or 'error' in response:
        pprint(response)

    if len(response) > 0:
        return response["trends"]


# =======================================================================================
# identify the top ranked story per cluster
def get_top_stories_in_cluster(cluster_id, no_stories):
    top_story_params = {
        'clusters[]': [cluster_id]
        , 'sort_by': "source.rankings.alexa.rank"
        , 'per_page': no_stories
        , 'return[]': ['id', 'language', 'links', 'title', 'source', 'translations', 'clusters', 'published_at']
    }

    response = requests.get('https://api.aylien.com/news/stories', params=top_story_params, headers=headers).json()

    if 'errors' in response or 'error' in response:
        pprint(response)
    if len(response["stories"]) > 0:
        return response["stories"]
    else:
        return None


# =======================================================================================
# helper endpoint that takes a string of characters and an entity type (such as sources, or DBpedia entities) and returns matching entities of the specified type along with additional metadata
# params = {'type' : 'source_names', 'term' : 'Times of India' }

def autocompletes(params={}):
    pprint(params)
    """
    Returns a list of up to 100 clusters that meet the parameters set out.
    """
    response = requests.get('https://api.aylien.com/news/autocompletes', params=params, headers=headers).json()

    if 'errors' in response or 'error' in response:
        pprint(response)

    pprint(response)


# =======================================================================================
# return transalted title or body of a story (specify in params)
def return_translated_content(story_x, text_x):
    if 'translations' in story_x:
        return story_x['translations']['en'][text_x]
    else:
        return story_x[text_x]


# create smaller lists from big lists
def chunks(lst, n):
    return list(lst[i:i + n] for i in range(0, len(lst), n))


# =======================================================================================
# split title string over multiple lines for legibility on graph
def split_title_string(dataframe_x, column_x):
    title_strings = []

    for index, row in dataframe_x.iterrows():
        word_array = row[column_x].split()
        counter = 0
        string = ''
        for word in word_array:
            if counter == 7:
                string += (word + '<br>')
                counter = 0
            else:
                string += (word + ' ')
                counter += 1
        title_strings.append(string)

    dataframe_x[column_x + '_string'] = (title_strings)


# =======================================================================================
def print_keyword_mention(story_x, element_x, keyword_x):
    body_x = story_x[element_x]

    if 'translations' in story_x and story_x['translations'] is not None and 'en' in story_x['translations']:
        body_x = story_x['translations']['en'][element_x]

    # extract a window around key entity
    e_idx = body_x.find(keyword_x)
    e_end = e_idx + len(keyword_x)
    if e_idx >= 0:
        e_str = body_x[e_idx - 100:e_idx] + "\033[1m" + body_x[e_idx:e_end] + "\033[0m " + body_x[e_end + 1:e_end + 51]
        print(f'{e_str}')

    elif element_x == 'title':
        print(story_x['title'])


# =======================================================================================
def print_entities(story_x, element_x=None, surface_form_x=None, version_x=None):
    element = ''
    if element_x is None or element_x == 'body':
        element = 'body'
    else:
        element = 'title'

    # if no surface_form
    if surface_form_x is None:
        for entity in story_x['entities']:
            pprint(entity)

    else:

        for entity in story_x['entities']:
            x = 0
            for surface_form in entity[element_x]['surface_forms']:
                if surface_form_x.lower() in surface_form['text'].lower():
                    x = 1

            if x != 0:
                pprint(entity)


# =======================================================================================
def checker(request):
    headers = {
        'X-AYLIEN-NewsAPI-Application-ID': '6ce280e7',
        'X-AYLIEN-NewsAPI-Application-Key': '5f9ffc44e244334cbfec94e19549dbd0'
    }

    if(request.method =='POST'):
        form = PublicsForm(request.POST)
        form.save()

    form = PublicsForm()

    publics = Publics.objects.all()

    all_publics = []

    for pub in publics:
        params = {
            'published_at.start': pub.public_start,
            'published_at.end': pub.public_end,
            'language[]': [pub.language],
            'per_page': pub.page
        }
        stories = get_top_ranked_stories(params, 1).json()
        info = {
            'published_at.start': stories['published_at.start'],
            'published_at.end': stories['published_at.end'],
            'language[]': stories['language[]'],
            'per_page': stories['per_page'],
            'polarity': stories['polarity'],
            'author': stories['author'],
            'name': stories['name'],
            'link': stories['link'],
        }
        all_publics.append(info)

    context = {'all_info': all_publics, 'form': form}
    return render(request, 'checker.html', context)

