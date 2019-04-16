# GPS tracker for multiple users

Simple app for setting and getting locations based on user ids.

# Configuration
The following environment variables are available:
- `BASIC_AUTH_USERNAME` specifies username for HTTP basic auth
- `BASIC_AUTH_PASSWORD` specifies password for HTTP basic auth

TODO
# Deployment to Heroku (example)
### Prerequisites

Sign upp for an heorku account, download the heroku CLI and log in.

### Create an application

```bash
heroku create --region eu <myapp>
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
```

### Configuration

To set the configuration variables,
```bash
heroku config:set BASIC_AUTH_USERNAME=<myusername>
heroku config:set BASIC_AUTH_PASSWORD=<mypassword>
heroku config:set FLASK_SECRET_KEY=<mysecretkey>
heroku config:set SALT=<mysecretsalt>
heroku config:set WEBHOOK_URL=<webhookurl>
```

### Development

Install dev-dependencies
```bash
pipenv install --dev
```

To run locally, do
```bash
docker-compose up --build
```

### Deployment

TODO

## Usage


Using GET requests:
```bash
$ curl "localhost:5000/set/123?latitude=60.16952&longitude=30.00000&initials=H%20H%20S"
{
  "success": true
}

$ curl "localhost:5000/"
{
  "sellers": [
    {
      "id": "Q18L6", 
      "initials": "B A", 
      "location": {
        "lat": "24.00000000", 
        "lon": "60.00000000"
      }
    }
  ]
}
```

## Contributing

Lint your code
```bash
pipenv run lint
```

Test using pytest
```bash
pipenv run pytest
```

## FAQ

How do I connec to the local database running in docker?
`psql -h localhost -p 9000 -U postgres postgres`

## License
[MIT](https://choosealicense.com/licenses/mit/)