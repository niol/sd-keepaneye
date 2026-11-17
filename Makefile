.PHONY: manpages lint clean

MANPAGES = man/keepaneye.8

lint:
		black sdkeepaneye/*.py

manpages: $(MANPAGES)

man/%: man/%.md
		pandoc -s -t man -o $@ $<

clean:
		rm -f $(MANPAGES)
