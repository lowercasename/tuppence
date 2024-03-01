# Tuppence

Tuppence is a budget tracker app, designed mostly for personal use, although you are welcome to make use of it!

I built Tuppence for a couple of reasons:

- I wanted a very specific and probably distressingly unorthodox feature set combining ideas from 'classic' budgeting software and currently-trendy [envelope budgeting](https://goodbudget.com/envelope-budgeting/). This combines a transaction log, 'pots' which are distinct from accounts, and charts to track spending across 'categories'. As time goes on I may refine some of these features so they work best for my brain.
- I wanted to experiment with the beautiful ideas in [Hypermedia Systems](https://hypermedia.systems/). Tuppence makes extensive use of [htmx] (https://htmx.org/) and [Alpine.js](https://alpinejs.dev/). The Python backend returns only HTML, no JSON in sight! htmx provides in-place content refresh and allows the frontend to use a full REST API.
- I wanted to use something for budget tracking which was unflashy and simple to the point of brutalism, so I understood it front-to-back, which meant handcrafted Python with few libraries beyond Flask, an SQLite database, and no ORMs.
- I wanted something which could support multiple accounts in a safe way (magic links, no passwords!), in case any family members wanted to use it, and in case I wanted to add community/sharing features later.

It is too early to tell if Tuppence has saved me any money.

## Running Tuppence

Clone the repo, install the dependencies, and run it!

```
git clone https://github.com/lowercasename/tuppence.git
cd tuppence
pip install -r requirements.txt
python3 run.py
```

### Production

In production, I run Tuppence using Gunicorn as a systemd service, but you can use any WSGI server and runner (like pm2):

```
# /etc/systemd/system/tuppence.service

[Unit]
Description=Tuppence
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/home/raphael/tuppence
Environment="PATH=/home/raphael/tuppence/.venv/bin"
ExecStart=/home/raphael/tuppence/.venv/bin/gunicorn -w 4 run:app

[Install]
WantedBy=multi-user.target
```