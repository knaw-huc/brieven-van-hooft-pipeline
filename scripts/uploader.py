#!/usr/bin/env python

import sys
import json
import os.path
import argparse
import hashlib
import stam

from datetime import datetime
from typing import Iterator
from copy import deepcopy
from collections import defaultdict

from textrepo.client import TextRepoClient
from annorepo.client import AnnoRepoClient

PROJECT_ID="brieven-van-hooft"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Uploader", description="Uploads Web Annotations and Texts, as outputted by STAM, to AnnoRepo and TextRepo") 
    parser.add_argument('textresources', nargs='+', help="Plain text resources (Resource IDs to the store)", type=str) 
    parser.add_argument('--store', help="STAM Annotation Store to load (needed to determine ordered segments)", type=str, required=True)
    parser.add_argument('--textrepo-url', help="URL to the textrepo instance", type=str, action="store", required=True, default="https://brieven-van-hooft.tt.di.huc.knaw.nl/") 
    parser.add_argument('--textrepo-key', help="API key for textrepo", type=str, action="store", required=True) 
    parser.add_argument('--annorepo-url', help="URL to the annorepo instance", type=str, action="store", required=True, default="https://brieven-van-hooft.annorepo.dev.clariah.nl/") 
    parser.add_argument('--annorepo-key', help="API key for annorepo", type=str, action="store", required=True) 
    parser.add_argument('--webannotations','-a', help="Filename to a JSON List of all web annotations", type=str, action="store", required=True) 
    parser.add_argument('--verbose','-v', help="Output updated webannotations to stdout", action="store_true")

    args = parser.parse_args()

    store = stam.AnnotationStore(file=args.store)

    resource2urimap = {}

    trclient = TextRepoClient(args.textrepo_url, verbose=False, api_key=args.textrepo_key)
    arclient = AnnoRepoClient(args.annorepo_url, verbose=False,api_key=args.annorepo_key)
    AR_CONTAINER_URI = f"{args.annorepo_url}/w3c/{PROJECT_ID}"

    #create file type
    filetype = "segmented_text"
    available_type_names = [t.name for t in trclient.read_file_types()]
    if filetype not in available_type_names:
        trclient.create_file_type(name=filetype, mimetype="application/json")

    char2segment_begin = defaultdict(dict)
    char2segment_end = defaultdict(dict)
    dbnl_date = None

    for resource_id in args.textresources:
        print(f"Processing {resource_id}...",file=sys.stderr)
        external_id = resource_id.replace('.txt','')
        dbnl_date = datetime.fromtimestamp(os.stat(resource_id).st_ctime).isoformat()

        resource = store.resource(resource_id)
        ordered_segments = resource.segmentation()

        #encapsulate the plain text format in the JSON format TextRepo expects  _ordered_segments (with only one huge segment containing the whole edition)
        with open(resource_id,'r',encoding='utf-8') as f:
            jsonresource = { "_ordered_segments":  [ str(x) for x in ordered_segments ] }
        for i, segment in enumerate(ordered_segments):
            char2segment_begin[external_id][segment.begin()] = i
            char2segment_end[external_id][segment.end() - 1] = i
        contents = json.dumps(jsonresource, ensure_ascii=False)

        print(f"Uploading {resource_id} ({len(contents.encode('utf-8'))} bytes, ID={external_id}) to TextRepo...", file=sys.stderr)
        version = trclient.import_version(external_id, type_name=filetype, contents=contents, allow_new_document=True, as_latest_version=True)
        
        #populate the map
        uri = f"{trclient.base_uri}/rest/versions/{version.version_id}"
        resource2urimap[external_id] = uri
        print(f"  Published as {uri}",file=sys.stderr)

    assert dbnl_date is not None

    if arclient.has_container(PROJECT_ID):
        print(f"Container already exists, did you intend to delete the existing container and annotations first? (make flush)", file=sys.stderr)
        sys.exit(2)
    else:
        print(f"Creating container for AnnoRepo...", file=sys.stderr)
        arclient.create_container(name=PROJECT_ID, label="Brieven van Hooft")

    arclient.set_anonymous_user_read_access(container_name=PROJECT_ID, has_read_access=True)

    chunks = []
    chunk = []
    CHUNK_SIZE = 150
    count = 0
    print(f"Processing annotations...", file=sys.stderr)
    with open(args.webannotations,'rb') as f:
        for line in f:
            webannotation = json.loads(line)

            #temporary hack because Brocolli/TAV can't deal with slashes in body IDs:
            webannotation['body']['id'] = hashlib.md5(webannotation['body']['id'].encode('utf-8')).hexdigest()

            #copy old target resource to one with new URI in textrepo
            if 'source' in webannotation['target']:
                external_id = webannotation['target']['source'].replace("https://www.dbnl.org/nieuws/text.php?id=","") #strip old prefix
                if external_id not in resource2urimap:
                    print(f"[error] File '{external_id}' is not a known target, must be one of the text resources passed",file=sys.stderr)
                    sys.exit(1)
                uri = resource2urimap[external_id]
                textrepo_copy = deepcopy(webannotation['target'])
                textrepo_copy['source'] = uri
                textrepo_copy['type'] = "Text"
                begin = textrepo_copy['selector']['start']
                startsegment = char2segment_begin[external_id][begin]
                end = textrepo_copy['selector']['end'] - 1 #inclusive end (W3C Anno is exclusive, so -1)
                endsegment = char2segment_end[external_id][end]
                textrepo_copy['selector'] = {
                    "@context": "https://knaw-huc.github.io/ns/huc-di-tt.jsonld",
                    "type": "TextAnchorSelector",
                    "start": startsegment, #segment index
                    "end": endsegment, #segment inclusive-end
                }
                view_uri = uri.replace('/rest/','/view/')
                #add a timestate to the DBNL source, corresponding to when we fetched it (it might change in the future rendering all offsets invalid)
                webannotation['target']['state'] = {
                    "type": "TimeState",
                    "sourceDate": dbnl_date,
                }
                webannotation['target'] = [ webannotation['target'], textrepo_copy, {
                    "source": f"{view_uri}/segments/index/{startsegment}/{endsegment}",
                    "type": "Text"
                }]
            elif 'items' in webannotation['target']: #target may be composite:
                textrepo_copy = deepcopy(webannotation['target'])
                textrepo_copy['items'] = []
                textrepo_copy2= deepcopy(webannotation['target'])
                textrepo_copy2['items'] = []
                for item in webannotation['target']['items']:
                    if 'source' in item:
                        external_id = item['source'].replace("https://www.dbnl.org/nieuws/text.php?id=","") #strip old prefix
                        if external_id not in resource2urimap:
                            print(f"[error] File '{external_id}' is not a known target, must be one of the text resources passed",file=sys.stderr)
                            sys.exit(1)
                        uri = resource2urimap[external_id]
                        item_copy = deepcopy(item)
                        item_copy['source'] = uri
                        item_copy['type'] = "Text"
                        begin = item_copy['selector']['start']
                        startsegment = char2segment_begin[external_id][begin]
                        end = item_copy['selector']['end'] - 1 #inclusive end (W3C Anno is exclusive, so -1)
                        endsegment = char2segment_end[external_id][end]
                        item_copy['selector'] = {
                            "@context": "https://knaw-huc.github.io/ns/huc-di-tt.jsonld",
                            "type": "TextAnchorSelector",
                            "start": startsegment, #segment index
                            "end": endsegment, #segment inclusive-end
                        }
                        textrepo_copy['items'].append(item_copy)
                        view_uri = uri.replace('/rest/','/view/')
                        textrepo_copy2['items'].append(
                            {
                                "source": f"{view_uri}/segments/index/0/{begin}/0/{end}",
                                "type": "Text"
                            }
                        )
                webannotation['target'] = [ webannotation['target'], textrepo_copy, textrepo_copy2 ]

            if len(chunk) >= CHUNK_SIZE:
                chunks.append(chunk)
                chunk = []
            chunk.append(webannotation)
            if args.verbose:
                json.dump(webannotation, sys.stdout)
                sys.stdout.write("\n")
            count += 1

    print(f"Processed {count} annotations", file=sys.stderr)

    for i, chunk in enumerate(chunks):
        print(f"Uploading annotations chunk ({i + 1}/{len(chunks)}) to AnnoRepo...", file=sys.stderr)
        arclient.add_annotations(PROJECT_ID, chunk)

