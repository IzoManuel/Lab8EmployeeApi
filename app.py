from flask import Flask
from flask_restful import Resource, Api
import employee
from employee import Employee
import auth
from utils import get_connection
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager, jwt_required
from datetime import timedelta

app = Flask(__name__)

app.register_blueprint(auth.bp)
app.register_blueprint(employee.bp)

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

api = Api(app)


api.add_resource(Employee, '/employees')

app.run(debug=True, host="0.0.0.0", port=3000)