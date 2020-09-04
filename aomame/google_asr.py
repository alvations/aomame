
import requests
from tqdm import tqdm
import base64
import json

from aomame.exceptions import ResponseError

class GoogleASR:
    def __init__(self, host, key):
        """Python SDK for
        https://cloud.google.com/speech-to-text/docs/apis"""
        # Default host: "speech.googleapis.com"
        self.host, self.key = host, key
        self.headers = {"Content-Type": "application/json; charset=utf-8"}

        self.endpoints = {'asr': f"v1/speech:recognize?key={self.key}",
                          }
        self.urls = {k:"https://" + self.host + '/' + v for k,v in self.endpoints.items()}


    def api_call(self, operation, method, params=None, json=None):
        """Wrapper class over API calls."""
        # Add other parameters.
        url = self.urls[method] + params if params else self.urls[method]
        response = operation(url, headers=self.headers, json=json)
        return response
    
    def _encode_audio(self, audio_file):
        """ Enocde audio file as Base64 string """
        with open(audio_file, "rb") as f:
            audio_encoded = base64.b64encode(f.read()) 
        return str(audio_encoded.decode("utf-8"))


    def _create_request(self, audio_file, lang):
        payload = {
          'config': {
            'encoding': 'LINEAR16',
            'sampleRateHertz': 16000,
            'languageCode': '{}'.format(lang),
            'enableAutomaticPunctuation': 'true'
          },
          'audio': {
            'content': self._encode_audio(audio_file)
          }
        }
        return payload
    
    def transcribe(self, audio_file, lang, out_file=None):
        payload = self._create_request(audio_file, lang)
        response = self.api_call(requests.post, 'asr', json=payload)
        result = response.json()

        if out_file:
            with open(out_file, 'w') as fout:
                json.dump(result, fout)
                
        if response.status_code == 200:
            if 'results' in result.keys():
                translation =  " ".join([ res['alternatives'][0]['transcript'] for res in result['results']])
            else:
                translation = ""
            return translation
        else:
            raise ResponseError(result)
    
