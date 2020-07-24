from aomame import MicrosoftTranslator
from aomame import SystranTranslator
from aomame import GoogleTranslator

import sys
import argparse
import tqdm

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-api", required=True, choices=["google", "microsoft", "systran"])
    parser.add_argument("-key", required=True, help="api key")
    parser.add_argument("-i","--input-file", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file path or stdin input if empty")
    parser.add_argument("-o","--output-file", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file path or stdout output if empty")
    parser.add_argument("-slang", required=True, help="source language")
    parser.add_argument("-tlang", required=True, help="target language")
    parser.add_argument("-cs", "--cache-size", type=int, default=10000, help="number of lines to cache from file")
    args = parser.parse_args()
    return args


def translate_write(translator, cache,slang, tlang, out_file):
    #out_lines = "\n".join(["xx "+l for l in cache])
    #out_file.write("\n".join(cache) + "\n")
    out_lines = "\n".join(translator.translate_sents(cache, slang, tlang))
    out_file.write(out_lines + "\n")

def main():
    # get command line arguments
    args = get_args()

    # set API
    if args.api == "google":
        translator = GoogleTranslator("translation.googleapis.com", args.key)
    elif args.api == "microsoft":
        translator = MicrosoftTranslator('api.cognitive.microsofttranslator.com', args.key)
    elif args.api == "systran":
        translator = SystranTranslator("systran-systran-platform-for-language-processing-v1.p.rapidapi.com", args,key)
    else:
        raise NotImplementedError
    
    # translate and write/print outputs
    cache = []
    for line in tqdm.tqdm(args.input_file):
        if len(cache) < args.cache_size:
            cache.append(line.rstrip())
        else:
            translate_write(translator, cache, args.slang, args.tlang, args.output_file)
            cache = [line.rstrip()]
            #"\n".join(translator.translate_sents)
    translate_write(translator, cache, args.slang, args.tlang, args.output_file)
