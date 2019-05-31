import json
import time
import requests

from threading import Thread

from time import sleep
from bs4 import BeautifulSoup
from kafka import KafkaConsumer, KafkaProducer
## to obtain the content to be pushed to kafka topics

path_to_fly = [{"longitude":121.56855083847638,"latitude":31.244599954339332,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56871555070629,"latitude":31.244378456210626,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56901287966905,"latitude":31.24404843269999,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56914964203287,"latitude":31.243781702468457,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56948087524067,"latitude":31.243398079531914,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56962769257942,"latitude":31.24311255223427,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56987104785223,"latitude":31.24282133028847,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.57002772156024,"latitude":31.242530623053977,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.57020935010884,"latitude":31.24219689975362,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.57052689138965,"latitude":31.242236488341845,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.57034547737325,"latitude":31.242516579935934,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.57010429679015,"latitude":31.24285919840755,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":10},{"longitude":121.5696949809987,"latitude":31.243608361266332,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.5694792436787,"latitude":31.243944895944225,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56930230431519,"latitude":31.244282909760404,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56904552489624,"latitude":31.2445614784835,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56889239308005,"latitude":31.24479675484711,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1}]

path_to_fly_2 = [{"longitude":121.56836994775401,"latitude":31.244940285114495,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56822397070312,"latitude":31.245186137313922,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56810113950795,"latitude":31.245397469403432,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56787295894222,"latitude":31.245667596652655,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.5677111558829,"latitude":31.2459265130909,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56750130342542,"latitude":31.246129322232434,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56737877622413,"latitude":31.246334447795387,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56734374668194,"latitude":31.246416078055038,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56754984801391,"latitude":31.246493368747903,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56779896250143,"latitude":31.2461910589473,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56796833581586,"latitude":31.245928429555388,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56812283684452,"latitude":31.24575250750827,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56828695443409,"latitude":31.245448189202133,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56848930229347,"latitude":31.245234709835742,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1},{"longitude":121.56859862885273,"latitude":31.24499574139532,"cameraYaw":0,"cameraPitch":0,"altitude":100,"stop":1}]

#fetch the raw html from the url 
def fetch_raw(recipe_url):
	html = None
	print("Processing..{}", format(recipe_url))

	try: 
		r = requests.get(recipe_url, headers=headers)
		if r.status.code == 200:
			html = r.text

	except Exception as ex:
		print("Exception while accessing raw html")
		print(str(ex))

	finally:
		return html.strip()


##to push the content to kafka topics
def publish_message(producer_instance, topic_name, key, value):
	try:
		key_bytes = bytes(key, encoding='utf-8')
		value_bytes = bytes(value, encoding='utf-8')
		producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
		producer_instance.flush()
		print("Message published successfully")

	except Exception as ex:
		print("Exception in publish_message")
		print(str(ex))

 
##connect to kafka producer
def connect_kafka_producer():
	_producer = None
	try:
		_producer = KafkaProducer(bootstrap_servers=['35.187.235.125:9092'], api_version=(0,10))

	except Exception as ex:
		print("Exception while connecting to Kafka")
		print(str(ex))

	finally: 
		return _producer


def get_input():
	message = input()
	if message is not "kill":
		# publish_message(kafka_producer, 'raw-recipes', 'raw', message.strip())
		publish_message(kafka_producer, 'base-topic', 'raw', message.strip())
		get_input()
	else:
		kafka_producer.close()



number = 0
number_2 = 0

def timeout_func(kafka_producer):
	global number
	print("timeout ")
	print(number)
	

	time.sleep(1)

	point = path_to_fly[number]
	

	format_msg = {"droneStatus": 1,"location":{"longitude":120.0,"latitude":31.242530623053977,"altitude":100},"battery": 0.9,"serialNumber": 1,"droneNumber": 1,"taskName": "Test drone","iotDeviceId": "1123123","taskName": "task 1","riverName": "river 1","areaName": "area 1","timeStarted": "time","taskStatus": 0,"liveUrl": "https://....","pushUrl": "https://"}

	format_msg["location"]["longitude"] = point["longitude"]
	format_msg["location"]["latitude"] = point["latitude"]
	format_msg["location"]["altitude"] = point["altitude"]

	message = json.dumps(format_msg)

	publish_message(kafka_producer, 'base-topic', 'raw', message.strip())

	
	number += 1
	if(number>len(path_to_fly)-1):
		number = 0

	timeout_func(kafka_producer)




#run main

if __name__ == "__main__":
	headers = {
	 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Pragma': 'no-cache'
	}

	all_recipes = ['1', '2','3']#get_recipes()

	# if len(all_recipes) > 0:
	# 	kafka_producer = connect_kafka_producer()	
	# 	get_input()
	kafka_producer = connect_kafka_producer()

	timeout_func(kafka_producer)

