.PHONY: test run install-cron setup

test:
	python3 -m pytest tests/ -v

run:
	DISPLAY=:99 python3 -m src.main

install-cron:
	@echo "Installing cron job for MW 2:25pm..."
	(crontab -l 2>/dev/null; echo "25 14 * * 1,3 cd $(shell pwd) && .venv/bin/python -m src.main >> /var/log/attendance-check.log 2>&1") | crontab -
	@echo "Done. Verify with: crontab -l"

setup:
	chmod +x setup/install.sh
	./setup/install.sh
