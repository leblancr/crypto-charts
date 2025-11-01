# fastapi-crypto
🧠 Develop on FreeBSD → 🧱 Deploy on FreeBSD.

Outside venv, no venv yet:
pyenv install 3.13.3 
pyenv local 3.13.3   # makes python=3.13.3 inside this project dir
poetry install
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
poetry add uvicorn httptools
poetry add sqlalchemy asyncpg
poetry add python-dotenv
poetry add httpx

******** Local:
source $(poetry env info --path)/bin/activate

To start backend, 9000 to avoid django's 8000:
cd /common/projects/python/crypto-charts
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 9000

pkill -f "uvicorn"

Kill anything using port 8000 automatically and restart:
kill -9 $(lsof -t -i :8000) 2>/dev/null; poetry run uvicorn backend.main:app --reload --log-level debug

Frontend:
npm create svelte@latest frontend
npm install -g npm@11.6.1
npx sv create .

Install dependencies:
npm install

Start the dev server (local):
cd /common/projects/python/crypto-charts/frontend
npm run dev

******** VPS:
That’s the production Postgres user and database:
User: crypto_dashboard_user
Password: reddcry
Database: crypto_db
Host: skyebeau.com
SSL: required

So the very first time (or after new deps are added):
cd /srv/crypto-dashboard/frontend
npm install
npm run build

After that
If you only change frontend source (no new libraries), you just:
git pull
npm run build
You don’t need npm install every time.

Or:
npm run build
npm run preview

After build:
scp -r /common/projects/crypto-dashboard/frontend/build/ rich@skyebeau.com:/srv/crypto-dashboard/frontend/
ssh rich@skyebeau.com 'sudo /usr/local/sbin/nginx -t && sudo service nginx restart'

To restart backend if it stops for some reason:
cd /srv/crypto-dashboard
nohup poetry run gunicorn backend.main:app \
  --workers 3 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:9000 \
  > gunicorn.log 2>&1 &

sudo supervisord -c /usr/local/etc/supervisord.conf

Verify and reload configs:
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status

sudo cat /usr/local/etc/supervisord.d/crypto-charts.ini

[program:crypto-charts]
command=/srv/crypto-charts/.venv/bin/gunicorn -k uvicorn.workers.UvicornWorker backend.main:app --bind 127.0.0.1:9000
directory=/srv/crypto-charts
user=rich
autostart=true
autorestart=true
stdout_logfile=/var/log/crypto_charts_access.log
stderr_logfile=/var/log/crypto_charts_error.log

to redeploy:
cd /srv/crypto-charts
git pull origin main
sudo supervisorctl restart crypto-charts

# Deploy to VPS:
# ── FastAPI (crypto-charts)
cd /srv/crypto-charts \
&& git pull --ff-only \
&& cd frontend \
&& npm ci --no-audit --no-fund \
&& npm run build \
&& cd .. \
&& . .venv/bin/activate \
&& pip install -U pip wheel setuptools \
&& poetry export -f requirements.txt --without-hashes | pip install -r /dev/stdin \
&& sudo supervisorctl restart crypto-charts \
&& sudo supervisorctl tail crypto-charts stderr

Must use tunnel on dev to appear on local vps.
To start tunnel:
ssh -N -L 5433:127.0.0.1:5432 rich@skyebeau.com

To start it in the background (so it doesn’t block the terminal):
ssh -f -N -L 5433:127.0.0.1:5432 rich@skyebeau.com

stop:
pkill -f "ssh -f -N -L 5433:127.0.0.1:5432"

shortcut in ~/.ssh/config:

Host dbvps
    HostName skyebeau.com
    User rich
    LocalForward 5433 127.0.0.1:5432
    ServerAliveInterval 60
    ServerAliveCountMax 3

ssh -f -N dbvps   # start
pkill -f dbvps    # stop

asyncpg fails build on vps so build local and use whl:
poetry run pip wheel asyncpg==0.30.0 --wheel-dir dist/
scp dist/asyncpg-0.30.0-cp313-cp313-*.whl rich@skyebeau.com:/tmp/
cd /srv/crypto-charts
source .venv/bin/activate
pip install /tmp/asyncpg-0.30.0-cp313-cp313-*.whl
python -c "import asyncpg; print(asyncpg.__version__)"







