format:
	black streamyard_down/*
	isort streamyard_down/*

install:
	pip install -r requirements.txt