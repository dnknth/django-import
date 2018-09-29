run: .venv
	./manage.py runserver

.venv: requirements.txt
	[ -d $@ ] || python3 -m venv $@
	$@/bin/pip3 install -r $<
	touch $@
