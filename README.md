# infdz
This is a django website for collecting user responses and generating reports.

## Deploy
1. clone project
2. `cd infdz`
3. `cp {.example,}.env`
4. edit .env for your environment
5. `docker-compose up`
6. Create superuser: `docker-compose exec django python manage.py createsuperuser`
