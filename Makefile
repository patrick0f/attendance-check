.PHONY: test run install-cron

test:
	python3 -m pytest tests/ -v

run:
	python3 -m src.main

install-cron:
	@echo "Installing cron job for MW 2:25pm..."
	(crontab -l 2>/dev/null; echo "25 14 * * 1,3 cd $(shell pwd) && .venv/bin/python3 -m src.main >> $(shell pwd)/cron.log 2>&1") | crontab -
	@echo "Done. Verify with: crontab -l"
