.PHONY: dev prod

dev:
	uv sync
	uv run python -c 'from argon2 import PasswordHasher; print(PasswordHasher().hash("dev_password"))' | \
		(export ADMIN_USERNAME=dev_user && \
		export ADMIN_PASSWORD_HASH=$$(cat) && \
		uv run streamlit run bedrock.py)

prod:
	docker-compose up --build
