# -*- coding: utf-8 -*-

import json
from threading import Thread
import time
import paho.mqtt.client as paho
import eval as submission
import os


IP_ADRESS = "127.0.0.1"
PORT = 1883


MAIN_DIR = os.path.dirname(os.path.abspath(__file__))



def message_handler(client, userdata, msg):
    topic = msg.topic
    msg_data = msg.payload.decode()
    
    
    print(f"Received {topic}: {msg_data}")

    if len(user_test_results) <= current_test_id:
        user_test_results.append([])
    
    user_test_results[current_test_id].append([topic, msg_data])



user_test_results = []
current_test_id = 0

def main():
    global current_test_id
    annot_file = MAIN_DIR + "/annotations.json"

    with open(annot_file, 'r') as f:
        data = json.load(f)
    
    test_cases = data['test_cases']    # массив с тестовыми заданиями
    test_results = data['test_results']  # массив с правльными ответами


    args = submission.setup()
    
    Thread(
        target=submission.main_loop,
        args=(args,),
        daemon=True
    ).start()
    
    
    client = paho.Client()
    client.on_message = message_handler


    if client.connect(IP_ADRESS, PORT, 60) != 0:
        print("Couldn't connect to the mqtt broker")
        exit(1)

    
    #  QoS - Quality of Service(качество обслуживания)
    client.subscribe("odd", qos=2)   # QoS 2 – с гарантированной доставкой
    client.subscribe("test_multiply", qos=2)
    client.subscribe("test_addend", qos=2)


    correct = 0
    for current_test_id, test_case in enumerate(test_cases):
        print("current_test_id: ", current_test_id)
        print("test_case: ", test_case, "\n")
        
        for topic, msg in test_case:
            print("topic: ", topic)
            print("msg: ", msg, "\n")
            
            client.publish(topic, msg, 0)
            client.loop_write()
        
        
        for _ in range(20):    # читаем пришедшие ответы
            client.loop_read()
            time.sleep(0.2)
        
        print("user_result: ", user_test_results[current_test_id])
        print("TRUE answer: ", test_results[current_test_id])
        
        if test_results[current_test_id] == user_test_results[current_test_id]:
            correct += 1

        print("\n")

    total_object = len(test_cases)
    print(f"Из {total_object} тестов верны {correct}")

    score = correct / total_object
    print(f"Точность: {score:.2f}")


if __name__ == '__main__':
    main()