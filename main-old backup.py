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


def bookRoom(event):
    order = {}
    order["room"] = event["request"]["intent"]["slots"]["Room"]["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"]["name"]
    order["date"] = event["request"]["intent"]["slots"]["date"]["value"]
    order["startTime"] = event["request"]["intent"]["slots"]["time"]["value"]
    order["endTime"] = (datetime.datetime.strptime(event["request"]["intent"]["slots"]["time"]["value"], "%H:%M") +
                        isodate.parse_duration(event["request"]["intent"]["slots"]["duration"]["value"])).strftime("%H:%M")
    _datetime = datetime.datetime.strptime(
        order["date"]+order["startTime"], '%Y-%m-%d%H:%M')
    if _datetime >= datetime.datetime.now():
        order = isTimeAvailable(order)
        if order["isAvailable"] == True:
            order = bookSlot(order)
            if order["status"] == "COMPLETED":
                msg = "Book Request For Room: "+event["request"]["intent"]["slots"]["Room"]["value"] +\
                    "From:"+event["request"]["intent"]["slots"]["date"]["value"]+" "+event["request"]["intent"]["slots"]["time"]["value"]+" " +\
                    "Duration:" + \
                    event["request"]["intent"]["slots"]["duration"]["value"].replace(
                    "PT", "")+" "
                #response = sns.publish(TopicArn='arn:aws:sns:eu-west-1:682426607174:suraj',Message=json.dumps(str(msg)))
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
                        },
                        "card": {
                            "type": "Simple",
                            "title": " your request has completed",
                            "content": "Example of card content. This card has just plain text content.\nThe content is formatted with line breaks to improve readability."
                        }
                    }
                }
        else:
            return {"version": "1.0",
                    "sessionAttributes": {
                        "favoriteColor": "blue"
                    },
                    "response": {
                        "outputSpeech": {
                            "type": "PlainText",
                            "text": "Requested room " + order["room"]+" is not avaliable. "+str(order["alternative"])+" are avaliable."
                        }
                    },
                    "shouldEndSession": False,
                    "directives": [
                        {
                            "type": "Dialog.ElicitSlot",
                            "slotToElicit": "Room"
                        }
                    ]
                    }
    else:
        return {"version": "1.0",
                "sessionAttributes": {
                    "favoriteColor": "blue"
                },
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "You requested booking for older day. Kindly try future date and time."
                    }
                },
                "shouldEndSession": False,
                "directives": [
                    {
                        "type": "Dialog.ElicitSlot",
                        "slotToElicit": "date",
                        "slotToElicit": "time"
                    }
                ]
                }


def main(event, context):
    # TODO implement
    # Publish a simple message to the specified SNS topic
    print(event)
    if event["request"]["type"] == "IntentRequest":
        if event["request"]["intent"]["name"] == "BookRoom":
            return bookRoom(event)
