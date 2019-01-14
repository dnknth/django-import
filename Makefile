DB = db.sqlite3
BIN = .venv3/bin

run: $(DB) .venv3
	$(BIN)/python3 manage.py runserver
	
load: $(DB)
	$(BIN)/python3 manage.py load_fedwire
	$(BIN)/python3 manage.py load_cities
	$(BIN)/python3 manage.py load_tz
	$(BIN)/python3 manage.py load_geoip
	$(BIN)/python3 manage.py load_ips

$(DB): .venv3
	$(BIN)/python3 manage.py migrate
	
.venv3: requirements.txt
	[ -d $@ ] || python3 -m venv --system-site-packages $@
	$(BIN)/pip3 install -U pip
	$(BIN)/pip3 install -r $<
	touch $@

clean:
	rm -rf .venv3 $(DB)
	find . -name __pycache__ | xargs rm -rf
