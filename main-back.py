import json
import datetime
import isodate
import boto3


# Create clients
sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
roomTable = dynamodb.Table('myrecords')

# Check if is there any booking fot that day


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


def askAgain(msg, key, _order):
    res = {"version": "1.0",
           "sessionAttributes": _order,
           "shouldEndSession": False,
           "response": {
               "outputSpeech": {
                   "type": "PlainText",
                   "text": msg
               },

               "directives": [
                   {
                       "type": "Dialog.Delegate",
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
                                       "resolutions": {"resolutionsPerAuthority": [{
                                           "authority": "amzn1.er-authority.echo-sdk.amzn1.ask.skill.49b043a1-f602-4f73-9d17-817f11a2a81e.AMAZON.Room"}
                                           ]
                                           },
                                       "confirmationStatus": "NONE"
                                   }
                               }
                       }
                   }
               ]
           }
           }
    print(msg, key, _order, res)
    return res


def conformation(_order):
    res = {"version": "1.0",
           "sessionAttributes": _order,
           "shouldEndSession": False,
           "response": {
               "outputSpeech": {
                   "type": "PlainText",
                   "text": "Ok Your request is for "+_order["room"]+" on "+_order["date"]+" from "+_order["startTime"]+" to "+_order["endTime"]+". Kindly conform"
               },

               "directives": [
                   {
                       "type": "Dialog.ConfirmIntent",
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
                                       "resolutions": {"resolutionsPerAuthority": [{
                                           "authority": "amzn1.er-authority.echo-sdk.amzn1.ask.skill.49b043a1-f602-4f73-9d17-817f11a2a81e.AMAZON.Room"}
                                           ]
                                           },
                                       "confirmationStatus": "NONE"
                                   }
                               }
                       }
                   }
               ]
           }
           }
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
    if event["request"]["intent"]["slots"]["room"]["value"]!= '':
        _room = event["request"]["intent"]["slots"]["room"]["value"]
        for rooms in bookingData:
            rooms["names"].append(rooms["room"])
            if _room in rooms["names"]:
                order["room"] = rooms["room"]
                break
        else:
            return askAgain("Requested room not found, try again.", 'room', order)
        if event["request"]["intent"]["slots"]["date"]["value"] != '':
            _date = event["request"]["intent"]["slots"]["date"]["value"]
            order["date"] = _date
            if event["request"]["intent"]["slots"]["time"]["value"] != '':
                _startTime = event["request"]["intent"]["slots"]["time"]["value"]
                _datetime = datetime.datetime.strptime(
                    _date+_startTime, '%Y-%m-%d%H:%M')
                if _datetime >= datetime.datetime.now():
                    order["startTime"] = _startTime
                    if event["request"]["intent"]["slots"]["duration"]["value"] != '':
                        order["duration"] = event["request"]["intent"]["slots"]["duration"]["value"]
                        order["endTime"] = (datetime.datetime.strptime(order["startTime"], "%H:%M") +
                                            isodate.parse_duration(order["duration"])).strftime("%H:%M")
                        order = isTimeAvailable(order)
                        if order["isAvailable"] == True:
                            if  event["request"]["intent"]["confirmationStatus"] == "CONFIRMED":
                                return bookRoom(event, order)
                            else:
                                return conformation(order)
                        else:
                            order["room"] = ''
                            return askAgain("Requested room " + order["room"]+" is not available. "+str(order["alternative"])+" are available.", 'room', order)
                    else:
                        return askAgain('How Long does it take ', 'duration', order)
                else:
                    order["date"] = ''
                    order["startTime"] = ''
                    return askAgain("You requested booking for older date time. Kindly try future date time.", "time", order)
            else:
                return askAgain('What time you want to book', 'time', order)
        else:
            return askAgain('When is this meeting', 'date', order)
    else:
        return askAgain('Which room you want to book ', 'room', order)


def bookRoom(event, order):
    order = bookSlot(order)
    if order["status"] == "COMPLETED":
        msg = "Book Request For room: "+event["request"]["intent"]["slots"]["room"]["value"] +\
            "From:"+event["request"]["intent"]["slots"]["date"]["value"]+" "+event["request"]["intent"]["slots"]["time"]["value"]+" " +\
            "Duration:" + \
            event["request"]["intent"]["slots"]["duration"]["value"].replace(
            "PT", "")+" "
        # response = sns.publish(TopicArn='arn:aws:sns:eu-west-1:682426607174:suraj',Message=json.dumps(str(msg)))
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Ok, Your request has completed, Here is the request information\n"+msg
                },
                "card": {
                    "type": "Simple",
                    "title": " your request has completed",
                    "content": "Example of card content. This card has just plain text content.\nThe content is formatted with line breaks to improve readability."
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


def sessionEndedRequest(event):
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Bye.."
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
    res = {"version": "1.0",
           "sessionAttributes": _order,
           "shouldEndSession": False,
           "response": {
               "directives": [
                   {
                       "type": "Dialog.Delegate",
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
    return res


def main(event, context):
    # TODO implement
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