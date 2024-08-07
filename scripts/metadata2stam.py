#!/usr/bin/env python

import sys
import stam
import os.path
import csv
from collections import defaultdict
from glob import glob
from enum import Enum

class Mode(Enum):
    PRE = 0 #pre-transposition/alignment, will create a new annotation store from scratch
    POST = 1 #post-transposition/alignment, will enrich an existing annotation store

EDITIONS = ("hoof001hwva02.txt","hoof001hwva03.txt","hoof001hwva04.txt")

try:
    sourcedir = sys.argv[1]
    assert os.path.isdir(sourcedir)
except:
    print("First argument must be source directory (../input/hooft_bron)")
    exit(1)

try:
    metadatadir = sys.argv[2]
    assert os.path.isdir(metadatadir)
except:
    print("Second argument must be metadata directory (../input/metadata)")
    exit(1)

try:
    storefile = sys.argv[3]
except:
    print("Third argument must be store file (hooft_bron.store.stam.json). Either a new one to generate (pre-transposition) or an existing one to enrich (post-transposition)")
    exit(1)

if os.path.exists(storefile):
    mode = Mode.POST
    store = stam.AnnotationStore(file=storefile)
else:
    mode = Mode.PRE
    store = stam.AnnotationStore(id="hooft_bron")
    store.set_filename(storefile)

    for filename in glob(os.path.join(sourcedir,"*.txt")):
        store.add_resource(filename)

correspondents = {}
with open(os.path.join(metadatadir,"correspondents.csv")) as csvfile:
    for row in csv.DictReader(csvfile):
        correspondents[row['id']] = row

letters = {}
with open(os.path.join(metadatadir,"letters.csv")) as csvfile:
    for row in csv.DictReader(csvfile):
        letters[row['dbnl_id']] = row

letters_mapped = defaultdict(dict)
if mode == Mode.POST:
    begin = None
    end = None

    for transposition in store.annotations(set="https://w3id.org/stam/extensions/stam-transpose/", key="Transposition"):
        targetside, sourceside = transposition.annotations_in_targets()
        sourceresource_id = sourceside.resources()[0].id()
        targetresource_id = targetside.resources()[0].id()
        assert sourceresource_id is not None
        assert targetresource_id is not None
        if sourceresource_id.startswith("input/hooft_bron/") and targetresource_id in EDITIONS:
            dbnl_id = sourceresource_id[len("input/hooft_bron/"):-4]

            begin = letters_mapped[dbnl_id].get(begin)
            end = letters_mapped[dbnl_id].get(end)
            for textselection in targetside.textselections():
                if begin is None:
                    begin = textselection.begin()
                else:
                    begin = min(textselection.begin(),begin)
                if end is None:
                    end = textselection.end()
                else:
                    end = max(textselection.end(),end)

            if begin and end:
                print(dbnl_id,"->", f"{targetresource_id}#{begin}-{end}", file=sys.stderr)
                letters_mapped[dbnl_id]['begin'] = begin
                letters_mapped[dbnl_id]['end'] = end
                letters_mapped[dbnl_id]['resource_id'] = targetresource_id

if mode == Mode.POST:
    #tier0 annotations are required for Broccoli/Brinta/TAV
    for i, edition in enumerate(EDITIONS):
        resource = store.resource(edition)
        target = stam.Selector.textselector(resource, stam.Offset.whole())
        dbnl_id = edition.replace(".txt","")
        store.annotate(target, [
            {
                "set": "http://www.w3.org/ns/anno/",
                "key": "type",
                "value": "File"
            },
            {
                "set": "brieven-van-hooft-metadata",
                "key": "dbnl_id",
                "value": f"{dbnl_id}"
            },
            {
                "set": "brieven-van-hooft-metadata",
                "key": "volume",
                "value": f"{i+1}"
            }
        ], id=dbnl_id)


categories = {}
with open(os.path.join(metadatadir,"categories.csv")) as csvfile:
    for row in csv.DictReader(csvfile):
        categories[row['dbnl_id']] = row

dbnl_ids = set(categories.keys()) | set(letters_mapped.keys())

