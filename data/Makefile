.SHELLFLAGS = -o pipefail -c
.PHONY: clean list all validation stam folia.html upload flush flushtextrepo flushannorepo webannotations indexannorepo
.DELETE_ON_ERROR:

folia_merged := $(wildcard *.merged.xml)
folia_fixed := $(folia_merged:%.merged.xml=%.fixed.xml)
folia_validation := $(folia_merged:%.merged.xml=%.validation)
folia_html := $(folia_merged:%.merged.xml=%.folia.html)

all: $(folia_fixed) $(folia_validation) stam

clean: cleanstam
	-rm *.lst
	-rm hoof*.fixed.xml
	-rm hoof*.validation
	-rm hoof*.folia.html

cleanstam:
	-rm hoof*.stam.json
	-rm hoof*.txt
	-rm hoof*.stam.html
	-rm hoof*.jsonl
	-rm *.batch
	-rm *.transpositions.tsv
	-rm *.edition.html

list: $(folia_merged)
	@ls $^

validation: $(folia_validation)

%.validation: %.fixed.xml
	@echo "--- FoLiA validation ---">&2
	xmllint --noout "$<" 2>&1 | tee "$@"
	foliavalidator "$<" 2>&1 | tee -a "$@"
	@echo "Validation report written to $@"

%.fixed.xml: %.merged.xml
	@echo "--- Sanitizing FoLiA input ---">&2
	if ! ../scripts/fixfolia.py "$<" > "$@" 2> err; then cat err; false; fi
	cat err >> alignments.lst

hoof001hwva02.txt:
	curl https://www.dbnl.org/nieuws/text.php\?id\=hoof001hwva02 > $@

hoof001hwva03.txt:
	curl https://www.dbnl.org/nieuws/text.php\?id\=hoof001hwva03 > $@

hoof001hwva04.txt:
	curl https://www.dbnl.org/nieuws/text.php\?id\=hoof001hwva04 > $@

stam: hoof001hwva.store.stam.json

folia.html: $(folia_html)

%.folia.html: %.fixed.xml
	@echo "--- HTML visualisation via FoLiA ---">&2
	folia2html $< > $@

%.stam.html: %.fixed.xml
	@echo "--- HTML visualisation via STAM ---">&2
	stam view --query "SELECT RESOURCE ?letter WHERE ID \"$*\";" --query '@VALUETAG SELECT ANNOTATION ?pos WHERE RESOURCE ?letter; DATA "gustave-pos" "class";' --query '@VALUETAG SELECT ANNOTATION ?lemma WHERE RESOURCE ?letter; DATA "gustave-lem" "class";' hoof001hwva.store.stam.json > $@

hoof001hwva.fromfolia.store.stam.json: $(folia_fixed)
	@echo "--- FoLiA to STAM conversion ---">&2
	folia2stam --id hoof001hwva -X $^
	mv hoof001hwva.store.stam.json $@

hoof001hwva.align.stam.batch: sourcetexts.noextension.lst
	cat $< | awk '{ print "align --trim --verbose --resource "substr($$1,1,13)".txt --resource "$$1 }' > $@

sourcetexts.lst: $(folia_fixed)
	ls hoof001hwva0?_01_*.txt > $@

sourcetexts.noextension.lst: sourcetexts.lst
	sed 's/.txt//g' < $< > $@ 

hoof001hwva.aligned.store.stam.json: hoof001hwva.fromfolia.store.stam.json hoof001hwva02.txt hoof001hwva03.txt hoof001hwva04.txt hoof001hwva.align.stam.batch
	@echo "--- Adding source texts ---">&2
	stam annotate --output $@ --resource hoof001hwva02.txt --resource hoof001hwva03.txt --resource hoof001hwva04.txt $<
	@echo "--- Realignment with source texts ---">&2
	cat hoof001hwva.align.stam.batch | stam batch $@

transpositions.tsv: hoof001hwva.aligned.store.stam.json
	stam export --alignments $< | cut -f 1,2,4 | sort -k3 | uniq > $@

transpose.stam.batch: transpositions.tsv
	cat $< | awk '{ print "transpose --ignore-errors --transposition "$$1" --query \"SELECT ANNOTATION WHERE RESOURCE "$$3";\"" }' > $@

hoof001hwva.transposed.store.stam.json: hoof001hwva.aligned.store.stam.json transpose.stam.batch
	@echo "--- Transposing annotations ---">&2
	cat transpose.stam.batch | stam batch --output $@ $<

