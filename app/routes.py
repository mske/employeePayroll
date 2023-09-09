import csv
import os.path
from collections import defaultdict
from datetime import datetime
from pprint import pprint

from flask import render_template, request, jsonify
from app import app, db
from app.models import TimeReport


def convert_date_string(date_string):
    date_format = '%d/%m/%Y'
    date_object = datetime.strptime(date_string, date_format)
    return date_object.date()


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/upload", methods=['POST'])
def upload_time_report():
    # Create 'data' folder if it doesn't exist
    data_folder = 'data'
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file:
            filename = uploaded_file.filename
            for name in os.listdir('./data'):
                if name.split('.')[0] == filename.split('.')[0]:
                    return jsonify(message="File with same name already exists")

            # Save the uploaded file
            file_path = os.path.join("data", filename)
            uploaded_file.save(file_path)

            try:
                with open(file_path, 'r') as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    for row in csv_reader:
                        print(row)
                        date = convert_date_string(row['date'])
                        hours_worked = row['hours worked']
                        employee_id = row['employee id']
                        job_group = row['job group']
                        time_report = TimeReport(date, hours_worked, employee_id, job_group)
                        db.session.add(time_report)
                    db.session.commit()
            except Exception as e:
                print(f'Error reading csv file {str(e)}')

    return jsonify(message=f"Uploaded {uploaded_file.filename}")

def set_job_group_rates(group_name):
    switcher = {
        "A": 20,
        "B": 30
    }
    return switcher.get(group_name, 0)

@app.route("/payroll-report", methods=['GET'])
def generate_payroll_report():
    employees_with_pay_periods = db.session.query(TimeReport).all()
    initial_report = []

    for employee in employees_with_pay_periods:
        employee_item = {}
        employee_item['employeeId'] = employee.employee_id
        pay_period = employee.calculate_pay_period()
        employee_item['payPeriod'] = pay_period
        employee_item['amountPaid'] = employee.hours_worked * set_job_group_rates(employee.job_group)
        initial_report.append(employee_item)
    pprint(initial_report)

    # Create a default dict to store grouped data
    grouped_report = defaultdict(float)

    #Group and sum the keys
    for item in initial_report:
        key = (item['employeeId'], item['payPeriod']['startDate'], item['payPeriod']['endDate'])
        grouped_report[key] += item['amountPaid']
    pprint(grouped_report)

    #Convert the grouped data back to list of dicts
    final_report = [{
        'employeeId': key[0],
        'payPeriod': {
            'startDate': key[1].strftime("%Y-%m-%d"),
            'endDate': key[2].strftime("%Y-%m-%d")
        },
        'amountPaid': f'${value}'
    } for key, value in grouped_report.items()]

    pprint(final_report)
    return jsonify(payRollReport=sorted(final_report, key=lambda x: x['employeeId']))

