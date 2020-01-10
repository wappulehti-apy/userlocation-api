# Equivalent to `flask run --host=0.0.0.0`
import api
app = api.create_app()
app.run(debug=True, host='0.0.0.0')