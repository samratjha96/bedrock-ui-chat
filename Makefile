.PHONY: dev prod

include .env
export

dev:
	uv sync
	uv run python -c 'from argon2 import PasswordHasher; print(PasswordHasher().hash("$(ADMIN_PASSWORD)"))' | \
		(export ADMIN_PASSWORD_HASH=$$(cat) && \
		uv run streamlit run bedrock.py)

prod:
	uv run python -c 'from argon2 import PasswordHasher; print(PasswordHasher().hash("$(ADMIN_PASSWORD)"))' | \
		docker-compose up --build