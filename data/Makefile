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

cleanstam:
	-rm hoof*.stam.json
	-rm hoof*.txt

list: $(folia_merged)
	@ls $^

validation: $(folia_validation)

%.validation: %.fixed.xml
	xmllint --noout "$<" 2>&1 | tee "$@"
	foliavalidator "$<" 2>&1 | tee -a "$@"
	@echo "Validation report written to $@"

%.fixed.xml: %.merged.xml
	if ! ../scripts/fixfolia.py "$<" > "$@" 2> err; then cat err; false; fi
	cat err >> alignments.lst

stam: hoof001hwva.store.stam.json

folia.html: $(folia_html)

%.folia.html: %.fixed.xml
	@#HTML visualisation via FoLiA
	folia2html $< > $@

%.stam.html: %.fixed.xml
	@#HTML visualisation via STAM
	stam view --query "SELECT RESOURCE ?letter WHERE ID \"$*\";" --query '@VALUETAG SELECT ANNOTATION ?pos WHERE RESOURCE ?letter; DATA "gustave-pos" "class";' --query '@VALUETAG SELECT ANNOTATION ?lemma WHERE RESOURCE ?letter; DATA "gustave-lem" "class";' hoof001hwva.store.stam.json > $@

hoof001hwva.store.stam.json: $(folia_fixed)
	folia2stam --id hoof001hwva -X $^
