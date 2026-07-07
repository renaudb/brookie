.PHONY: run run-backend run-frontend test

run:
	@trap 'kill 0' EXIT INT TERM; \
	$(MAKE) run-backend & \
	$(MAKE) run-frontend & \
	wait

run-backend:
	uv run uvicorn brookie.main:app --reload

run-frontend:
	npm --prefix brookie-web run dev

test:
	uv run pytest
