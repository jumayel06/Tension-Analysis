from packages import *

# ********* Initializations ********* #
lmtzr = WordNetLemmatizer()
hedge_words = []
discourse_markers = []
THRESHOLD = 0.8

# ********* Python Wrapper for Stanford CoreNLP ********* #
# ********* Class definition implemented from "https://github.com/Lynten/stanford-corenlp" with slight modifications ********* #

class StanfordCoreNLP:
    def __init__(self, path_or_host, port=None, memory='4g', lang='en', timeout=5000, quiet=True,
                 logging_level=logging.WARNING, max_retries=100):
        self.path_or_host = path_or_host
        self.port = port
        self.memory = memory
        self.lang = lang
        self.timeout = timeout
        self.quiet = quiet
        self.logging_level = logging_level

        logging.basicConfig(level=self.logging_level)

        # Check args
        self._check_args()

        if path_or_host.startswith('http'):
            self.url = path_or_host + ':' + str(port)
            logging.info('Using an existing server {}'.format(self.url))
        else:

            # Check Java
            if not subprocess.call(['java', '-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) == 0:
                raise RuntimeError('Java not found.')

            # Check if the dir exists
            if not os.path.isdir(self.path_or_host):
                raise IOError(str(self.path_or_host) + ' is not a directory.')
            directory = os.path.normpath(self.path_or_host) + os.sep
            self.class_path_dir = directory

            # Check if the language specific model file exists
            switcher = {
                'en': 'stanford-corenlp-[0-9].[0-9].[0-9]-models.jar',
                'zh': 'stanford-chinese-corenlp-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-models.jar',
                'ar': 'stanford-arabic-corenlp-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-models.jar',
                'fr': 'stanford-french-corenlp-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-models.jar',
                'de': 'stanford-german-corenlp-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-models.jar',
                'es': 'stanford-spanish-corenlp-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-models.jar'
            }
            jars = {
                'en': 'stanford-corenlp-x.x.x-models.jar',
                'zh': 'stanford-chinese-corenlp-yyyy-MM-dd-models.jar',
                'ar': 'stanford-arabic-corenlp-yyyy-MM-dd-models.jar',
                'fr': 'stanford-french-corenlp-yyyy-MM-dd-models.jar',
                'de': 'stanford-german-corenlp-yyyy-MM-dd-models.jar',
                'es': 'stanford-spanish-corenlp-yyyy-MM-dd-models.jar'
            }
            if len(glob.glob(directory + switcher.get(self.lang))) <= 0:
                raise IOError(jars.get(
                    self.lang) + ' not exists. You should download and place it in the ' + directory + ' first.')

            self.port = 9999

            # Start native server
            logging.info('Initializing native server...')
            cmd = "java"
            java_args = "-Xmx{}".format(self.memory)
            java_class = "edu.stanford.nlp.pipeline.StanfordCoreNLPServer"
            class_path = '"{}*"'.format(directory)

            args = [cmd, java_args, '-cp', class_path, java_class, '-port', str(self.port)]

            args = ' '.join(args)

            logging.info(args)

            # Silence
            with open(os.devnull, 'w') as null_file:
                out_file = None
                if self.quiet:
                    out_file = null_file

                self.p = subprocess.Popen(args, shell=True, stdout=out_file, stderr=subprocess.STDOUT)
                logging.info('Server shell PID: {}'.format(self.p.pid))

            self.url = 'http://localhost:' + str(self.port)

        # Wait until server starts
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_name = urlparse(self.url).hostname
        time.sleep(1)  # OSX, not tested
        trial = 1
        while sock.connect_ex((host_name, self.port)):
            if trial > max_retries:
                raise ValueError('Corenlp server is not available')
            logging.info('Waiting until the server is available.')
            trial += 1
            time.sleep(1)
        logging.info('The server is available.')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        logging.info('Cleanup...')
        if hasattr(self, 'p'):
            try:
                parent = psutil.Process(self.p.pid)
            except psutil.NoSuchProcess:
                logging.info('No process: {}'.format(self.p.pid))
                return

            if self.class_path_dir not in ' '.join(parent.cmdline()):
                logging.info('Process not in: {}'.format(parent.cmdline()))
                return

            children = parent.children(recursive=True)
            for process in children:
                logging.info('Killing pid: {}, cmdline: {}'.format(process.pid, process.cmdline()))
                # process.send_signal(signal.SIGTERM)
                process.kill()

            logging.info('Killing shell pid: {}, cmdline: {}'.format(parent.pid, parent.cmdline()))
            # parent.send_signal(signal.SIGTERM)
            parent.kill()

    def annotate(self, text, properties=None):
        if sys.version_info.major >= 3:
            text = text.encode('utf-8')

        r = requests.post(self.url, params={'properties': str(properties)}, data=text,
                          headers={'Connection': 'close'})
        return r.text

    def tregex(self, sentence, pattern):
        tregex_url = self.url + '/tregex'
        r_dict = self._request(tregex_url, "tokenize,ssplit,depparse,parse", sentence, pattern=pattern)
        return r_dict

    def tokensregex(self, sentence, pattern):
        tokensregex_url = self.url + '/tokensregex'
        r_dict = self._request(tokensregex_url, "tokenize,ssplit,depparse", sentence, pattern=pattern)
        return r_dict

    def semgrex(self, sentence, pattern):
        semgrex_url = self.url + '/semgrex'
        r_dict = self._request(semgrex_url, "tokenize,ssplit,depparse", sentence, pattern=pattern)
        return r_dict

    def word_tokenize(self, sentence, span=False):
        r_dict = self._request('ssplit,tokenize', sentence)
        tokens = [token['originalText'] for s in r_dict['sentences'] for token in s['tokens']]

        # Whether return token span
        if span:
            spans = [(token['characterOffsetBegin'], token['characterOffsetEnd']) for s in r_dict['sentences'] for token
                     in s['tokens']]
            return tokens, spans
        else:
            return tokens

    def pos_tag(self, sentence):
        r_dict = self._request(self.url, 'pos', sentence)
        words = []
        tags = []
        for s in r_dict['sentences']:
            for token in s['tokens']:
                words.append(token['originalText'])
                tags.append(token['pos'])
        return list(zip(words, tags))

    def ner(self, sentence):
        r_dict = self._request(self.url, 'ner', sentence)
        words = []
        ner_tags = []
        for s in r_dict['sentences']:
            for token in s['tokens']:
                words.append(token['originalText'])
                ner_tags.append(token['ner'])
        return list(zip(words, ner_tags))

    def parse(self, sentence):
        r_dict = self._request(self.url, 'pos,parse', sentence)
        return [s['parse'] for s in r_dict['sentences']][0]

    def dependency_parse(self, text):
        r_dict = self._request(self.url, 'depparse', text)
        ls = []
        for s in r_dict['sentences']:
            tmp = []
            for dep in s['basicDependencies']:
                tmp.append((dep['dep'], dep['governorGloss'], dep['dependentGloss']))
            ls.append(tmp)
        return ls

    def coref(self, text):
        r_dict = self._request('coref', text)

        corefs = []
        for k, mentions in r_dict['corefs'].items():
            simplified_mentions = []
            for m in mentions:
                simplified_mentions.append((m['sentNum'], m['startIndex'], m['endIndex'], m['text']))
            corefs.append(simplified_mentions)
        return corefs

    def switch_language(self, language="en"):
        self._check_language(language)
        self.lang = language

    def _request(self, url, annotators=None, data=None, *args, **kwargs):
        if sys.version_info.major >= 3:
            data = data.encode('utf-8')

        properties = {'annotators': annotators, 'outputFormat': 'json'}
        params = {'properties': str(properties), 'pipelineLanguage': self.lang}
        if 'pattern' in kwargs:
            params = {"pattern": kwargs['pattern'], 'properties': str(properties), 'pipelineLanguage': self.lang}

        logging.info(params)
        r = requests.post(url, params=params, data=data, headers={'Connection': 'close'})
        r_dict = json.loads(r.text)

        return r_dict

    def _check_args(self):
        self._check_language(self.lang)
        if not re.match('\dg', self.memory):
            raise ValueError('memory=' + self.memory + ' not supported. Use 4g, 6g, 8g and etc. ')

    def _check_language(self, lang):
        if lang not in ['en', 'zh', 'ar', 'fr', 'de', 'es']:
            raise ValueError('lang=' + self.lang + ' not supported. Use English(en), Chinese(zh), Arabic(ar), '
                                                   'French(fr), German(de), Spanish(es).')

# ********* Load Lexicons ********* #

def load_lexicons():
    with open("resources/hedge_words.txt", "r") as f:
        for line in f:
            if '#' in line:
                continue
            elif line.strip() != "":
                hedge_words.append(line.strip())

    with open("resources/discourse_markers.txt", "r") as f:
        for line in f:
            if '#' in line:
                continue
            elif line.strip() != "":
                discourse_markers.append(line.strip())

# ********* Initialize CoreNLP ********* #
# Download (if you haven't already) the zip file from this link: https://drive.google.com/open?id=1ROwL9fY1-BJ57O5wkgMk4UAxWKretfTk
# Unzip the file in the resources folder
path = os.path.abspath('resources/stanford-corenlp-full-2018-02-27/')
nlp = StanfordCoreNLP(path)
load_lexicons()

# ********* Disambiguate Hedge Terms ********* #
# ********* Returns true if (hedge) token is true hedge term, otherwise, returns false ********* #

def IsTrueHedgeTerm(hedge, text):
    exclude = set(string.punctuation)

    if hedge == "assume":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if pair[0] == "ccomp" and lmtzr.lemmatize(pair[1], 'v') == hedge:
                return True
        return False

    elif hedge == "appear":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if (pair[0] in ["xcomp", "ccomp"]) and lmtzr.lemmatize(pair[1], 'v') == hedge:
                return True
        return False

    elif hedge == "suppose":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if pair[0] == "xcomp" and lmtzr.lemmatize(pair[1], 'v') == hedge:
                token = pair[2]
                for temp in tree:
                    if temp[0] == "mark" and temp[1] == token and temp[2] == "to":
                        return False
        return True

    elif hedge == "tend":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if pair[0] == "xcomp" and lmtzr.lemmatize(pair[1], 'v') == hedge:
                return True
        return False

    elif hedge == "should":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if pair[0] == "aux" and pair[2] == hedge:
                token = pair[1]
                for temp in tree:
                    if temp[1] == token and temp[2] == "have":
                        return False
        return True

    elif hedge == "likely":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if pair[2] == hedge:
                token = pair[1]
                for temp in tree:
                    if temp[2] == token and temp[1] != "ROOT":
                        tag = nlp.pos_tag(temp[1])
                        if tag[0][1] in ["NN", "NNS", "NNP", "NNPS"]:
                            return False
        return True

    elif hedge == "rather":
        s = ''.join(ch for ch in text if ch not in exclude)
        list_of_words = s.split()
        next_word = list_of_words[list_of_words.index(hedge) + 1]
        if next_word == 'than':
            return False
        else:
            return True

    elif hedge == "think":
        words = word_tokenize(text)
        for i in range(len(words) - 1):
            if words[i] == hedge:
                tag = nlp.pos_tag(words[i + 1])
                if tag[0][1] == "IN":
                    return False
                    break
        return True

    elif hedge in ["feel", "suggest", "believe", "consider", "doubt", "guess", "presume", "hope"]:
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        isRoot = False
        hasNSubj = False
        for pair in tree:
            if lmtzr.lemmatize(pair[2]) in [hedge] and pair[1] == "ROOT":
                isRoot = True
            elif lmtzr.lemmatize(pair[1]) in [hedge] and pair[0] == "nsubj":
                token = lmtzr.lemmatize(pair[1])
                subject = pair[2]
                hasNSubj = True

        if isRoot and hasNSubj:
            tags = nlp.pos_tag(text)
            status1 = False
            status2 = False
            for tag in tags:
                if lmtzr.lemmatize(tag[0]) == token and tag[1] in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                    status1 = True
                if subject.lower() in ["i", "we"]:
                    status2 = True
            if status1 and status2:
                return True
            else:
                return False


# ********* Determines if a sentence is hedged sentence or not ********* #
# ********* Returns true if sentence is hedged sentence, otherwise, returns false ********* #

def IsHedgedSentence(text):
    exclude = set(string.punctuation)
    text = text.lower()

    if "n't" in text:
        text = text.replace("n't", " not")
    elif "n’t" in text:
        text = text.replace("n’t", " not")

    tokenized = word_tokenize(text)
    phrases = []
    status = False

    # Determine the n-grams of the given sentence
    for i in range(1,6):
        phrases += ngrams(tokenized, i)

    # Determine whether hedge terms are present in the sentence and find out if they are true hedge terms
    for hedge in hedge_words:
        if hedge in tokenized and IsTrueHedgeTerm(hedge, text):
            status = True
            break


    # Determine whether disocurse markers are present in the n-grams
    # Use Jaccard distance for measuring similarity
    if not status:
        for A in discourse_markers:
            for B in phrases:
                if (1 - jaccard_distance(set(A.split()), set(list(B)))) >= THRESHOLD:
                    status = True
                    break

            if status:
                break

    return status
