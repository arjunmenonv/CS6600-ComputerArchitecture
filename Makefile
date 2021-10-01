predictor:
	$(MAKE) -C sim predictor

.PHONY: tempsim
tempsim:
	$(MAKE) -C scripts tempsim

.PHONY: allsim
allsim:
	$(MAKE) -C scripts allsim

.PHONY: clean
clean:
	$(MAKE) -C sim clean

clean-results:
	rm -rf results/*
