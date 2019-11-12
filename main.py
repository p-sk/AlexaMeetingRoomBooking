import json
import datetime
import isodate
import boto3


# Create clients
sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
roomTable = dynamodb.Table('myrecords')

# Check if is there any booking fot that day

def sessionEndedRequest(event):
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Ok Bye.."
            }
        }
    }


def defaultFunction(event):
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Sorry I cannot understand that can you please try again"
            },
            "shouldEndSession": False,
        }
    }


def canFulfilled(event):
    if event["request"]["intent"]["name"] == "BookRoom":
        return {
            "version": "1.0",
            "response": {
                "canFulfillIntent": {
                    "canFulfill": "YES"
                }
            },
            "shouldEndSession": False,
        }


def launchRequest(event):
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Welcome..."
            }
        }
    }


def startDialog(event):
    _order = {
        "room": '',
        "date": '',
        "startTime": '',
        "duration": ''
    }
    return askAgain(msg='Welcome...',_order=_order)

def isTimeAvailable(_order):
    bookingData = roomTable.scan()["Items"]
    _order["isAvailable"] = True
    _order["alternative"] = []
    for _bookingData in bookingData:
        for _slot in _bookingData["slots"]:
            if _slot["date"] == _order["date"]:
                __stime = _stime = datetime.datetime.strptime(
                    _slot["startTime"], "%H:%M").time()
                __etime = _stime = datetime.datetime.strptime(
                    _slot["endTime"], "%H:%M").time()
                _stime = _stime = datetime.datetime.strptime(
                    _order["startTime"], "%H:%M").time()
                _etime = datetime.datetime.strptime(
                    _order["endTime"], "%H:%M").time()
                if (_stime >= __stime and _stime < __etime) or (_etime > __stime and _etime <= __etime):
                    if _bookingData["room"] == _order["room"]:
                        _order["isAvailable"] = False
                else:
                    if _bookingData["room"] != _order["room"]:
                        if _bookingData["room"] not in _order["alternative"]:
                            _order["alternative"].append(_bookingData["room"])
            else:
                if _bookingData["room"] != _order["room"]:
                    if _bookingData["room"] not in _order["alternative"]:
                        _order["alternative"].append(_bookingData["room"])
    return _order

# Book the Slot

def bookSlot(_order):
    _slot = [{
        "date": _order["date"],
        "endTime": _order["endTime"],
        "startTime": _order["startTime"]
    }]
    try:
        roomTable.update_item(
            Key={
                'room': _order["room"]
            },
            UpdateExpression="set slots = list_append(slots, :i)",
            ExpressionAttributeValues={
                ':i': _slot
            },
            ReturnValues="UPDATED_NEW"
        )
        _order["status"] = "COMPLETED"
    except Exception as e:
        print(e)
        _order["status"] = "NOTCOMPLETED"
    return _order


def askAgain(msg='',_order = {},directives="Dialog.Delegate"):
    res = {"version": "1.0",
           "sessionAttributes": _order,
           "shouldEndSession": False,
           "response": {
               "directives": [
                   {
                       "type": directives,
                       "updatedIntent": {
                               "name": "BookRoom",
                               "confirmationStatus": "NONE",
                               "slots": {
                                   "date": {
                                       "name": "date",
                                       "value": _order["date"],
                                       "confirmationStatus": "NONE"
                                   },
                                   "duration": {
                                       "name": "duration",
                                       "value": _order["duration"],
                                       "confirmationStatus": "NONE"
                                   },
                                   "time": {
                                       "name": "time",
                                       "value": _order["startTime"],
                                       "confirmationStatus": "NONE"
                                   },
                                   "room": {
                                       "name": "room",
                                       "value": _order["room"],
                                       "resolutions": {},
                                       "confirmationStatus": "NONE"
                                   }
                               }
                       }
                   }
               ]
           }
           }
    if msg !='':
        res["response"]["outputSpeech"] ={}
        res["response"]["outputSpeech"]["type"] ="PlainText"
        res["response"]["outputSpeech"]["text"]= msg   
    print(_order, res)
    return res


