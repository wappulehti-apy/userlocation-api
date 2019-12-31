# GPS map for multiple users

Simple webapp for setting and getting locations based on user id's. Also allows sending messages to users.

## Features
* api for setting and getting user locations based (authenticated)
* api for sending messages to users based on a public_id and receiving responses (unauthenticated)

# Deployment to Heroku (example)
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
```
These can be chosen arbitrarily, as long as they are sufficiently long.

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

## Contributing

Lint your code (PEP8)
```bash
pipenv run lint
```

Run tests
```bash
pipenv run pytest
```

## License
[MIT](https://choosealicense.com/licenses/mit/)