.SHELLFLAGS = -o pipefail -c
.PHONY: clean list all validation stam folia.html sourcetexts upload flush flushtextrepo flushannorepo
.DELETE_ON_ERROR:

folia_merged := $(wildcard *.merged.xml)
folia_fixed := $(folia_merged:%.merged.xml=%.fixed.xml)
folia_validation := $(folia_merged:%.merged.xml=%.validation)
folia_html := $(folia_merged:%.merged.xml=%.folia.html)

#there are three editions from DBNL
sourcetexts_2 := $(wildcard hoof001hwva02_01_*.txt)
sourcetexts_3 := $(wildcard hoof001hwva03_01_*.txt)
sourcetexts_4 := $(wildcard hoof001hwva04_01_*.txt)
sourcetexts_2_noext := $(sourcetexts_2:%.txt=%)
sourcetexts_3_noext := $(sourcetexts_3:%.txt=%)
sourcetexts_4_noext := $(sourcetexts_4:%.txt=%)
metadata_sourcetexts_2 := $(wildcard hooft_bron/hoof001hwva02_01_*.txt)
metadata_sourcetexts_3 := $(wildcard hooft_bron/hoof001hwva03_01_*.txt)
metadata_sourcetexts_4 := $(wildcard hooft_bron/hoof001hwva04_01_*.txt)


all: $(folia_fixed) $(folia_validation) stam


clean: cleanstam
	-rm alignments.lst
	-rm hoof*.fixed.xml
	-rm hoof*.validation
	-rm hoof*.folia.html

cleanstam:
	-rm hoof*.stam.json
	-rm hoof*.txt
	-rm hoof*.stam.html
	-rm *.batch
	-rm *.transpositions.tsv

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

sourcetexts: hoof001hwva02.txt hoof001hwva03.txt hoof001hwva04.txt

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

hoof001hwva.align.stam.batch: hoof001hwva.fromfolia.store.stam.json hoof001hwva02.txt hoof001hwva03.txt hoof001hwva04.txt
	for FILE in ${sourcetexts_2_noext}; do echo "align --trim --verbose --resource hoof001hwva02.txt --resource $$FILE" > $@; done
	for FILE in ${sourcetexts_3_noext}; do echo "align --trim --verbose --resource hoof001hwva03.txt --resource $$FILE" >> $@; done
	for FILE in ${sourcetexts_4_noext}; do echo "align --trim --verbose --resource hoof001hwva04.txt --resource $$FILE" >> $@; done

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

hooft_bron_align.stam.batch: hooft_bron.store.stam.json hoof001hwva02.txt hoof001hwva03.txt hoof001hwva04.txt
	for FILE in ${metadata_sourcetexts_2}; do echo "align --trim --verbose --resource hoof001hwva02.txt --resource $$FILE" > $@; done
	for FILE in ${metadata_sourcetexts_3}; do echo "align --trim --verbose --resource hoof001hwva03.txt --resource $$FILE" >> $@; done
	for FILE in ${metadata_sourcetexts_4}; do echo "align --trim --verbose --resource hoof001hwva04.txt --resource $$FILE" >> $@; done

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

hoof001hwva.jsonl: hoof001hwva.store.stam.json
	@echo "--- Web Annotation export ---">&2
	stam query --format w3anno --ns "folia: https://w3id.org/folia/v2/" --ns "pos: urn:brievenvanhooft:dataset/gustave-pos/" --dataset-prefix "urn:brievenvanhooft:dataset" --annotation-prefix "urn:brievenvanhooft:annotation" --resource-prefix "urn:brievenvanhooft:resource" --use "pos" --query 'SELECT ANNOTATION ?pos WHERE DATA "gustave-pos" "class"; [ RESOURCE "hoof001hwva02.txt" OR RESOURCE "hoof001hwva03.txt" OR RESOURCE "hoof001hwva04.txt" ];' hoof001hwva.store.stam.json > $@
	stam query --format w3anno --ns "folia: https://w3id.org/folia/v2/" --ns "lem: urn:brievenvanhooft:dataset/gustave-lem/" --dataset-prefix "urn:brievenvanhooft:dataset" --annotation-prefix "urn:brievenvanhooft:annotation" --resource-prefix "urn:brievenvanhooft:resource" --use "lem" --query 'SELECT ANNOTATION ?lem WHERE DATA "gustave-lem" "class"; [ RESOURCE "hoof001hwva02.txt" OR RESOURCE "hoof001hwva03.txt" OR RESOURCE "hoof001hwva04.txt" ];' hoof001hwva.store.stam.json >> $@

upload: hoof001hwva.jsonl hoof001hwva02.txt hoof001hwva03.txt hoof001hwva04.txt
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
	../scripts/uploader.py --textrepo-url $(TEXTREPO_URL) --textrepo-key $(TEXTREPO_KEY) --annorepo-url $(ANNOREPO_URL) --annorepo-key $(ANNOREPO_KEY) --webannotations $< hoof001hwva02.txt hoof001hwva03.txt hoof001hwva04.txt

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


	




