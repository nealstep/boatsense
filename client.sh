#!/bin/sh

DB_LIMIT=10
DB_URL='sqlite:////tmp/boatsense.db'
export DB_LIMIT
export DB_URL

python3 -m boatsense.client

