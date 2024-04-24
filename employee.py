
from flask import request, jsonify, Blueprint
from flask_restful import Resource, Api, reqparse
import pymysql
import pymysql.cursors
from datetime import datetime
import os
import auth
from utils import get_connection
from flask_jwt_extended import jwt_required

bp = Blueprint('employee', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class Employee(Resource):
    def get(self):
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        sql = "SELECT * FROM employees ORDER BY created_at DESC"

        try:
            cursor.execute(sql)

            if cursor.rowcount == 0:
                return jsonify({
                    "message": "NO RECORDS FOUND"
                })
            else:
                employees = cursor.fetchall()

                for employee in employees:
                    if employee['employee_image_name']:
                        employee['image_url'] = f"{request.url_root}static/images/{employee['employee_image_name']}"
                    else:
                        employee['image_url'] = None

                return jsonify(employees)
        except Exception as e:
            return jsonify({
                "message": "ERROR OCCURRED WHILE RETRIEVING",
                "error": str(e)
            })

    @jwt_required()
    def post(self):
        try:
            data = request.form.to_dict()

            id_number = data["id_number"]
            username = data["username"]
            others = data["others"]
            salary = data["salary"]
            department = data["department"]

            employee_image = request.files['employee_image']

            if not self.allowed_file(employee_image.filename):
                raise Exception("Unsupported file type")

            max_file_size_mb = 1
            image_size = len(employee_image.read())
            employee_image.seek(0)
            if employee_image and image_size > max_file_size_mb * 1024 * 1024:
                raise Exception(f"Image file exceeds limit of 1MB")

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            employee_image_name = timestamp + '_' + employee_image.filename

            connection = get_connection()

            cursor = connection.cursor()

            sql = "INSERT INTO employees (id_number, username, others, salary, department, employee_image_name) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (id_number, username, others, salary, department, employee_image_name)

            cursor.execute(sql, data)
            connection.commit()

            os.makedirs('static/images/', exist_ok=True)
            employee_image.save('static/images/' + employee_image_name)

            return jsonify({
                "message": "Employee created successfully"
            })
        except Exception as e:
            return jsonify({
                "message": "Employee creation failed",
                "error": str(e)
            })

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @jwt_required()
    def put(self):
        data = request.json

        id_number = data["id_number"]
        salary = data["salary"]

        connection = get_connection()
        cursor = connection.cursor()

        sql = "UPDATE employees SET salary = %s WHERE id_number = %s"

        try:
            cursor.execute(sql, (salary, id_number))
            connection.commit()
            return jsonify({
                "message": "EMPLOYEE UPDATE SUCCESSFUL"
            })
        except Exception as e:
            connection.rollback()
            return jsonify({
                "message": "EMPLOYEE UPDATE FAILED",
                "error": str(e)
            })

    def delete(self):
        try:
            data = request.json
            id_number = data["id_number"]

            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

        
            # Retrieve the employee's image name from the database
            sql_select_image = "SELECT employee_image_name FROM employees WHERE id_number = %s"
            cursor.execute(sql_select_image, id_number)
            result = cursor.fetchone()

            if result:
                # Delete the employee's image file from the file system
                image_name = result["employee_image_name"]
                image_path = os.path.join("static/images/", image_name)
                if os.path.exists(image_path):
                    os.remove(image_path)

            # Delete the employee from the database
            sql_delete_employee = "DELETE FROM employees WHERE id_number = %s"
            cursor.execute(sql_delete_employee, (id_number,))
            connection.commit()

            return jsonify({
                "message": "Employee and associated image deleted successfully"
            })
        except Exception as e:
            connection.rollback()
            return jsonify({
                "message": "Deletion failed",
                "error": str(e)
            })
