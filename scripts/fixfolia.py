#!/usr/bin/env python

"""
This is a fairly crude script to correct some of the errors present in the XML/FoLiA of Brieven van Hooft.

It output the corrected document to stdout, and the extra instructions for alignment/post-correction (see data docs) to stderr.
"""
import sys
import re
import os.path

re_getclass = re.compile("class=\"([^\"]*)\"")
re_id = re.compile("xml:id=\"([^\"]*)\"")

alt = False
split_pos = []
split_lemma = []
skip_until = None

has_lemma = False
has_pos = False
word_id = ""

filename = sys.argv[1]

with open(filename,'r', encoding='utf-8') as f:
    filename = os.path.basename(filename).replace(".merged.xml","")
    for line in f:
        if skip_until:
            if line.find(skip_until) != -1:
                skip_until = None
            continue
        if line.find("<w ") != -1:
            word_id = re.findall(re_id, line)[0]
        elif line.find("<alt") != -1 and (line.find("src=\"gustave\"") != -1 or line.find("src=\"gustave-merge\"") != -1):
            alt = True
            split_pos = []
            split_lemma = []
            has_lemma = False
            has_pos = False
            continue
        elif line.find("<pos ") != -1:
            if line.find("src=\"gustave\"") != -1:
                if has_pos:
                    print("append-pos", word_id, re.findall(re_getclass, line)[0], file=sys.stderr)
                    if line.find("/>") == -1:
                        skip_until = "</pos>"
                    continue
                has_pos = True
                line = line.replace("src=\"gustave\"","set=\"gustave-pos\"")
            elif line.find("src=\"gustave-ins\"") != -1:
                line = line.replace("src=\"gustave-ins\"","set=\"gustave-pos\"")
            elif line.find("src=\"gustave-cb\"") != -1:
                split_pos.append(re.findall(re_getclass, line)[0])
                if line.find("/>") == -1:
                    skip_until = "</pos>"
                continue
            elif line.find("set=") == -1:
                oldline = line
                line = line.replace("/>"," set=\"http://ilk.uvt.nl/folia/sets/frog-mbpos-cgn\"/>")
                if line == oldline:
                    line = line.replace(">"," set=\"http://ilk.uvt.nl/folia/sets/frog-mbpos-cgn\">")
        elif line.find("<lemma ") != -1:
            if line.find("src=\"gustave\"") != -1:
                if has_lemma:
                    print("append-lemma", word_id, re.findall(re_getclass, line)[0], file=sys.stderr)
                    continue
                has_lemma = True
                line = line.replace("src=\"gustave\"","set=\"gustave-lem\"")
            elif line.find("src=\"gustave-cb\"") != -1:
                split_lemma.append(re.findall(re_getclass, line)[0])
                if line.find("/>") == -1:
                    skip_until = "</lemma>"
                continue
            else:
                line = line.replace("/>"," set=\"http://ilk.uvt.nl/folia/sets/frog-mblem-nl\"/>")
        elif line.find("</alt>") != -1 and alt:
            if split_pos:
                print("split-pos",filename, word_id, " ".join(split_pos), file=sys.stderr)
                print("<pos class=\"%s\" set=\"gustave-pos\" />" % " ".join(split_pos))
            if split_lemma:
                print("split-lemma",filename, word_id, " ".join(split_lemma), file=sys.stderr)
                print("<lemma class=\"%s\" set=\"gustave-lem\" />" % " ".join(split_lemma))
            split_pos = []
            split_lemma = []
            alt = False
            continue
        elif line.find("<merge") != -1:
            #output merge rules to stderr
            mergerule = line.replace("<merge src=\"","").replace("dest=\"","").replace("/>","").replace("\"","").strip()
            print("merge",filename, mergerule,file=sys.stderr)
            continue
        print(line,end="")
    if skip_until:
        raise Exception("Skip until not resolved! (%s)" % skip_until)




