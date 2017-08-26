
doc-reqs:
	pip install -U -r requirements-doc.txt

doc-server:
	sphinx-autobuild docs docs/_build/html --watch service_objects

reqs:
	pip install -U -r requirements.txt

flake:
	flake8

test: flake
	python runtests.py
