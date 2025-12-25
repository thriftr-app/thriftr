dev:
	ENV=dev fastapi dev backend/app.py

test:
	ENV=test pytest

prod:
	ENV=prod uvicorn backend.app:app

