format:
	black streamyard_down/*
	isort streamyard_down/*

install:
	pip install -e .

clean:
	rm -rf build
	rm -rf dist

dist: clean
	python setup.py sdist bdist_wheel
