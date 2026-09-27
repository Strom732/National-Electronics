# National Electronics

Django e-commerce site (products, cart, quotations, Razorpay payments, service
requests) for nationalelectronics.org.

## Local setup

```bash
python -m venv venv
source venv/bin/activate          # venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env              # then fill in real values
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

`.env` holds every secret the app needs (DB credentials, Django secret key,
email credentials, Razorpay keys). It is git-ignored on purpose — never commit
it. `.env.example` documents which variables are required.

## Production deployment

This repo doesn't run itself in production — it needs Gunicorn behind Nginx.
Templates for both are in `deploy/`:

- `deploy/systemd/nationalelectronics.service` — runs the app with Gunicorn
  as a systemd service. Adjust the paths inside it to match your server, then:

  ```bash
  sudo cp deploy/systemd/nationalelectronics.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable --now nationalelectronics
  ```

- `deploy/nginx/nationalelectronics.conf` — reverse-proxies Nginx to Gunicorn
  and serves `/static/` and `/media/` directly. See the comments at the top
  of that file for install steps and getting a TLS cert with certbot.

Before deploying, make sure `.env` on the server has `DJANGO_DEBUG=False` and
real production credentials — see the security notes below.

## Security notes

- Never commit `.env`. If credentials ever end up in git history, rotate them
  and scrub the history (e.g. with `git filter-repo`) rather than just
  deleting the line in a new commit.
- `DJANGO_DEBUG` must be `False` in production — Debug mode exposes stack
  traces, source code, and settings to any visitor on error pages.
- Razorpay payments are verified server-side via signature check before any
  order or quotation is marked paid — don't remove that verification.
