# GPS logger http server

GPS logger is a ready-to-deploy app to use with [GPSLogger for Android](https://gpslogger.app/) in order to serve a realtime location API. This readme describes an example Heroku setup.


## Installation

Clone the repository and use [pipenv](https://pipenv.readthedocs.io/en/latest/) or [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
git clone https://github.com/gamgi/gpslogger-http-server.git
pip install foobar
```

# Configuration
The following environment variables are available:
- `BASIC_AUTH_USERNAME` specifies username for HTTP basic auth
- `BASIC_AUTH_PASSWORD` specifies password for HTTP basic auth
- `GEO_NAME` Name for tracked object (optional)


## Deployment to Heroku (example)
### Prerequisites

Sign upp for an heorku account, downlaod the heroku CLI and log in. If you intend to run locally, you also need to install `libmemcached`.

### Create an application

```bash
heroku create --region eu <myapp>
heroku addons:create memcachier:dev
```

### Configuration

TODO

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

Lint using autopep8 or similar.
```bash
pipenv run autopep8 --in-place --aggressive --aggressive --recursive --max-line-length 250 .
```

Test using pytest
```bash
pipenv run pytest
```

## License
[MIT](https://choosealicense.com/licenses/mit/)