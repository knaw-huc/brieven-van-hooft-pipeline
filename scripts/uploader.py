#!/usr/bin/env python

import sys
import json
import os.path
import argparse

from textrepo.client import TextRepoClient
from annorepo.client import AnnoRepoClient

PROJECT_ID="brieven-van-hooft"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Uploader", description="Uploads Web Annotations and Texts, as outputted by STAM, to AnnoRepo and TextRepo") 
    parser.add_argument('textresources', nargs='+', help="Plain text resources", type=str) 
    parser.add_argument('--textrepo-url', help="URL to the textrepo instance", type=str, action="store", required=True, default="https://brieven-van-hooft.tt.di.huc.knaw.nl/") 
    parser.add_argument('--textrepo-key', help="API key for textrepo", type=str, action="store", required=True) 
    parser.add_argument('--annorepo-url', help="URL to the annorepo instance", type=str, action="store", required=True, default="https://brieven-van-hooft.annorepo.dev.clariah.nl/") 
    parser.add_argument('--annorepo-key', help="API key for annorepo", type=str, action="store", required=True) 
    parser.add_argument('--webannotations','-a', help="Filename to a JSON List of all web annotations", type=str, action="store", required=True) 

    args = parser.parse_args()

    resource2urimap = {}

    trclient = TextRepoClient(args.textrepo_url, verbose=False, api_key=args.textrepo_key)
    arclient = AnnoRepoClient(args.annorepo_url, verbose=True,api_key=args.annorepo_key)
    AR_CONTAINER_URI = f"{args.annorepo_url}/w3c/{PROJECT_ID}"

    for textfile in args.textresources:
        external_id = ".".join(os.path.basename(textfile).split(".")[:-1]) #strip extension

        #encapsulate the plain text format in the JSON format TextRepo expects  _ordered_segments (with only one huge segment containing the whole edition)
        with open(textfile,'r',encoding='utf-8') as f:
            jsonresource = { "_ordered_segments": [ f.read() ] }
        print(f"Uploading {textfile} to TextRepo...", file=sys.stderr)
        version = trclient.import_version(external_id, type_name="segmented_text", contents=json.dumps(jsonresource, ensure_ascii=False), allow_new_document=True, as_latest_version=True)
        
        #keep the map
        resource2urimap[external_id] = f"{trclient.base_uri}/rest/versions/{version.version_id}"

    if not arclient.has_container(PROJECT_ID):
        print(f"Creating container for AnnoRepo...", file=sys.stderr)
        arclient.create_container(name=PROJECT_ID, label="Brieven van Hooft")

    chunks = []
    chunk = []
    CHUNK_SIZE = 150
    count = 0
    print(f"Processing annotations...", file=sys.stderr)
    with open(args.webannotations,'rb') as f:
        for line in f:
            webannotation = json.loads(line)

            #substitute old target resource for new URI in textrepo
            if 'source' in webannotation['target']:
                filename = webannotation['target']['source'].replace("urn:brievenvanhooft:resource/","") #strip old prefix
                uri = resource2urimap[filename]
                webannotation['target']['source'] = uri
            elif 'items' in webannotation['target']: #target may be composite:
                for item in webannotation['items']:
                    if 'source' in item:
                        filename = item['source'].replace("urn:brievenvanhooft:resource/","") #strip old prefix
                        uri = resource2urimap[filename]
                        item['source'] = uri

            if len(chunk) >= CHUNK_SIZE:
                chunks.append(chunk)
                chunk = []
            chunk.append(webannotation)
            count += 1

    print(f"Processed {count} annotations", file=sys.stderr)

    for i, chunk in enumerate(chunks):
        print(f"Uploading annotations chunk ({i + 1}/{len(chunks)}) to AnnoRepo...", file=sys.stderr)
        arclient.add_annotations(PROJECT_ID, chunk)

