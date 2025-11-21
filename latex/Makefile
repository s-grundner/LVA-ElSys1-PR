# Makefile for building the LaTeX project in this directory
# Usage:
#   make          # build the default PDF
#   make all
#   make clean    # remove aux files
#   make distclean# remove aux files and PDFs
#   make watch    # continuously build (requires latexmk)
#   make view     # open the produced PDF with system default (xdg-open/open)
#   make help
#
# This Makefile prefers latexmk when available, otherwise falls back to
# a pdflatex -> bibtex -> pdflatex* flow.

# Main TeX source (change if you want a different main file)
MAIN := ElSys1_Protokoll_k12136610_2.tex
OUT := $(MAIN:.tex=.pdf)

# Tools (allow overriding on command line)
LATEX := pdflatex
BIB    := bibtex
LATEXMK := $(shell command -v latexmk 2>/dev/null || true)
OPENCMD := $(shell command -v xdg-open 2>/dev/null || command -v open 2>/dev/null || true)

# LaTeX flags
LATEXFLAGS := -interaction=nonstopmode -halt-on-error -file-line-error
LATEXMKFLAGS := -pdf -interaction=nonstopmode -file-line-error -silent

# Collect sources so `make` notices changes (wildcard includes common files/dirs)
TEX_SRCS := $(wildcard *.tex)
BIB_SRCS := $(wildcard *.bib)
STY_SRCS := $(wildcard *.sty)
IMG_SRCS := $(wildcard images/* logos/*)

.PHONY: all default help clean distclean watch view

default: all

# Prefer latexmk if available
ifeq ($(LATEXMK),)
all: $(OUT)

# Build sequence when latexmk isn't available
# Run pdflatex -> bibtex (if .aux indicates) -> pdflatex x2
$(OUT): $(TEX_SRCS) $(BIB_SRCS) $(STY_SRCS) $(IMG_SRCS)
	@echo "Building PDF with $(LATEX) (latexmk not found)..."
	$(LATEX) $(LATEXFLAGS) $(MAIN)
	@if grep -q "Citation" $(MAIN:.tex=.log) 2>/dev/null || true; then \
		$(BIB) $(MAIN:.tex=); \
	fi
	$(LATEX) $(LATEXFLAGS) $(MAIN)
	$(LATEX) $(LATEXFLAGS) $(MAIN)
	@echo "Built: $(OUT)"

clean:
	@echo "Removing auxiliary files..."
	-rm -f *.aux *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk *.bbl *.blg *.bcf *.run.xml *.synctex.gz

distclean: clean
	@echo "Removing generated PDF(s)..."
	-rm -f $(OUT)

watch:
	@echo "watch target requires latexmk; not available on this system."
	@exit 1

view:
ifeq ($(OPENCMD),)
	@echo "No open command found (xdg-open/open). Please open $(OUT) manually."
else
	$(OPENCMD) $(OUT) &
endif

else
# latexmk is available: use it for builds, cleaning and continuous mode
all: $(OUT)

$(OUT): $(TEX_SRCS) $(BIB_SRCS) $(STY_SRCS) $(IMG_SRCS)
	@echo "Building with latexmk..."
	$(LATEXMK) $(LATEXMKFLAGS) $(MAIN)
	@echo "Built: $(OUT)"

clean:
	@echo "Cleaning auxiliary files via latexmk..."
	-$(LATEXMK) -c $(MAIN)
	# latexmk -c removes many aux files but leaves .pdf

distclean: clean
	@echo "Removing generated PDF(s)..."
	-$(LATEXMK) -C $(MAIN)
	-@rm -f $(OUT)

watch:
	@echo "Starting continuous build (latexmk -pvc)..."
	$(LATEXMK) -pvc $(LATEXMKFLAGS) $(MAIN)

view:
ifeq ($(OPENCMD),)
	@echo "No open command found (xdg-open/open). Please open $(OUT) manually."
else
	$(OPENCMD) $(OUT) &
endif

endif

help:
	@echo "Makefile targets:"
	@echo "  make, make all      Build the main PDF ($(MAIN))"
	@echo "  make clean          Remove LaTeX auxiliary files"
	@echo "  make distclean      Remove auxiliary files and generated PDF(s)"
	@echo "  make watch          Continuous build (requires latexmk)"
	@echo "  make view           Open produced PDF with system default viewer"
	@echo "  make help           Show this help message"
	@echo ""
	@echo "You can override tools on the command line, e.g.:"
	@echo "  make LATEX=pdflatex BIB=bibtex"