for dbnl_id in dbnl_ids:
    letter_filename = f"input/hooft_bron/{dbnl_id}.txt"
    if mode == Mode.PRE:
        resource = store.resource(letter_filename)
        target = stam.Selector.resourceselector(resource)
    elif mode == Mode.POST:
        if 'resource_id' in letters_mapped[dbnl_id]:
            resource = store.resource(letters_mapped[dbnl_id]['resource_id'])
            begin = letters_mapped[dbnl_id]['begin']
            end = letters_mapped[dbnl_id]['end']
            target = stam.Selector.textselector(resource, stam.Offset.simple(begin,end) )
        else:
            print(f"WARNING: No resource found for {dbnl_id} ..skipping!", file=sys.stderr)
            continue
    else:
        raise Exception("Invalid mode")

    data = [
        {
            "set": "http://www.w3.org/ns/anno/",
            "key": "type",
            "value": "Letter"
        },
        {
            "set": "brieven-van-hooft-metadata",
            "key": "dbnl_id",
            "value": dbnl_id
        }
    ]
    if dbnl_id in letters:
        data += [
            {
                "set": "brieven-van-hooft-metadata",
                "key": "letter_id",
                "value": letters[dbnl_id]['id']
            },
            {
                "set": "brieven-van-hooft-metadata",
                "key": "dated",
                "value": letters[dbnl_id]['dated']
            }
        ]
        if all(x['key'] != 'letter_id' for x in data):
            data.append({
                "set": "brieven-van-hooft-metadata",
                "key": "letter_id",
                "value": letters[dbnl_id]['id']
            })
        correspondent_id = letters[dbnl_id]['to_id']
        if correspondent_id not in correspondents:
            print(f"WARNING: Correspondent ID {correspondent_id} was not defined.. Skipping", file=sys.stderr)
        else:
            data += [
                {
                    "set": "brieven-van-hooft-metadata",
                    "key": "correspondent_id",
                    "value": correspondent_id
                },
                {
                    "set": "brieven-van-hooft-metadata",
                    "key": "recipient",
                    "value": correspondents[correspondent_id]['name']
                },
                {
                    "set": "brieven-van-hooft-metadata",
                    "key": "function",
                    "value": correspondents[correspondent_id]['function']
                },
                {
                    "set": "brieven-van-hooft-metadata",
                    "key": "invidividual",
                    "value": True if correspondents[correspondent_id]['individual'] == "1" else False,
                },
                {
                    "set": "brieven-van-hooft-metadata",
                    "key": "literary",
                    "value": True if correspondents[correspondent_id]['function_unclear'] == "1" else False,
                }
            ]
            if correspondents[correspondent_id]['individual'] == "1":
                data.append({
                    "set": "brieven-van-hooft-metadata",
                    "key": "gender",
                    "value": "female" if correspondents[correspondent_id]['gender'] == "1" else "male",
                })
                if correspondents[correspondent_id]['birthyear'] != 0:
                    data.append(
                        {
                            "set": "brieven-van-hooft-metadata",
                            "key": "birthyear",
                            "value": int(correspondents[correspondent_id]['birthyear']),
                        }
                    )
                if correspondents[correspondent_id]['deathyear'] != 0:
                    data.append(
                        {
                            "set": "brieven-van-hooft-metadata",
                            "key": "deathyear",
                            "value": int(correspondents[correspondent_id]['deathyear']),
                        }
                    )
                data.append(
                    {
                        "set": "brieven-van-hooft-metadata",
                        "key": "literary",
                        "value": True if correspondents[correspondent_id]['literary'] == "1" else False,
                    }
                )
                data.append(
                    {
                        "set": "brieven-van-hooft-metadata",
                        "key": "birthyear_unclear",
                        "value": True if correspondents[correspondent_id]['birthyear_unclear'] == "1" else False,
                    }
                )
                data.append(
                    {
                        "set": "brieven-van-hooft-metadata",
                        "key": "deathyear_unclear",
                        "value": True if correspondents[correspondent_id]['deathyear_unclear'] == "1" else False,
                    }
                )
    else:
        print(f"WARNING: DBNL ID {dbnl_id} was not defined in letters.csv.. No further metadata associated!", file=sys.stderr)
    if dbnl_id in categories:
        data += [
            {
                "set": "brieven-van-hooft-categories",
                "key": "type",
                "value": "business" if categories[dbnl_id]['business'] == "1" else "private"
            },
            {
                "set": "brieven-van-hooft-categories",
                "key": "dependency",
                "value": "independent" if categories[dbnl_id]['accompanying'] == "0" else "accompanying"
            },
             {
                "set": "brieven-van-hooft-categories",
                "key": "function",
                "value": categories[dbnl_id]['function']
            },
             {
                "set": "brieven-van-hooft-categories",
                "key": "topic",
                "value": categories[dbnl_id]['topic']
            }
        ]
        
    kwargs = {}
    if mode == Mode.POST:
        kwargs['id'] = dbnl_id

    store.annotate(target, data, **kwargs)

    if mode == Mode.PRE and dbnl_id in categories:
        row = categories[dbnl_id]
        if row['greeting_start'] != "" and row['greeting_end'] != "":
            target = stam.Selector.textselector(resource, stam.Offset.simple(int(row['greeting_start']), int(row['greeting_end'])))
            store.annotate(target, {
                "set": "brieven-van-hooft-categories",
                "key": "part",
                "value": "greeting"
            })
        if row['opening_start'] != "" and row['opening_end'] != "":
            target = stam.Selector.textselector(resource, stam.Offset.simple(int(row['opening_start']), int(row['opening_end'])))
            store.annotate(target, {
                "set": "brieven-van-hooft-categories",
                "key": "part",
                "value": "opening"
            })
        if row['narratio_start'] != "" and row['narratio_end'] != "":
            target = stam.Selector.textselector(resource, stam.Offset.simple(int(row['narratio_start']), int(row['narratio_end'])))
            store.annotate(target, {
                "set": "brieven-van-hooft-categories",
                "key": "part",
                "value": "narratio"
            })
        if row['closing_start'] != "" and row['closing_end'] != "":
            target = stam.Selector.textselector(resource, stam.Offset.simple(int(row['closing_start']), int(row['closing_end'])))
            store.annotate(target, {
                "set": "brieven-van-hooft-categories",
                "key": "part",
                "value": "closing"
            })
        if row['finalgreeting_start'] != "" and row['finalgreeting_end'] != "":
            target = stam.Selector.textselector(resource, stam.Offset.simple(int(row['finalgreeting_start']), int(row['finalgreeting_end'])))
            try:
                store.annotate(target, {
                    "set": "brieven-van-hooft-categories",
                    "key": "part",
                    "value": "finalgreeting"
                })
            except Exception as err:
                print(f"WARNING: Finalgreeting cursor out of bounds: {err}", file=sys.stderr)


store.save()
