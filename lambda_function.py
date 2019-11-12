import json
import boto3

# Create an SNS client
sns = boto3.client('sns')


def lambda_handler(event, context):
    # TODO implement
    # Publish a simple message to the specified SNS topic
    print(event)
    msg = "Book Request For Room: "+event["request"]["intent"]["slots"]["Room"]["value"]+\
        "From:"+event["request"]["intent"]["slots"]["date"]["value"]+" "+event["request"]["intent"]["slots"]["time"]["value"]+" "+\
                "Duration:"+event["request"]["intent"]["slots"]["duration"]["value"].replace("PT","")+" "
    print(msg)
    response = sns.publish(
    TopicArn='arn:aws:sns:eu-west-1:682426607174:suraj',    
    Message=json.dumps(str(msg))
    )
    return {
    "version": "1.0",
    "response": {
    "outputSpeech": {"type":"PlainText","text":"Ok, Your request has completed, Here is the request information\n"+msg},
    "card": {
      "type": "Simple",
      "title": " your request has completed",
      "content": "Example of card content. This card has just plain text content.\nThe content is formatted with line breaks to improve readability."
    }
    }
    }
    