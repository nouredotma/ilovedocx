#!/bin/bash
echo Installing dependencies...
pip install -r requirements.txt
echo Starting i-love-docs on http://localhost:8000
cd app && uvicorn main:app --reload --port 8000