hoof001hwva.store.stam.json: hoof001hwva.transposed.store.stam.json hooft_bron_transposed.store.stam.json 
	@echo "--- Merging annotation stores ---">&2
	stam init --output $@ $^
	@echo "--- Adding final metadata ---">&2
	python ../scripts/metadata2stam.py hooft_bron metadata $@   #existing file, will augment

hooft_bron.store.stam.json:
	-rm $@
	python ../scripts/metadata2stam.py hooft_bron metadata $@  #non-existing file, will be created

hooft_bron.lst:
	ls hooft_bron/hoof001hwva0?_01_*.txt > $@

hooft_bron_align.stam.batch: hooft_bron.lst
	cat $< | awk '{ print "align --trim --verbose --resource "substr($$1,12,13)".txt --resource "$$1 }' > $@

hooft_bron_aligned.store.stam.json: hooft_bron.store.stam.json hooft_bron_align.stam.batch
	@echo "--- Adding source texts ---">&2
	stam annotate --output $@ --resource hoof001hwva02.txt --resource hoof001hwva03.txt --resource hoof001hwva04.txt $<
	@echo "--- Aligning ---">&2
	cat hooft_bron_align.stam.batch | stam batch $@

hooft_bron_transpose.stam.batch: hooft_bron_transpositions.tsv
	cat $< | awk '{ print "transpose --ignore-errors --transposition "$$1" --query \"SELECT ANNOTATION WHERE RESOURCE "$$3";\"" }' >> $@

hooft_bron_transpositions.tsv: hooft_bron_aligned.store.stam.json
	stam export --alignments $< | cut -f 1,2,4 | sort -k3 | uniq > $@

hooft_bron_transposed.store.stam.json: hooft_bron_aligned.store.stam.json hooft_bron_transpose.stam.batch
	@echo "--- Transposing annotations ---">&2
	cat hooft_bron_transpose.stam.batch | stam batch --output $@ $<

%.edition.html: %.txt hoof001hwva.store.stam.json
	@echo "--- HTML edition visualisation via STAM ---">&2
	stam view --query "SELECT RESOURCE ?edition WHERE ID \"$<\";" --query '@VALUETAG SELECT ANNOTATION ?pos WHERE RESOURCE ?edition; DATA "gustave-pos" "class";' --query '@VALUETAG SELECT ANNOTATION ?lemma WHERE RESOURCE ?edition; DATA "gustave-lem" "class";' hoof001hwva.store.stam.json > $@

webannotations: hoof001hwva.jsonl

hoof001hwva.jsonl: hoof001hwva.store.stam.json
	@echo "--- Web Annotation export ---">&2
	stam query --format w3anno --ns "folia: https://w3id.org/folia/v2/" --ns "pos: urn:brievenvanhooft:dataset/gustave-pos/" --dataset-prefix "urn:brievenvanhooft:dataset" --annotation-prefix "urn:brievenvanhooft:annotation" --resource-prefix "https://www.dbnl.org/nieuws/text.php?id=" --use "pos" --query 'SELECT ANNOTATION ?pos WHERE DATA "gustave-pos" "class"; [ RESOURCE "hoof001hwva02.txt" OR RESOURCE "hoof001hwva03.txt" OR RESOURCE "hoof001hwva04.txt" ];' hoof001hwva.store.stam.json | sed -r 's/id=\/(hoof001hwva0[234]).txt/id=\1/g' > $@
	stam query --format w3anno --ns "folia: https://w3id.org/folia/v2/" --ns "lem: urn:brievenvanhooft:dataset/gustave-lem/" --dataset-prefix "urn:brievenvanhooft:dataset" --annotation-prefix "urn:brievenvanhooft:annotation" --resource-prefix "https://www.dbnl.org/nieuws/text.php?id=" --use "lem" --query 'SELECT ANNOTATION ?lem WHERE DATA "gustave-lem" "class"; [ RESOURCE "hoof001hwva02.txt" OR RESOURCE "hoof001hwva03.txt" OR RESOURCE "hoof001hwva04.txt" ];' hoof001hwva.store.stam.json | sed -r 's/id=\/(hoof001hwva0[234]).txt/id=\1/g' >> $@
	stam query --format w3anno --dataset-prefix "urn:brievenvanhooft:metadata" --annotation-prefix "urn:brievenvanhooft:annotation" --resource-prefix "https://www.dbnl.org/nieuws/text.php?id=" --use "meta" --query 'SELECT ANNOTATION ?meta WHERE DATA "brieven-van-hooft-categories" "part"; [ RESOURCE "hoof001hwva02.txt" OR RESOURCE "hoof001hwva03.txt" OR RESOURCE "hoof001hwva04.txt" ];' hoof001hwva.store.stam.json | sed -r 's/id=\/(hoof001hwva0[234]).txt/id=\1/g' >> $@
	stam query --format w3anno --dataset-prefix "urn:brievenvanhooft:metadata" --annotation-prefix "urn:brievenvanhooft:annotation" --resource-prefix "https://www.dbnl.org/nieuws/text.php?id=" --use "meta" --query 'SELECT ANNOTATION ?meta WHERE DATASET "brieven-van-hooft-metadata"; [ RESOURCE "hoof001hwva02.txt" OR RESOURCE "hoof001hwva03.txt" OR RESOURCE "hoof001hwva04.txt" ];' hoof001hwva.store.stam.json | sed -r 's/id=\/(hoof001hwva0[234]).txt/id=\1/g' >> $@

