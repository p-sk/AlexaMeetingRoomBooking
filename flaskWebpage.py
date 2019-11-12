from flask import Flask
from flask import render_template
import json 
import boto3

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
roomTable = dynamodb.Table('myrecords')

bookingData = roomTable.scan()["Items"]
app = Flask(__name__)

bookingData = roomTable.scan()["Items"]

@app.route('/')
def index():
   return render_template('table.html',data = bookingData )

if __name__ == '__main__':
   app.run(debug = True)











'''[{'slots': [{'date': '2019-07-05', 'startTime': '12:00', 'endTime': '14:00'}, {'date': '2019-07-05', 'startTime': '15:00', 'endTime': '16:00'}, {'date': '2019-07-12', 'startTime':'20:00', 'endTime': '21:00'}, {'date': '2019-07-12', 'startTime': '14:00', 'endTime': '16:00'}], 'room': 'boardRoom', 'names': ['boardroom', 'board room']}, {'slots': [{'date': '2019-07-05', 'startTime': '15:00', 'endTime': '16:00'}, {'date': '2019-07-11', 'startTime': '19:00', 'endTime': '21:00'}, {'date': '2019-07-13', 'startTime': '08:00', 'endTime': '10:00'}, {'date': '2019-07-23', 'startTime': '17:00', 'endTime': '19:00'}], 'names': ['conference room 2', 'conference 2', 'conf 2', 'conf room 2', 'conference room two', 'conference two', 'conf two', 'conf room two'], 'room': 'conf2'}, {'slots': [{'date': '2019-07-05', 'startTime': '15:00', 'endTime': '16:00'}, {'date': '2019-07-12', 'startTime': '08:00', 'endTime': '10:00'}, {'date': '2019-07-12', 'startTime': '20:00', 'endTime': '23:00'}, {'date': '2019-07-13', 'startTime': '08:00', 'endTime': '10:00'}, {'date': '2019-07-12', 'startTime': '16:00', 'endTime': '20:00'}, {'date': '2019-07-15', 'startTime': '19:00', 'endTime': '20:00'}, {'date': '2019-07-16', 'startTime': '17:00', 'endTime': '18:00'}, {'date': '2019-07-17', 'startTime': '17:00', 'endTime': '19:00'}, {'date': '2019-07-23', 'startTime': '17:00', 'endTime': '19:00'}], 'names': ['conference room 1', 'conference 1', 'conf 1', 'conf room 1', 'conference room one', 'conference one', 'conf one', 'conf room one'], 'room': 'conf1'}, {'slots': [{'date': '2019-07-05', 'startTime': '15:00', 'endTime': '16:00'}, {'date': '2019-07-17', 'startTime': '17:00', 'endTime': '18:00'}], 'names': ['conference room 3', 'conference 3', 'conf 3', 'conf room 3', 'conference room three', 'conference three', 'conf three', 'conf room three'], 'room': 'conf3'}]'''

