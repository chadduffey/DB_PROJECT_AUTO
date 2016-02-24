# DB_PROJECT_AUTO

Requires:
Python 2.7 +
Pip

Set up dependencies:
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt

*The core api work is authenticated via OAuth, However a static team token is configured for the application so that non team admins may set up projects. This feature relies on an environment variable (either in OS, or Heroku): 

export DB_AUTH=YOURKEYHERE
(config variable called DB_AUTH on Heroku)

Running:
python app.py runserver