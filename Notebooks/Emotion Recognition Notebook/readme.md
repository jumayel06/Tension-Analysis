1. The notebook in the current directory demnostrates the implementation of multi-channel CNN model on the Twitter Emotion Corpus (TEC) dataset. 
2. Link of paper: http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.383.3384&rep=rep1&type=pdf
3. Link of dataset: http://saifmohammad.com/WebPages/SentimentEmotionLabeledData.html
4. The notebook can be reused for other twitter datasets, but those datasets must be processed in the same way as the TEC dataset


## Prerequisites:
Install Anaconda.

We will use ***Jupyter*** notebook.

**Python version:** 3.6.3

**Tensorflow version:** 1.5.1

**Keras version:** 2.1.6

## GloVe Embeddings:
**Link:** https://nlp.stanford.edu/projects/glove/

Download **glove.twitter.27B.zip**.

Place **glove.twitter.27B.100d.txt** in the project directory.

Change the variable **embedding_dir** in the notebook and set the location.

## Lexicons:
Lexicons and resources are available in the directory (folder -> lexicons).

#### Warriner et al. (2013)
**Paper:** Warriner, A.B., Kuperman, V., & Brysbaert, M. (2013). Norms of valence, arousal, and dominance for 13,915 English lemmas. Behavior Research Methods.

**Link:** http://crr.ugent.be/papers/Ratings_Warriner_et_al.csv

#### Vader (2014)
**Paper:** Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. Eighth International Conference on Weblogs and Social Media (ICWSM-14).

**Link:** https://github.com/cjhutto/vaderSentiment

Python Library available!

#### NRC Emotion Lexicon (2013)
**Paper:** Saif Mohammad and Peter Turney (2013). Crowdsourcing a Word-Emotion Association Lexicon,  Computational Intelligence.

**Link:** https://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm

#### NRC Affect Intensity Lexicon (2018)
**Paper:** Saif M. Mohammad (2018). Word Affect Intensities. In Proceedings of the 11th Edition of the Language Resources and Evaluation Conference (LREC-2018).

**Link:** http://saifmohammad.com/WebPages/AffectIntensity.htm


#### NRC Hashtag Emotion Lexicon (2015)
**Paper:** Saif M. Mohammad, Svetlana Kiritchenko (2015). Using Hashtags to Capture Fine Emotion Categories from Tweets. Computational Intelligence.

**Link:** http://saifmohammad.com/WebPages/lexicons.html


#### BingLiu (2004)
**Paper:** Minqing Hu and Bing Liu (2004). Mining and Summarizing Customer Reviews. KDD.

**Link:** https://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html


#### MPQA (2005)
**Paper:** Theresa Wilson, Janyce Wiebe, and Paul Hoffmann (2005). Recognizing Contextual Polarity in Phrase-Level Sentiment Analysis. Proc. of HLT-EMNLP.

**Link:** https://mpqa.cs.pitt.edu/lexicons/


#### AFINN (2011)
**Paper:** Finn Årup Nielsen (2011). A new ANEW: Evaluation of a word list for sentiment analysis in microblogs. Proceedings of the ESWC2011.

**Link:** http://corpustext.com/reference/sentiment_afinn.html
