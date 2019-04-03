from flask import Flask
app = Flask(__name__)
app.config.from_object('config.Config')


@app.route('/')
def hello():
    return "Hello World!" + app.config['API_VERSION']


if __name__ == '__main__':
    app.run()
