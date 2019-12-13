import json

import requests
from requests import Response
from requests.exceptions import RequestException, Timeout

from settings import CLEVERBOT_API, API_KEY


class CleverbotSession():

    def __init__(self):
        self.bot_id = None
        self.session = requests.Session()
        self.interaction_count = 0

    def check_status_code(self, code):
        return 200 <= code < 400

    def decode_response(self, response: Response):
        try:
            return json.loads(response.content.decode('unicode-escape').encode('iso-8859-1').decode('utf-8'))
        except Exception as e:
            print(f"CLEVERBOT: ошибка во время декодирования данных {e}")
            return None

    def post_message(self, message):
        print(f"CLEVERBOT: Попытка соединения с API_KEY={API_KEY} text='{message}' bot_id={self.bot_id}")
        params = {
            'key': API_KEY,
            'input': message,
        }
        if self.bot_id:
            params['cs'] = self.bot_id

        try:
            response = self.session.post(CLEVERBOT_API, params=params, timeout=5)
            response.encoding = 'ascii'
        except Timeout as te:
            print(f"CLEVERBOT: Соединение сброшено по таймауту CLEVERBOT_API: {te}")
            return None
        except RequestException as e:
            print(f"CLEVERBOT: Произошла ошибка во время соединения с CLEVERBOT_API: {e}")
            return None
        if not self.check_status_code(response.status_code):
            print(f"CLEVERBOT: Соединение . status_code={response.status_code}. response_text={response.text}")
            return None
        if response.headers.get('Content-Type', None) != 'application/json':
            print(f"CLEVERBOT: Неверный формат данных ответа")
            return None
        json_response = self.decode_response(response)
        if not json_response:
            return None
        return json_response

    def prepare_answer(self, json_response, message):
        self.bot_id = json_response.get('cs', None)
        time_taken = json_response.get('time_taken', None)
        interaction_count = json_response.get('interaction_count', None)
        if interaction_count:
            self.interaction_count = int(interaction_count)
        clever_output = json_response.get('clever_output', None)
        if not clever_output:
            print(f"CLEVERBOT: не получен текстовый ответ на message={message}")
            return None
        print(f"CLEVERBOT: Получен ответ clever_output='{clever_output}' interaction_count={interaction_count} "
              f"time_taken={time_taken} message={message}")
        return clever_output

    def say(self, message: str):
        json_response = self.post_message(message)
        if not json_response:
            return None
        return self.prepare_answer(json_response, message)


if __name__ == '__main__':
    cleverBot = CleverbotSession()
    s1 = cleverBot.say("Привет")
    print(s1)
    s2 = cleverBot.say("Хорошо")
    print(s2)
