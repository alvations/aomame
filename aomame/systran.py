import requests
from tqdm import tqdm

from aomame.exceptions import ResponseError
from aomame.utils import retry

class SystranTranslator:
    """Python SDK for
    https://rapidapi.com/systran/api/systran-io-translation-and-nlp"""
    def __init__(self, host, key):
        self.host, self.key = host, key
        self.headers = {'x-rapidapi-host': host, 'x-rapidapi-key': key}

        self.endpoints = {'lemmatize': "nlp/morphology/extract/lemma",
                          'pos': "nlp/morphology/extract/pos",
                          'langid': "nlp/lid/detectLanguage/document",
                          'ner_extract': "nlp/ner/extract/entities",
                          'ner_annotate': "nlp/ner/extract/annotations",
                          'tokenize': "nlp/segmentation/segmentAndTokenize",
                          'translate': "translation/text/translate"}
        self.urls = {k:"https://" + self.host + '/' + v for k,v in self.endpoints.items()}

    def api_call(self, operation, method, text, lang=None):
        """Wrapper class over API calls."""
        query = {"input":text,"lang":lang} if lang else {"input":text}
        response = operation(self.urls[method],
                                headers=self.headers,
                                params=query)
        return response

    def lemmatize(self, text, lang):
        output = self.api_call(requests.get, 'lemmatize', text, lang).json()
        return [(tok['text'], tok['lemma']) for tok in output['lemmas']]

    def langid(self, text):
        output = self.api_call(requests.get, 'langid', text).json()
        return [(l['lang'], l['confidence']) for l in output['detectedLanguages']]

    def ner(self, text, lang):
        return self.api_call(requests.get, 'ner_annotate', text, lang).json()

    def pos(self, text, lang):
        output = self.api_call(requests.get, 'pos', text, lang).json()
        return [(token['text'], token['pos']) for token in output['partsOfSpeech']]

    def pos_tag(self, tokenized_text, lang):
        output = self.api_call(requests.get, 'pos',  ' '.join(tokenized_text), lang).json()
        return [(token['text'], token['pos']) for token in output['partsOfSpeech']]

    def word_tokenize(self, text, lang):
        output = self.api_call(requests.get, 'tokenize', text, lang).json()
        return [token['source'] for sent in output['segments'] for token in sent['tokens']
                if token['type'] != 'separator']

    def sent_tokenize(self, text, lang):
        output = self.api_call(requests.get, 'tokenize', text, lang).json()
        return [sent['source'] for sent in output['segments']]

    def doc_tokenize(self, text, lang):
        output = self.api_call(requests.get, 'tokenize', text, lang).json()
        return [[token['source'] for token in sent['tokens'] if token['type'] != 'separator']
                for sent in output['segments']]

    @retry(Exception, tries=10, delay=1)
    def translate(self, text, srclang, trglang):
        query = {"source":srclang, "target":trglang,"input":text}
        response = requests.get(self.urls['translate'], headers=self.headers, params=query)
        return response.json()['outputs'][0]['output']

    def translate_sents(self, texts, srclang, trglang):
        return [self.translate(text, srclang, trglang) for text in tqdm(texts)]
