import os
import json
import requests


def add_data_to_index():
    for filename in os.listdir(os.getcwd() + '/ustawy'):
        with open('./ustawy/' + filename, 'r', encoding='utf-8') as file:
            out = ' '.join(file.readlines()).replace('\n', '')
            body = {'content': out,'title':filename}
            print(body)
            res = requests.post('http://localhost:9200/idx/_doc', data=json.dumps(body),
                                headers={"content-type": "application/json"})
            print(res.json())


if __name__ == "__main__":
    add_data_to_index()
