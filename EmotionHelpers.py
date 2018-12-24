from packages import *

feature_dimension = 29

# ********* Load Lexicons ********* #
bingliu_mpqa = {}
nrc_emotion = {}
nrc_affect_intensity = {}
nrc_hashtag_emotion = {}
afinn = {}
ratings = {}
stopwords = []
slangs = {}
negated = {}
emoticons = []

# Vader
analyzer = SentimentIntensityAnalyzer()

def load_lexicons():
    # Ratings by Warriner et al. (2013)
    with open('lexicons/Ratings_Warriner_et_al.csv', 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
    for i in range(1, len(rows)):
        # Normalize values
        valence = (float(rows[i][2]) - 1.0)/(9.0-1.0)
        arousal = (float(rows[i][5]) - 1.0)/(9.0-1.0)
        dominance = (float(rows[i][8]) - 1.0)/(9.0-1.0)
        ratings[rows[i][1]] = {"Valence": valence, "Arousal": arousal, "Dominance": dominance}


    # NRC Emotion Lexicon (2014)
    with open('lexicons/NRC-emotion-lexicon-wordlevel-v0.92.txt', 'r') as f:
        f.readline()
        for line in f:
            splitted = line.strip().split('\t')
            if splitted[0] not in nrc_emotion:
                nrc_emotion[splitted[0]] = {'anger': float(splitted[1]),
                                                    'disgust': float(splitted[3]),
                                                    'fear': float(splitted[4]),
                                                    'joy': float(splitted[5]),
                                                    'sadness': float(splitted[8]),
                                                    'surprise': float(splitted[9])}

    # NRC Affect Intensity (2018)
    with open('lexicons/nrc_affect_intensity.txt', 'r') as f:
        f.readline()
        for line in f:
            splitted = line.strip().split('\t')
            if splitted[0] not in nrc_affect_intensity:
                nrc_affect_intensity[splitted[0]] = {'anger': float(splitted[1]),
                                                    'disgust': float(splitted[3]),
                                                    'fear': float(splitted[4]),
                                                    'joy': float(splitted[5]),
                                                    'sadness': float(splitted[8]),
                                                    'surprise': float(splitted[9])}

    # NRC Hashtag Emotion Lexicon (2015)
    with open('lexicons/NRC-Hashtag-Emotion-Lexicon-v0.2.txt', 'r') as f:
        f.readline()
        for line in f:
            splitted = line.strip().split('\t')
            splitted[0] = splitted[0].replace('#','')
            if splitted[0] not in nrc_hashtag_emotion:
                nrc_hashtag_emotion[splitted[0]] = {'anger': float(splitted[1]),
                                                    'disgust': float(splitted[3]),
                                                    'fear': float(splitted[4]),
                                                    'joy': float(splitted[5]),
                                                    'sadness': float(splitted[8]),
                                                    'surprise': float(splitted[9])}


    # BingLiu (2004) and MPQA (2005)
    with open('lexicons/BingLiu.txt', 'r') as f:
        for line in f:
            splitted = line.strip().split('\t')
            if splitted[0] not in bingliu_mpqa:
                bingliu_mpqa[splitted[0]] = splitted[1]
    with open('lexicons/mpqa.txt', 'r') as f:
        for line in f:
            splitted = line.strip().split('\t')
            if splitted[0] not in bingliu_mpqa:
                bingliu_mpqa[splitted[0]] = splitted[1]


    with open('lexicons/AFINN-en-165.txt', 'r') as f:
        for line in f:
            splitted = line.strip().split('\t')
            if splitted[0] not in afinn:
                score = float(splitted[1])
                normalized_score = (score - (-5)) / (5-(-5))
                afinn[splitted[0]] = normalized_score


    with open('lexicons/stopwords.txt', 'r') as f:
        for line in f:
            stopwords.append(line.strip())

    with open('lexicons/slangs.txt', 'r') as f:
        for line in f:
            splitted = line.strip().split(',', 1)
            slangs[splitted[0]] = splitted[1]

    with open('lexicons/negated_words.txt', 'r') as f:
        for line in f:
            splitted = line.strip().split(',', 1)
            negated[splitted[0]] = splitted[1]

    with open('lexicons/emoticons.txt', 'r') as f:
        for line in f:
            emoticons.append(line.strip())
load_lexicons()

# ********* Helper Functions ********* #

def clean_texts(texts):
    cleaned_tweets = []
    hash_emos = []

    for text in texts:
        hash_emo = []
        text = re.sub('(!){2,}', ' <!repeat> ', text)
        text = re.sub('(\?){2,}', ' <?repeat> ', text)

        # Tokenize using tweet tokenizer
        tokenizer = TweetTokenizer(strip_handles=False, reduce_len=True)
        tokens = tokenizer.tokenize(text.lower())
        lemmatizer = WordNetLemmatizer()


        # Emojis and emoticons
        if text_has_emoji(text):
            temp = []
            for word in tokens:
                if char_is_emoji(word):
                    hash_emo.append(UNICODE_EMOJI[word])
                elif word in emoticons:
                    hash_emo.append(word)
                else:
                    temp.append(word)
            tokens = temp

        # Hashtags
        temp = []
        for word in tokens:
            if '#' in word:
                word = word.replace('#','')
                hash_emo.append(word)
            else:
                temp.append(word)
        tokens = temp

        # Replace slangs and negated words
        temp = []
        for word in tokens:
            if word in slangs:
                temp += slangs[word].split()
            elif word in negated:
                temp += negated[word].split()
            else:
                temp.append(word)
        tokens = temp

        # Replace user names
        tokens = ['<user>'  if '@' in word else word for word in tokens]

        #Replace numbers
        tokens = ['<number>' if word.isdigit() else word for word in tokens]

        # Remove urls
        tokens = ['' if 'http' in word else word for word in tokens]

        # Lemmatize
        #tokens = [lemmatizer.lemmatize(word) for word in tokens]

        # Remove stop words
        tokens = [word for word in tokens if word not in stopwords]

        # Remove tokens having length 1
        tokens = [word for word in tokens if word != '' and len(word) > 1]

        cleaned_tweets.append(tokens)
        hash_emos.append(hash_emo)

    return cleaned_tweets, hash_emos


# This function returns a n-dimensional feature vector
def feature_generation(texts, hashtags):
    feature_vectors = []

    for i in range(len(texts)):
        feats = [0] * feature_dimension
        for word in texts[i]:
            # Warriner er al.
            if word in ratings:
                feats[0] += ratings[word]['Valence']
                feats[1] += ratings[word]['Arousal']
                feats[2] += ratings[word]['Dominance']

            # Vader Sentiment
            polarity_scores = analyzer.polarity_scores(word)
            feats[3] += polarity_scores['pos']
            feats[4] += polarity_scores['neg']
            feats[5] += polarity_scores['neu']

            # NRC Emotion
            if word in nrc_emotion:
                feats[6] += nrc_emotion[word]['anger']
                feats[7] += nrc_emotion[word]['disgust']
                feats[8] += nrc_emotion[word]['fear']
                feats[9] += nrc_emotion[word]['joy']
                feats[10] += nrc_emotion[word]['sadness']
                feats[11] += nrc_emotion[word]['surprise']

            # NRC Affect Intensity
            if word in nrc_affect_intensity:
                feats[12] += nrc_affect_intensity[word]['anger']
                feats[13] += nrc_affect_intensity[word]['disgust']
                feats[14] += nrc_affect_intensity[word]['fear']
                feats[15] += nrc_affect_intensity[word]['joy']
                feats[16] += nrc_affect_intensity[word]['sadness']
                feats[17] += nrc_affect_intensity[word]['surprise']

            # AFINN
            if word in afinn:
                feats[18] += float(afinn[word])

            # BingLiu and MPQA
            if word in bingliu_mpqa:
                if bingliu_mpqa[word] == 'positive':
                    feats[19] += 1
                else:
                    feats[20] += 1


        count = len(texts[i])
        if count == 0:
            count = 1
        newArray = np.array(feats)/count
        feats = list(newArray)

        # Presence of consecutive exclamation mark or question mark
        for word in texts[i]:
            if word == '<!REPEAT>':
                feats[21] = 1
            elif word == '<?REPEAT>':
                feats[22] = 1

        for word in hashtags[i]:
            #NRC Hashtag Emotion
            if word in nrc_hashtag_emotion:
                feats[23] += nrc_hashtag_emotion[word]['anger']
                feats[24] += nrc_hashtag_emotion[word]['disgust']
                feats[25] += nrc_hashtag_emotion[word]['fear']
                feats[26] += nrc_hashtag_emotion[word]['joy']
                feats[27] += nrc_hashtag_emotion[word]['sadness']
                feats[28] += nrc_hashtag_emotion[word]['surprise']

        feature_vectors.append(feats)
    return np.array(feature_vectors)


def create_tokenizer(lines):
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(lines)
    return tokenizer


def max_length(lines):
    return max([len(s) for s in lines])


def encode_text(tokenizer, lines, length):
    encoded = tokenizer.texts_to_sequences(lines)
    padded = pad_sequences(encoded, maxlen=length, padding='post')
    return padded

def char_is_emoji(character):
    return character in emoji.UNICODE_EMOJI

def text_has_emoji(text):
    for character in text:
        if character in emoji.UNICODE_EMOJI:
            return True
    return False
