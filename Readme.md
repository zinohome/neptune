# Neptune

REST API autogeneration tool for RDBMS base on fastapi and SQLAlchemy

uvicorn main:app --host 0.0.0.0 --port 8890 --reload --no-server-header --no-date-header --workers 2

gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:8890

/opt/pyAPI/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:8890
