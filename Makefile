CORE_DIR := ../core
RESULTS  := simulations/results
FIGURES  := figures
LATEX    := latex

.PHONY: all jar simulate figures paper clean

all: jar simulate figures paper

jar:
	cd $(CORE_DIR) && sbt assembly

simulate:
	bash simulations/scripts/run_all.sh

figures:
	python3 analysis/python/phase_diagram.py
	python3 analysis/python/topology_universality.py
	python3 analysis/python/critical_exponents.py
	python3 analysis/python/fss_scaling.py
	python3 analysis/python/decision_sensitivity.py

paper:
	cd $(LATEX) && xelatex paper_en.tex && biber paper_en && xelatex paper_en.tex && xelatex paper_en.tex

clean:
	rm -f $(RESULTS)/c1_phase/{pln,eur}/*.csv
	rm -f $(RESULTS)/c2_topology/{ws,er,ba,lattice}/{pln,eur}/*.csv
	rm -f $(RESULTS)/c3_fss/{n1000,n5000,n10000,n50000}/*.csv
	rm -f $(RESULTS)/c4_decision/{baseline,high_demo,low_demo,narrow_risk,cautious}/*.csv
	rm -f $(FIGURES)/*.png
	rm -f $(LATEX)/*.aux $(LATEX)/*.bbl $(LATEX)/*.bcf $(LATEX)/*.blg $(LATEX)/*.log $(LATEX)/*.out $(LATEX)/*.run.xml $(LATEX)/*.pdf
