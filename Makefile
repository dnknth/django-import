DB = db.sqlite3

run: $(DB) .venv3
	./manage.py runserver
	
load: $(DB)
	./manage.py load_fedwire
	./manage.py load_cities
	./manage.py load_tz
	./manage.py load_geoip
	./manage.py load_ips

$(DB): .venv3
	./manage.py migrate
	
.venv3: requirements.txt
	[ -d $@ ] || python3 -m venv $@
	$@/bin/pip3 install -U pip
	$@/bin/pip3 install -r $<
	touch $@

clean:
	rm -rf .venv3 $(DB)
	find . -name __pycache__ | xargs rm -rf
