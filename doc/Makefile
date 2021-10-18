pdf: report.pdf

report.pdf: report.tex ref.bib
	xelatex -pdf -shell-escape report.tex

.PHONY: clean
clean:
	latexmk -c && rm -rf report.synctex.gz && rm -f report.bbl
	rm -rf _minted-report
	rm -f report.pdf
	rm -f *.pdf_tex
