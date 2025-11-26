#!/bin/bash
cd "$(dirname "$0")"
echo "Starting CV Matcher..."
if ! command -v streamlit &> /dev/null; then
    echo "Streamlit not found. Installing dependencies..."
    python3 -m pip install -r requirements.txt
fi
python3 -m streamlit run app.py
