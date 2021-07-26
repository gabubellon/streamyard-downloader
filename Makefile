format:
	black .
	isort .

install:
	pip install -r requirements.txt

run:
	python src/down_streamyard.py