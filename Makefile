.PHONY: lint pdf send

lint:
	poetry run pytest -q

pdf:
	poetry run python src/fetch_summaries.py
	poetry run python src/render_pdf.py

send:
	poetry run python src/send_digest.py
