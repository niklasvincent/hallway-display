#!/bin/bash -x

. venv/bin/activate
env $(cat .env-production| xargs) python3 wsgi.py