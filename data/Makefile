.PHONY: clean list all validation

folia_merged := $(wildcard *.merged.xml)
folia_fixed := $(folia_merged:%.merged.xml=%.fixed.xml)
folia_validation := $(folia_merged:%.merged.xml=%.validation)

all: $(folia_fixed) $(folia_validation) 

clean:
	-rm alignments.lst
	-rm *.fixed.xml
	-rm *.validation

list: $(folia_merged)
	@ls $(folia_merged)

validation: $(folia_validation)

%.validation: %.fixed.xml
	xmllint --noout "$<" 2>&1 | tee "$@"
	foliavalidator "$<" 2>&1 | tee -a "$@"
	@echo "Validation report written to $@"

%.fixed.xml: %.merged.xml
	if ! ../scripts/fixfolia.py "$<" > "$@" 2> err; then cat err; false; fi
	cat err >> alignments.lst

