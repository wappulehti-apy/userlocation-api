# User Location API
.. project-description-start

An API built to serve two purposes:

* Serving user location data for use in a map
* Allowing message exchange between users and clients

A proven example use case is listing locations of sellers on a hyperlocal map, and allowing customers (clients)
to request a callback phonecall from a user of their choice.
A fully working system requires an additional way of relying messages to and from users, that is implemented
as a webhook. The webhook is called by the User Location API.

.. project-description-end
## Documentation

API reference is available in the [project docs](https://wappulehti-apy.github.io/userlocation-api/index.html).

## Running locally (docker)

To run locally, do
```bash
cp .env.sample .env
docker-compose up --build
```

A local testing interface should be available at http://localhost:5000.

## Deployment to Heroku (example)
### Prerequisites

Sign upp for an heroku account, download the heroku CLI and log in.

### Create an application

```bash
heroku create --region eu <myapp>
heroku addons:create heroku-redis:hobby-dev
```

### Configuration

To set the configuration variables,
```bash
heroku config:set BASIC_AUTH_USERNAME=<myusername>
heroku config:set BASIC_AUTH_PASSWORD=<mypassword>
heroku config:set FLASK_SECRET_KEY=<mysecretkey>
heroku config:set SALT=<mysecretsalt>
heroku config:set WEBHOOK_URL=<mymessagewebhookurl>
heroku config:set CORS_ORIGINS=http://mywebsite.com,localhost:5000
```
Most of these can be chosen arbitrarily, as long as they are sufficiently long.

### Deployment using git

Set the remote url.
```bash
heroku git:remote -a <myapp>
```
Deploy to heroku.
```bash
git push heroku master
```

Wait until deployment has succeeded (failed).

Check if it works.
```bash
curl "https://<myapp>.herokuapp.com/locations"
```

## Development

Install dev-dependencies
```bash
pipenv install --dev
```

Lint your code (PEP8)
```bash
pipenv run lint
```

Run tests
```bash
pipenv run pytest
```

Generate docs (local)
```bash
cd docsrc/;pipenv run make html
```

Generate docs (build)
```bash
cd docsrc/;pipenv run make github
```

## License
[MIT](https://choosealicense.com/licenses/mit/)