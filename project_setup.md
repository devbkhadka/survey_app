## Virtual Environment
- Create
`pyenv virtualenv 3.7.0 survey_app`

- Select `virtualenv` Project Directory
```
cd <project-dir>
pyenv local survey_app
```
## Create Djanog Project
Use cookie-cutter template as base project 
- install cookie-cutter package
`pip install "cookiecutter>=1.4.0"`

- create base project using cookiecutter-django repo
`cookiecutter https://github.com/pydanny/cookiecutter-django`
enter values asked by the cookiecutter package.
**Note**: give 'y' to 'use_whitenoise [n]' for serving static file in local machine


## Setup Postgres Database
- make sure postgres is installed and started. Below is commands to manually start or stop it
    ```
    pg_ctl -D /usr/local/var/postgres stop
        # or
    pg_ctl -D /usr/local/var/postgres stop -s -m fast


    pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
    ```
- make sure user you want to use exists 
- Create database for the project
    ```
    ## createdb <database-name> -U <user> --password <password>
    createdb survey_app -U dev --password <password>
    ```
- Set environment variable 'DATABASE_URL' as below
    ```
    # find path of virtual env using following command
    pyenv which python
    # add following line to end of the activate file (<venv-path>/bin/activate)
    export DATABASE_URL=postgres://<user>:<password>@127.0.0.1:5432/<DB name>
    ```
## Runserver
    ```
    python manage.py migrate
    python manage.py runserver
    ```