upload: hoof001hwva.jsonl hoof001hwva.store.stam.json hoof001hwva02.txt hoof001hwva03.txt hoof001hwva04.txt
	@echo "--- Upload data into TextRepo & AnnoRepo ---">&2
ifeq ($(TEXTREPO_URL),)
		$(error TEXTREPO_URL not set)
endif
ifeq ($(TEXTREPO_KEY),)
		$(error TEXTREPO_KEY not set)
endif
ifeq ($(ANNOREPO_URL),)
		$(error ANNOREPO_URL not set)
endif
ifeq ($(ANNOREPO_KEY),)
		$(error ANNOREPO_KEY not set)
endif
	../scripts/uploader.py --verbose --store hoof001hwva.store.stam.json --textrepo-url $(TEXTREPO_URL) --textrepo-key $(TEXTREPO_KEY) --annorepo-url $(ANNOREPO_URL) --annorepo-key $(ANNOREPO_KEY) --webannotations $< hoof001hwva02.txt hoof001hwva03.txt hoof001hwva04.txt > hoof001hwva.uploaded.jsonl

flushannorepo:
	@echo "--- Flush remote database for AnnoRepo ---">&2
ifeq ($(ANNOREPO_URL),)
		$(error ANNOREPO_URL not set)
endif
ifeq ($(ANNOREPO_KEY),)
		$(error ANNOREPO_KEY not set)
endif
	curl -I --etag-save etag --oauth2-bearer $(ANNOREPO_KEY) "$(ANNOREPO_URL)/w3c/brieven-van-hooft/"
	curl -X DELETE -H 'If-Match: $(shell cat etag)' --oauth2-bearer $(ANNOREPO_KEY) "$(ANNOREPO_URL)/w3c/brieven-van-hooft/?force=true"

flush: flushannorepo

indexannorepo:
ifeq ($(ANNOREPO_URL),)
		$(error ANNOREPO_URL not set)
endif
ifeq ($(ANNOREPO_KEY),)
		$(error ANNOREPO_KEY not set)
endif
	curl -X PUT --oauth2-bearer $(ANNOREPO_KEY) "$(ANNOREPO_URL)/services/brieven-van-hooft/indexes/body.id/hashed"
	curl -X PUT --oauth2-bearer $(ANNOREPO_KEY) "$(ANNOREPO_URL)/services/brieven-van-hooft/indexes/body.type/hashed"
	curl -X PUT --oauth2-bearer $(ANNOREPO_KEY) "$(ANNOREPO_URL)/services/brieven-van-hooft/indexes/target.source/ascending"
	curl -X PUT --oauth2-bearer $(ANNOREPO_KEY) "$(ANNOREPO_URL)/services/brieven-van-hooft/indexes/target.selector.type/ascending"
	curl -X PUT --oauth2-bearer $(ANNOREPO_KEY) "$(ANNOREPO_URL)/services/brieven-van-hooft/indexes/target.selector.start/ascending"
	curl -X PUT --oauth2-bearer $(ANNOREPO_KEY) "$(ANNOREPO_URL)/services/brieven-van-hooft/indexes/target.selector.end/ascending"


	




