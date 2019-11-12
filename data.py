"""
DB  syntex

{
  "room": "boardRoom",
  "slots": [
    {
      "date": "2019-07-05",
      "endTime": "16:00",
      "startTime": "15:00"
    }
  ]
}
"""
order = {}
order["room"] ="boardRoom"
order["date"] = "2019-07-05"
order["startTime"] = "15:00"
order["endTime"] = "16:00"
order = isTimeAvailable(order)
if order["isAvailable"] == True:
    order = bookSlot(order)
    print(order["status"])
else:
    print("Requested Room "+order["room"]+" not avaliable. ALternative rooms "+str(order["alternative"][0]))

