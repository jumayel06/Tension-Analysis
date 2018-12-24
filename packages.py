from bs4 import BeautifulSoup
import mammoth
import json
import logging
import os
import socket
import subprocess
import sys
import time
import requests
from nltk.tokenize import word_tokenize
from nltk.metrics import jaccard_distance
import string
import psutil
from nltk.tokenize import TweetTokenizer
import re, csv
from nltk.stem.wordnet import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from emoji.unicode_codes import UNICODE_EMOJI
import emoji
import glob, re, pickle, math, statistics
from collections import Counter
from nltk import sent_tokenize, ngrams
from keras.models import load_model
import numpy as np
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from random import shuffle

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
