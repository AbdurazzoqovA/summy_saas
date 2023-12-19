run:
	python manage.py runserver

push:
	git add .
	git commit -m "update"
	git push 

migrate:
	python manage.py makemigrations
	python manage.py migrate