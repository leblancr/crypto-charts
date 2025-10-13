# hfastapi-crypto
Outside venv, no venv yet:
pyenv install 3.13.3 
pyenv local 3.13.3   # makes python=3.13.3 inside this project dir
poetry install
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
poetry add uvicorn httptools
poetry add sqlalchemy asyncpg
poetry add python-dotenv
poetry add httpx

source $(poetry env info --path)/bin/activate

To start backend:
cd /common/projects/python/crypto-dashboard
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
poetry run uvicorn backend.main:app --reload

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
cd /common/projects/python/crypto-dashboard/frontend
npm run dev

VPS:
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

