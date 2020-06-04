import uuid

import requests
from tqdm import tqdm

from aomame.exceptions import ResponseError

class MicrosoftTranslator:
    """Python SDK for
    https://azure.microsoft.com/en-us/services/cognitive-services/translator/
    """
    def __init__(self, host, key):
        self.host, self.key = host, key
        # See "Add headers" section from
        # https://docs.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-translate?pivots=programming-language-python
        self.headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        # Endpoints.
        self.endpoints = {
            'translate': '/translate?api-version=3.0',
            'transliterate': '/transliterate?api-version=3.0',
            'languages': '/languages?api-version=3.0'
        }
        self.urls = {k:"https://" + self.host + '/' + v
                     for k,v in self.endpoints.items()}

        # Pre-populate the list of languages for translation.
        self._languages = self.languages()

        # Pre-populate the list of languages for transliteration
        self._scripts = self.scripts()

    def api_call(self, operation, method, params=None, json=None):
        """Wrapper class over API calls."""
        url = self.urls[method] + params if params else self.urls[method]
        response = operation(url, headers=self.headers, json=json)
        return response

    def languages(self):
        """Return list of languages available for translation."""
        reponse_json = self.api_call(requests.get, 'languages').json()
        return {lang_code:_dict['name'] for lang_code, _dict in
                reponse_json['translation'].items()}

    def scripts(self):
        """Return list of scripts available for transliteration."""
        _scripts = {}
        reponse_json = self.api_call(requests.get, 'languages').json()
        for l, details in reponse_json['transliteration'].items():
            for s in details['scripts']:
                for _s in s['toScripts']:
                    if _s['name'] == 'Hat':
                        _scripts[_s['code'].lower()] = 'Han Traditional'
                    elif _s['name'] == 'Han':
                        _scripts[_s['code'].lower()] = 'Han Simplified'
                    else:
                        _scripts[_s['code'].lower()] = _s['name']
        return _scripts

    def transliterate(self, text, srclang, from_script, to_script):
        params = f'&language={srclang}&fromScript={from_script}&toScript={to_script}'
        response = self.api_call(requests.post, 'transliterate',
                                 params=params, json=[{'Text': text}])
        if response.status_code == 200:
            return response.json()[0]['text']
        else:
            raise ResponseError(response.json())

    def translate(self, text, srclang, trglang):
        params = f'&to={srclang}&to={trglang}'
        response = self.api_call(requests.post, 'translate',
                                 params=params, json=[{'Text': text}])
        if response.status_code == 200:
            return response.json()[0]['translations'][-1]['text']
        else:
            raise ResponseError(response.json())

    def _get_multiple_translations(self, texts, srclang, trglang):
        params = f'&to={srclang}&to={trglang}'
        # Splitting texts into batches.
        # See https://docs.microsoft.com/en-us/azure/cognitive-services/translator/request-limits
        responses = []
        batch = []
        len_batch = 0
        for t in tqdm(texts):
            if len_batch + len(t) < 5000 and len(batch) < 100:
                batch.append({'Text':t})
                len_batch += len(t)
            else:
                # Process this batch.
                yield requests.post(self.urls['translate'] + params,
                                    headers=self.headers,json=batch)
                # Clear this batch, prepare the next batch.
                batch = [{'Text':t}]
                len_batch = 0
        # Process last batch.
        if batch:
            yield requests.post(self.urls['translate'] + params,
                                headers=self.headers,json=batch)

    def translate_sents(self, texts, srclang, trglang):
        translations = []
        for response in self._get_multiple_translations(texts, srclang, trglang):
            if response.status_code == 200:
                for t in response.json():
                    src = t['translations'][0]['text']
                    trg = t['translations'][1]['text']
                    translations.append((src, trg))
            else:
                raise ResponseError(response.json())
        src, trg = zip(*translations)
        # Sanity check to check that all sentences are translated.
        assert len(trg) == len(texts)
        return trg
