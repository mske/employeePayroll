from datetime import  datetime

from app import db

class TimeReport(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    hours_worked = db.Column(db.Float, nullable=False)
    employee_id = db.Column(db.String(255), nullable=False)
    job_group = db.Column(db.String(1), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now())

    def __init__(self, date, hours_worked, employee_id, job_group):
        self.date = date
        self.hours_worked = hours_worked
        self.employee_id = employee_id
        self.job_group = job_group
    def calculate_pay_period(self):
        # Calculate the start and end dates of the pay period
        if self.date.day <= 15:
            start_date = datetime(self.date.year, self.date.month, 1).date()
            end_date = datetime(self.date.year, self.date.month, 15).date()
        else:
            start_date = datetime(self.date.year, self.date.month, 16).date()
            end_date = datetime(self.date.year, self.date.month, 30).date()
        return {
            'startDate' : start_date,
            'endDate': end_date
        }