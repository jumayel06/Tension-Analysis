from process import *
from EmotionHelpers import *
from HedgeDetection import *

# Initializations
hedges = []
markers = []
cues = []
boosters = []
NEGATIVE_EMOTIONS = ["anger", 'fear', "sadness"]
QUES_TYPES = ["what", "when", "where", "who", "why", "how", "yesno", "mixed"]


# Pre-trained model for emotion recognition
# emotions = ['anger', 'emotion-not-listed', 'fear', 'happiness', 'NE', 'sadness']
model = load_model(sys.argv[1])
with open(sys.argv[2], 'rb') as f:
    lb, tokenizer_tweets, max_tweet_length, tokenizer_hash_emo, max_hash_emo_length, embeddings_index = pickle.load(f)


# Load pre-requisites
with open("resources/booster_words.txt", 'r') as f:
    for line in f:
        if '#' not in line.strip():
            boosters.append(line.strip())

with open("resources/cues.txt", 'r') as f:
    for line in f:
        if '#' not in line.strip():
            cues.append(line.strip())


# Returns negative if given sentence contains negative emotion, otherwise returns positive
# Input: Sentence or Text
# Output: "Negative" or "Positive"
def get_emotion(sentence):
    cleaned_sentences, hash_emos = clean_texts([sentence])
    features = feature_generation(cleaned_sentences, hash_emos)

    evalX = encode_text(tokenizer_tweets, cleaned_sentences, max_tweet_length)
    encoded_hash_emo = encode_text(tokenizer_hash_emo, hash_emos, max_hash_emo_length)

    predictedY = model.predict([evalX,encoded_hash_emo,features])
    predicted_classes = lb.inverse_transform(predictedY)
    if predicted_classes[0] in NEGATIVE_EMOTIONS:
        return "negative"
    else:
        return "positive"


# Returns statistics (mean, standard deviation) for all kind of question types in a transcript
# Input: question-answer pairs
# Output: Dictionary with mean and standard deviation
def ques_statistics(pairs):
    d = {"what": [], "when": [], "where": [], "who": [], "why": [], "how": [], "yesno": [], "mixed": []}
    stats = {"what": {"mean": 0.0, "std": 0.0},
             "when": {"mean": 0.0, "std": 0.0},
             "where": {"mean": 0.0, "std": 0.0},
             "who": {"mean": 0.0, "std": 0.0},
             "why": {"mean": 0.0, "std": 0.0},
             "how": {"mean": 0.0, "std": 0.0},
             "yesno": {"mean": 0.0, "std": 0.0},
             "mixed": {"mean": 0.0, "std": 0.0}}

    for pair in pairs:
        ques = pair[0].lower()
        ans = pair[1].lower()
        counter = 0
        found_type = ""
        for type in QUES_TYPES:
            if type in ques:
                counter += 1
                found_type = type

        if counter == 0:
            d["yesno"].append(len(word_tokenize(ans)))
        elif counter == 1:
            d[found_type].append(len(word_tokenize(ans)))
        else:
            d["mixed"].append(len(word_tokenize(ans)))

    for key, value in d.items():
        if len(value) > 0:
            stats[key]["mean"] = np.mean(value)
            stats[key]["std"] = np.std(value)
        else:
            stats[key]["mean"] = 0.0
            stats[key]["std"] = 0.0

    return stats


# Returns True if sentence contains boosting, otherwise returns False
# Input: Sentence
# Output: True/False
def IsBoosting(s):
    for word in boosters:
        if word in s:
            list_of_words = s.split()
            if word in list_of_words:
                previous_word = list_of_words[list_of_words.index(word) - 1]
            else:
                previous_word = ""
            if previous_word in ['not', "without"]:
                return False
            else:
                return True

# Generates a csv file containing identified tension points for the provided interview file
# Input: List of question-answer pairs (Ex: [(q1,a1),(q2,a2),...])
def tension_analysis(ques_ans):
    with open(sys.argv[4], mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Content', 'Role', 'Predicted Label'])

        stats = ques_statistics(ques_ans)
        for pair in ques_ans:
            ques = pair[0].lower()
            ans = pair[1].lower()
            sentences = sent_tokenize(ans)
            writer.writerow([pair[0], 'Interviewer', "-"])
            isNegativeEmotion = False
            isHedging = False
            isQuestion = False
            isOutlier = False
            isBoosting = False
            cuePresent = False

            for s in sentences[:5]:
                if get_emotion(s) == "negative":
                    isNegativeEmotion = True

                if IsHedgedSentence(s):
                    isHedging = True

                if IsBoosting(s):
                    isBoosting = True

            for cue in cues:
                if cue in ans:
                    cuePresent = True

            for qt in ["what", "when", "where", "who", "why", "how"]:
                if len(sentences) > 0 and qt in sentences[0] and "?" in sentences[0]:
                    isQuestion = True

            number_of_words = len(word_tokenize(ans))
            counter = 0
            found_type = ""

            for type in QUES_TYPES:
                if type in ques:
                    counter += 1
                    found_type = type

            if counter == 0:
                mean = stats["yesno"]["mean"]
                std = stats["yesno"]["std"]
            elif counter == 1:
                mean = stats[found_type]["mean"]
                std = stats[found_type]["std"]
            else:
                mean = stats["mixed"]["mean"]
                std = stats["mixed"]["std"]

            if number_of_words > mean + 3 * std or number_of_words < mean - 3 * std:
                isOutlier = True

            if (isNegativeEmotion and isHedging) or (isBoosting and isHedging) or (cuePresent and isHedging) or isQuestion or isOutlier:
                writer.writerow([pair[1], 'Interviewee', "Tension"])
            else:
                writer.writerow([pair[1], 'Interviewee', "No Tension"])


if __name__ == "__main__":
        print("Processing file...")
        try:
            processor = Process(sys.argv[3])
            processor.process_html()
            ques_ans = processor.extract_ques_ans()
        except:
            print("Your file is not in the right format. Please provide valid file.")
            sys.exit()
        print("Processing completed...")

        print("Analyzing...")
        tension_analysis(ques_ans)
        print("*** Analysis Completed ***")
