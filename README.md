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

To start:
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000


