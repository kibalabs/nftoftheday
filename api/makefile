install:
	@ pip install -r requirements.txt -r requirements-dev.txt

list-outdated: install
	@ pip list -o

lint-check:
	@ lint --directory ./notd

lint-check-ci:
	@ lint --directory ./notd --output-file lint-check-results.json --output-format annotations

lint-fix:
	@ isort --sl -l 1000 ./notd
	@ lint --directory ./notd

type-check:
	@ type-check --directory ./notd

type-check-ci:
	@ type-check --directory ./notd --output-file type-check-results.json --output-format annotations

security-check:
	@ security-check --directory ./notd

security-check-ci:
	@ security-check --directory ./notd --output-file security-check-results.json --output-format annotations

build:
	@ echo "Not Supported"

start:
	@ uvicorn application:app --host 0.0.0.0 --port 5000 --no-access-log --reload

start-prod:
	@ uvicorn application:app --host 0.0.0.0 --port 5000 --no-access-log

start-worker:
	@ python3 worker.py

test:
	@ echo "Not Supported"

clean:
	@ rm -rf ./.mypy_cache ./__pycache__ ./build ./dist

.PHONY: *
