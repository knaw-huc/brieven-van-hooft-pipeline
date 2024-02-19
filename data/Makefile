.SHELLFLAGS = -o pipefail -c
.PHONY: clean list all validation stam folia.html

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

stam: hoof001hwva.store.stam.json

folia.html: $(folia_html)

%.folia.html: %.fixed.xml
	@echo "--- HTML visualisation via FoLiA ---">&2
	folia2html $< > $@

%.stam.html: %.fixed.xml
	@echo "--- HTML visualisation via STAM ---">&2
	stam view --query "SELECT RESOURCE ?letter WHERE ID \"$*\";" --query '@VALUETAG SELECT ANNOTATION ?pos WHERE RESOURCE ?letter; DATA "gustave-pos" "class";' --query '@VALUETAG SELECT ANNOTATION ?lemma WHERE RESOURCE ?letter; DATA "gustave-lem" "class";' hoof001hwva.store.stam.json > $@

hoof001hwva.store.stam.json: $(folia_fixed)
	@echo "--- FoLiA to STAM conversion ---">&2
	folia2stam --id hoof001hwva -X $^

hoof001hwva.jsonl: hoof001hwva.store.stam.json
	@echo "--- Web Annotation export ---">&2
	stam query --format w3anno --ns "folia: https://w3id.org/folia/v2/" --ns "pos: urn:brievenvanhooft:dataset/gustave-pos/" --dataset-prefix "urn:brievenvanhooft:dataset" --annotation-prefix "urn:brievenvanhooft:annotation" --resource-prefix "urn:brievenvanhooft:resource" --use "pos" --query 'SELECT ANNOTATION ?pos WHERE DATA "gustave-pos" "class";' hoof001hwva.store.stam.json > $@
	stam query --format w3anno --ns "folia: https://w3id.org/folia/v2/" --ns "lem: urn:brievenvanhooft:dataset/gustave-lem/" --dataset-prefix "urn:brievenvanhooft:dataset" --annotation-prefix "urn:brievenvanhooft:annotation" --resource-prefix "urn:brievenvanhooft:resource" --use "lem" --query 'SELECT ANNOTATION ?lem WHERE DATA "gustave-lem" "class";' hoof001hwva.store.stam.json >> $@
