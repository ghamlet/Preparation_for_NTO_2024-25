# -*- coding: utf-8 -*-
import paho.mqtt.client as paho


IP_ADRESS = "127.0.0.1"
PORT = 1883


addend_numbers = []

def on_message(client, userdata, message):
    
    msg = message.payload.decode("utf-8")
    

    if message.topic.endswith("2"):    # получаем название топика
        number, channel_name = msg.split(";")
        result = int(number) * 2
        client.publish(channel_name, str(result), qos=2)  # QoS 2 – с гарантированной доставкой
    
    
    elif message.topic.endswith("3"):
        number, channel_name = msg.split(";")
        result = int(number) * 3
        client.publish(channel_name, str(result),qos=2)
    
    
    elif message.topic == "addend":    # команда суммирования поступающих чисел
        addend_numbers.append(int(msg))
    
    
    elif message.topic == "command":    # команда отправки накопленной суммы на указанный канал
        channel_name = msg
        total_sum = sum(addend_numbers)
        client.publish(channel_name, str(total_sum),qos=2)
        
        addend_numbers.clear()   # после отправки  массив для суммы надо очитить

    
    elif message.topic == "numbers":   # проверка  на четность
        number = int(msg)
        if number % 2 != 0:  # Если число нечетное
            client.publish("odd", str(number),qos=2)


def setup():
    client = paho.Client()
    client.on_message = on_message
    client.connect(IP_ADRESS, PORT, 60)
    
    # Подписка на необходимые каналы
    client.subscribe("#", qos=2)  # подпись на все каналы
    
    # client.subscribe("*2",qos=2)  # Подписка на все каналы, заканчивающиеся на 2
    # client.subscribe("*3",qos=2)  # Подписка на все каналы, заканчивающиеся на 3
    # client.subscribe("addend", qos=2)
    # client.subscribe("command", qos=2)
    # client.subscribe("numbers", qos=2)
    
    return client


def main_loop(client):
    client.loop_forever()   # бесконечный цикл обработки сообщений
 

if __name__ == "__main__":
    mqtt_client = setup()
    main_loop(mqtt_client)