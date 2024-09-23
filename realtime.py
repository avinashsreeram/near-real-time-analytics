import csv
import json
import time
import boto3
from multiprocessing import Process, Queue

# AWS Kinesis Firehose delivery stream is named as
FIREHOSE_STREAM_NAME = 'findatastream'

# AWS Kinesis Firehose client setup
client = boto3.client('firehose', region_name='us-east-1')  # Region of deployment is specified here
def produce_data(queue):
    with open('/Users/avinashnandikatti/my_files/uc/courses/sem-2/adv_data_vis/streaming_data_vis_project/credit_risk_dataset.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert the CSV row to JSON format
            json_data = json.dumps(row)
            # Put the JSON object into the queue for streaming
            queue.put(json_data)
            # Simulate a delay for real-time streaming effect
            time.sleep(1) #Simulates a new transaction every 1 second

def stream_data(queue):
    while True:
        if not queue.empty():
            json_data = queue.get()
            # Stream the data to AWS Kinesis Firehose
            response = client.put_record(
                DeliveryStreamName=FIREHOSE_STREAM_NAME,
                Record={'Data': json_data}
            )
            print('Data streamed to Kinesis Firehose:', json_data, 'Response:', response)

if __name__ == '__main__':
    # Create a queue to hold the JSON data
    queue = Queue()
    
    # Create a data producer process
    producer_process = Process(target=produce_data, args=(queue,))
    producer_process.start()
    
    # Create a data streaming process
    streamer_process = Process(target=stream_data, args=(queue,))
    streamer_process.start()
    
    producer_process.join()
    streamer_process.join()
