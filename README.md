# scrapeNCBI

### Setup

1. python3 -m venv .venv
2. source .venv/bin/activate
3. pip install -U pip
4. pip install -r requirements.txt
5. create config.py file with Entrez credentials in the following format:
```
    api_key = "[API KEY HERE]"
    email = "[email/username]"
```
6. Alter the terms.json file to match the desired search terms
7. python3 scrapeNCBI.py

### Purpose

