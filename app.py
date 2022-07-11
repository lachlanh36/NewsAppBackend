# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import logging
from pprint import pprint
import boto3
from botocore.exceptions import ClientError
import requests
import json
from newsapi import NewsApiClient
from flask_cors import CORS
import random


from apscheduler.schedulers.background import BackgroundScheduler
positiveArticles = []
newsapi = NewsApiClient(api_key='4441e00ee0f44711a030109b986f82fc')
try:
    with open('sample.json', 'r') as openfile:
        # Reading from json file
         positiveArticles = json.load(openfile)

except Exception as e:
    print(e)
    pass
articles = {}

# setting up some flask stuff
app = Flask(__name__)
api = Api(app)
cors = CORS(app)

def getNewsEveryHour():
    print('Getting news')
    r = requests.get(
        "https://newsapi.org/v2/everything?sources=abc-news&pageSize=100&apiKey=4441e00ee0f44711a030109b986f82fc")
    print(r.json())
    p = requests.get(
       "https://newsapi.org/v2/everything?sources=bbc-news&pageSize=100&apiKey=4441e00ee0f44711a030109b986f82fc")
    print(p.json())
    f = requests.get("https://newsapi.org/v2/everything?sources=national-geographic&pageSize=100&apiKey=4441e00ee0f44711a030109b986f82fc")
    g = requests.get(
       "https://newsapi.org/v2/everything?sources=associated-press&pageSize=100&apiKey=4441e00ee0f44711a030109b986f82fc")
    print(g.json())
    k= requests.get("https://newsapi.org/v2/everything?sources=new-scientist&pageSize=100&apiKey=4441e00ee0f44711a030109b986f82fc")
    l = requests.get(
       'https://newsapi.org/v2/everything?q=wholesome&pageSize=33&apiKey=4441e00ee0f44711a030109b986f82fc')
    filterArticles(r.text)
    filterArticles(p.text)
    filterArticles(f.text)
    filterArticles(g.text)
    filterArticles(k.text)
    filterArticles(l.text)
    random.shuffle(positiveArticles)
    json_object = json.dumps(positiveArticles, indent=4)
    with open("sample.json", "a") as outfile:
        outfile.write(json_object)

class PositiveNews(Resource):
    def get(self):
        return jsonify(positiveArticles)

class GetNews(Resource):
    def get(self):
        print('Getting news')
        r = requests.get("https://newsapi.org/v2/everything?sources=abc-news&pageSize=100&apiKey=4441e00ee0f44711a030109b986f82fc")
        print(r.json())
        p = requests.get("https://newsapi.org/v2/everything?sources=bbc-news&pageSize=100&apiKey=4441e00ee0f44711a030109b986f82fc")
        print(p.json())
        f = requests.get("https://newsapi.org/v2/everything?sources=national-geographic&pageSize=100&apiKey=4441e00ee0f44711a030109b986f82fc")
        print(f.json())
        g = requests.get("https://newsapi.org/v2/everything?sources=associated-press&pageSize=100&apiKey=4441e00ee0f44711a030109b986f82fc")
        print(g.json())
        k = requests.get(
            "https://newsapi.org/v2/everything?sources=new-scientist&pageSize=100&apiKey=4441e00ee0f44711a030109b986f82fc")
        l = requests.get(
           'https://newsapi.org/v2/everything?q=inspirational&pageSize=33&apiKey=4441e00ee0f44711a030109b986f82fc')
        filterArticles(r.text)
        filterArticles(p.text)
        filterArticles(f.text)
        filterArticles(g.text)
        filterArticles(k.text)
        filterArticles(l.text)
        random.shuffle(positiveArticles)
        json_object = json.dumps(positiveArticles, indent=4)
        with open("sample.json", "a") as outfile:
            outfile.write(json_object)

api.add_resource(PositiveNews, '/api/positiveNews')
api.add_resource(GetNews, '/api/getNews')
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=getNewsEveryHour, trigger='interval', seconds=(3600))
# scheduler.start()


def filterArticles (data):
    articles = json.loads(data)['articles']
    print('filtering articles')
    for article in articles:
        try:
            if article['description'] and doAllTheStuff(article['description']) == 'POSITIVE' and doAllTheStuff(article['title']) == 'POSITIVE':
                positiveArticles.append(article)

                # print(article['title'])
            elif article['content'] and doAllTheStuff(article['content']) == 'POSITIVE':
                positiveArticles.append(article)
                # print(article['title'])
        except Exception as e:
            print(e)
            pass



def isPositive(sentiment):
    if (sentiment):
        mixed = sentiment['SentimentScore']['Mixed']
        positive = sentiment['SentimentScore']['Positive']
        negative = sentiment['SentimentScore']['Negative']
        neutral = sentiment['SentimentScore']['Neutral']
        if positive > negative and negative<0.25 and positive>0.18:
            return 'POSITIVE'
    return "NEGATIVE"


logger = logging.getLogger(__name__)


class ComprehendDetect:
    """Encapsulates Comprehend detection functions."""
    def __init__(self, comprehend_client):
        """
        :param comprehend_client: A Boto3 Comprehend client.
        """
        self.comprehend_client = boto3.client('comprehend')


    def detect_languages(self, text):
        try:
            response = self.comprehend_client.detect_dominant_language(Text=text)
            languages = response['Languages']
            #logger.info("Detected %s languages.", len(languages))
        except ClientError:
            logger.exception("Couldn't detect languages.")
            raise
        else:
            return languages


    def detect_sentiment(self, text, language_code):
        try:
            if (language_code == 'en'):
                response = self.comprehend_client.detect_sentiment(Text=text, LanguageCode=language_code)
            else:
                return None
            #logger.info("Detected primary sentiment %s.", response['Sentiment'])
        except ClientError:
            logger.exception("Couldn't detect sentiment.")
            raise
        else:
            return response



def doAllTheStuff(testText):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    comp_detect = ComprehendDetect(boto3.client('comprehend'))

    with open('detect_sample.txt') as sample_file:
        sample_text = sample_file.read()
    demo_size = 3
    #print("Sample text used for this demo:")
    #print('-'*88)
    #print(sample_text)
    #print('-'*88)

    #print("Detecting languages.")
    languages = comp_detect.detect_languages(testText)
    #pprint(languages)
    lang_code = languages[0]['LanguageCode']



    #print("Detecting sentiment.")
    sentiment = comp_detect.detect_sentiment(testText, lang_code)
    # print(f"Sentiment: {sentiment['Sentiment']}")getNewsEveryHour
    if (sentiment):
        return sentiment
    # print("SentimentScore:")
    if (sentiment):
        mixed = sentiment['SentimentScore']['Mixed']
        positive = sentiment['SentimentScore']['Positive']
        negative = sentiment['SentimentScore']['Negative']
        neutral = sentiment['SentimentScore']['Neutral']
        if positive > negative and negative<0.25 and positive>0.18:
            return 'POSITIVE'
    return "NEGATIVE"

    #return sentiment['Sentiment']


#
# if 1==1:
#     filterArticles()



getNewsEveryHour()
app.run(debug=False, host="0.0.0.0", port=5000)