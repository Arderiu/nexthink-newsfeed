# Nexthink IT Newsfeed — Assignment

## Overview
A lightweight system that aggregates IT-related news, filters relevant items for IT managers, and exposes them through a minimal API compatible with the assignment’s automated tests.  


## Running the Project
Create a conda environment:
```
conda create --name nexthink_challenge python=3.12
```

Install dependencies:
```
pip install -r requirements.txt
```

Start the news fetcher and the Mock Newsfeed API:
```
bash run.sh
```

This script launches:
   - The periodic news ingestion
   - The API exposing the required /ingest and /retrieve endpoints


## Tests
Run tests: 
```
pytest
```