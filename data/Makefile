.SHELLFLAGS = -o pipefail -c
.PHONY: clean list all validation stam folia.html sourcetexts

folia_merged := $(wildcard *.merged.xml)
folia_fixed := $(folia_merged:%.merged.xml=%.fixed.xml)
folia_validation := $(folia_merged:%.merged.xml=%.validation)
folia_html := $(folia_merged:%.merged.xml=%.folia.html)

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

hoof001hwva.tmpstore1.stam.json: $(folia_fixed)
	@echo "--- FoLiA to STAM conversion ---">&2
	folia2stam --id hoof001hwva -X $^
	mv hoof001hwva.store.stam.json $@

hoof001hwva.store.stam.json: hoof001hwva.tmpstore1.stam.json sourcetexts
	@echo "--- Copying ---">&2
	cp "$<" "$@"
	@echo "--- Adding source texts ---">&2
	stam annotate --resource hoof001hwva02.txt --resource hoof001hwva03.txt --resource hoof001hwva04.txt $@
	@echo "--- Realignment with source texts (1/3) ---">&2
	stam align --resource hoof001hwva02.txt $(shell ls hoof001hwva02_01_*.txt | sed -s "s/.txt//" | sed -s "s/^/--resource /" | tr "\n" " ") $@
	@echo "--- Realignment with source texts (2/3) ---">&2
	stam align --resource hoof001hwva03.txt $(shell ls hoof001hwva03_01_*.txt | sed -s "s/.txt//" | sed -s "s/^/--resource /" | tr "\n" " ") $@
	@echo "--- Realignment with source texts (3/3) ---">&2
	stam align --resource hoof001hwva04.txt $(shell ls hoof001hwva04_01_*.txt | sed -s "s/.txt//" | sed -s "s/^/--resource /" | tr "\n" " ") $@

hoof001hwva.jsonl: hoof001hwva.store.stam.json
	@echo "--- Web Annotation export ---">&2
	stam query --format w3anno --ns "folia: https://w3id.org/folia/v2/" --ns "pos: urn:brievenvanhooft:dataset/gustave-pos/" --dataset-prefix "urn:brievenvanhooft:dataset" --annotation-prefix "urn:brievenvanhooft:annotation" --resource-prefix "urn:brievenvanhooft:resource" --use "pos" --query 'SELECT ANNOTATION ?pos WHERE DATA "gustave-pos" "class";' hoof001hwva.store.stam.json > $@
	stam query --format w3anno --ns "folia: https://w3id.org/folia/v2/" --ns "lem: urn:brievenvanhooft:dataset/gustave-lem/" --dataset-prefix "urn:brievenvanhooft:dataset" --annotation-prefix "urn:brievenvanhooft:annotation" --resource-prefix "urn:brievenvanhooft:resource" --use "lem" --query 'SELECT ANNOTATION ?lem WHERE DATA "gustave-lem" "class";' hoof001hwva.store.stam.json >> $@
