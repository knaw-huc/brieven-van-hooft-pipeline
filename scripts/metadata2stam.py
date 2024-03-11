#!/usr/bin/env python

import sys
import stam
import os.path
import csv
from glob import glob

try:
    sourcedir = sys.argv[1]
    assert os.path.isdir(sourcedir)
except:
    print("First argument must be source directory (../hooft_bron)")
    exit(1)

try:
    metadatadir = sys.argv[2]
    assert os.path.isdir(metadatadir)
except:
    print("First argument must be metadata directory (../metadata)")
    exit(1)

store = stam.AnnotationStore(id="hooft_bron")
store.set_filename("hooft_bron.stam.store.json")

for filename in glob(os.path.join(sourcedir,"*.txt")):
    store.add_resource(filename)

correspondents = {}
with open(os.path.join(metadatadir,"correspondents.csv")) as csvfile:
    for row in csv.DictReader(csvfile):
        correspondents[row['id']] = row

letters = {}
with open(os.path.join(metadatadir,"letters.csv")) as csvfile:
    for row in csv.DictReader(csvfile):
        letters[row['id']] = row

with open(os.path.join(metadatadir,"categories.csv")) as csvfile:
    for row in csv.DictReader(csvfile):
        dbnl_id = f"hooft_bron/{row['dbnl_id']}.txt"
        resource = store.resource(dbnl_id)
        target = stam.Selector.resourceselector(resource)
        store.annotate(target, {
            "set": "brieven-van-hooft-categories",
            "key": "type",
            "value": "business" if row['business'] == "1" else "private"
        })
        store.annotate(target, {
            "set": "brieven-van-hooft-categories",
            "key": "dependency",
            "value": "independent" if row['accompanying'] == "0" else "accompanying"
        })
        store.annotate(target, {
            "set": "brieven-van-hooft-categories",
            "key": "function",
            "value": row['function']
        })
        store.annotate(target, {
            "set": "brieven-van-hooft-categories",
            "key": "topic",
            "value": row['topic']
        })
        target = stam.Selector.textselector(resource, stam.Offset.whole())
        store.annotate(target, {
            "set": "brieven-van-hooft-metadata",
            "key": "dbnl_id",
            "value": dbnl_id
        })
        store.annotate(target, {
            "set": "brieven-van-hooft-metadata",
            "key": "dated",
            "value": letters[row['id']]['dated']
        })
        correspondent_id = letters[row['id']]['to_id']
        if correspondent_id not in correspondents:
            print(f"WARNING: Correspondent ID {correspondent_id} was not defined.. Skipping", file=sys.stderr)
        else:
            data = [
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
            store.annotate(target, data)

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
