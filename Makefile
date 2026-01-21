dev:
	ENV=dev uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

test:
	ENV=test uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000 

prod:
	ENV=prod uvicorn backend.app:app --host 0.0.0.0 --port 8000

