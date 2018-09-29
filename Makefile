DB = db.sqlite3

run: $(DB)
	./manage.py runserver
	
load: $(DB)
	./manage.py load_fedwire
	./manage.py load_cities
	./manage.py load_tz
	./manage.py load_geoip
	./manage.py load_ips

$(DB): .venv
	./manage.py migrate
	
.venv: requirements.txt
	[ -d $@ ] || python3 -m venv $@
	$@/bin/pip3 install -r $<
	touch $@

clean:
	rm -rf .venv $(DB)
