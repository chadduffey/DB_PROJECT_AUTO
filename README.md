# DB_PROJECT_AUTO

Requires:
Python 2.7 +
Pip

Set up dependencies:
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt

Configuration:

Configurations are loaded into the application through the use of environment variables (ENV).  When you run the app the values set in the `.env` file will get injected into the ENV so that the code can access them.  There is a sample file `.env.default` that you can use as a template to fill out the required environment variables in your own copy of the `.env` file.  For more information you read the [Heroku help doc](https://devcenter.heroku.com/articles/heroku-local).

The Dropbox CORE api work is authenticated via OAuth. 
A static business team token is required for so that non team admins may set up projects. 
The token is configured as an environment variable (OS, or Heroku) with: 

export DB_AUTH=YOURKEYHERE
(or a Heroku config variable called DB_AUTH)
 
Running:
python app.py runserver
# DB_PROJECT_AUTO

Requires:
Python 2.7 +
Pip

Set up dependencies:
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt

Configuration:

Configurations are loaded into the application through the use of environment variables (ENV).  When you run the app the values set in the `.env` file will get injected into the ENV so that the code can access them.  There is a sample file `.env.default` that you can use as a template to fill out the required environment variables in your own copy of the `.env` file.  For more information you read the [Heroku help doc](https://devcenter.heroku.com/articles/heroku-local).

The Dropbox CORE api work is authenticated via OAuth. 
A static business team token is required for so that non team admins may set up projects. 
The token is configured as an environment variable (OS, or Heroku) with: 

export DB_AUTH=YOURKEYHERE
(or a Heroku config variable called DB_AUTH)

Running:
````shell
# If you have the heroku command line tool chain you can use:
$ heroku local

# Otherwise:
$ python app.py runserver
````
