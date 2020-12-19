venv:
	python3 -m venv venv
	. venv/bin/activate; python -m pip install --upgrade pip

.PHONY: dependencies
dependencies: venv
	. venv/bin/activate; pip install -Ur requirements.txt >/dev/null 2>&1

.PHONY: check-api-keys
check-api-keys: check-finnhub-key check-alphavantage-key

.PHONY: clean-env
clean-env:
	rm -rf venv

.PHONY: clean
clean: clean-env