def slotValidation(event):
    bookingData = roomTable.scan()["Items"]
    order = {
        "room": '',
        "date": '',
        "startTime": '',
        "duration": ''
    }
    if ("value" in event["request"]["intent"]["slots"]["room"]) and event["request"]["intent"]["slots"]["room"]["value"]!= '':
        _room = event["request"]["intent"]["slots"]["room"]["value"]
        for rooms in bookingData:
            rooms["names"].append(rooms["room"])
            if _room in rooms["names"]:
                order["room"] = rooms["room"]
                order["roomname"] = _room
                break
        else:
            return askAgain("Requested room not found, try again.", 'room', order)
        if ("value" in event["request"]["intent"]["slots"]["date"])  and event["request"]["intent"]["slots"]["date"]["value"] != '':
            _date = event["request"]["intent"]["slots"]["date"]["value"]
            order["date"] = _date
            if ("value" in event["request"]["intent"]["slots"]["time"])  and event["request"]["intent"]["slots"]["time"]["value"] != '':
                _startTime = event["request"]["intent"]["slots"]["time"]["value"]
                _datetime = datetime.datetime.strptime(
                    _date+_startTime, '%Y-%m-%d%H:%M')
                if _datetime >= datetime.datetime.now():
                    order["startTime"] = _startTime
                    if ("value" in event["request"]["intent"]["slots"]["duration"])  and event["request"]["intent"]["slots"]["duration"]["value"] != '':
                        order["duration"] = event["request"]["intent"]["slots"]["duration"]["value"]
                        order["endTime"] = (datetime.datetime.strptime(order["startTime"], "%H:%M") +
                                            isodate.parse_duration(order["duration"])).strftime("%H:%M")
                        order = isTimeAvailable(order)
                        if order["isAvailable"] == True:
                            if  event["request"]["intent"]["confirmationStatus"] == "CONFIRMED":
                                return bookRoom(event, order)
                            elif event["request"]["intent"]["confirmationStatus"] == 'DENIED':
                                return sessionEndedRequest(event)
                            else:
                                return askAgain(msg = "Ok Your request is for "+order["roomname"]+" on "+order["date"]+" from "+order["startTime"]+" to "+order["endTime"]+". Kindly conform",_order=order,directives="Dialog.ConfirmIntent")
                        else:
                            order["room"] = ''
                            return askAgain(msg =order["roomname"] +" is not available. Following rooms are available for requested time slot "+str(order["alternative"]),_order=order)
                    else:
                        return askAgain(_order=order) #'How Long does it take ',
                else:
                    order["date"] = ''
                    order["startTime"] = ''
                    return askAgain(_order=order) # "You requested booking for older date time. Kindly try future date time.",
            else:
                return askAgain(_order=order) # 'What time you want to book',  
        else:
            return askAgain(_order=order) # 'When is this meeting', 'date',
    else:
        return askAgain(_order=order) # 'Which room you want to book ', 'room',


def bookRoom(event, order):
    order = bookSlot(order)
    if order["status"] == "COMPLETED":
        msg = "Book Request For room: "+order["roomname"]  +\
            "From:"+order['date']+" "+order['startTime']+" " +\
            "To:" +order['date']+" "+order['endTime']+" "
        # response = sns.publish(TopicArn='arn:aws:sns:eu-west-1:682426607174:suraj',Message=json.dumps(str(msg)))
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Ok, Your request has completed, Here is the request information "+msg
                }
            }
        }
    else:
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Something Went Wrong"
                }
            }
            
        }


def main(event, context):
    # Publish a simple message to the specified SNS topic
    print(event)
    if event["request"]["type"] == "IntentRequest":
        if event["request"]["intent"]["name"] == "BookRoom":
            if event["request"]["dialogState"] == "COMPLETED":
                return bookRoom(event, event["session"]["attributes"])
            elif event["request"]["dialogState"] == "STARTED":
                return startDialog(event)
            else:
                return slotValidation(event)
    if event["request"]["type"] == "SessionEndedRequest":
        return sessionEndedRequest(event)
    if event["request"]["type"] == "CanFulfillIntentRequest":
        return canFulfilled(event)
    if event["request"]["type"] == "LaunchRequest":
        return launchRequest(event)