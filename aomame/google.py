
import requests
from tqdm import tqdm

from aomame.exceptions import ResponseError

class GoogleTranslator:
    def __init__(self, host, key):
        """Python SDK for
        https://cloud.google.com/translate/docs/apis"""
        # Default host: "translation.googleapis.com"
        self.host, self.key = host, key
        self.headers = {"Content-Type": "application/json; charset=utf-8"}

        self.endpoints = {'translate': f"language/translate/v2?key={self.key}",
                          'languages': f"language/translate/v2/languages?key={self.key}",
                          'detect': f"language/translate/v2/detect?key={self.key}",
                          }

        self.urls = {k:"https://" + self.host + '/' + v for k,v in self.endpoints.items()}

    def api_call(self, operation, method, params=None, json=None):
        """Wrapper class over API calls."""
        # Add other parameters.
        url = self.urls[method] + params if params else self.urls[method]
        response = operation(url, headers=self.headers, json=json)
        return response

    def languages(self):
        response = self.api_call(requests.get, 'languages')
        return set(l['language'] for l in response.json()['data']['languages'])

    def detect(self, text):
        payload = {"q": [text]}
        response = self.api_call(requests.post, 'detect', json=payload)
        return response.json()['data']['detections'][0][0]['language']

    def translate(self, text, srclang, trglang):
        payload = {"q": [text], "target": trglang, "source": srclang, "format": "text"}
        response = self.api_call(requests.post, 'translate', json=payload)
        translation = response.json()['data']['translations'][0]['translatedText']
        return translation

    def _get_multiple_translations(self, texts, srclang, trglang):
        # Splitting texts into batches.
        # See https://cloud.google.com/translate/quotas
        responses = []
        batch = []
        len_batch = 0
        for t in tqdm(texts):
            if len_batch + len(t) < 5000 and len(batch) < 100:
                batch.append(t)
                len_batch += len(t)
            else:
                # Process this batch.
                payload = {"q": batch, "target": trglang, "source": srclang, "format": "text"}
                yield self.api_call(requests.post, 'translate', json=payload)
                # Clear this batch, prepare the next batch.
                batch = [t]
                len_batch = 0
        # Process last batch.
        if batch:
            payload = {"q": batch, "target": trglang, "source": srclang, "format": "text"}
            yield self.api_call(requests.post, 'translate', json=payload)

    def translate_sents(self, texts, srclang, trglang):
        translations = []
        for response in self._get_multiple_translations(texts, srclang, trglang):
            if response.status_code == 200:
                for t in response.json()['data']['translations']:
                    translations.append(t['translatedText'])
            else:
                raise ResponseError(response.json())
        # Sanity check to check that all sentences are translated.
        assert len(texts) == len(translations)
        return translations
