import requests
import os , sys
import telebot
from dotenv import load_dotenv
from time import sleep

def send_message(tg_token, tg_chat_id, new_attempts):
    bot = telebot.TeleBot(tg_token, parse_mode='MARKDOWN')

    for attempt in new_attempts:
        lesson_title = attempt['lesson_title']
        if attempt['is_negative']:
            is_negative = 'Преподаватель *не принял* вашу работу. Нужно исправить ошибки'
        else:
            is_negative = 'Преподаватель *принял* вашу работу! Можете приступать к следующему уроку'

        bot.send_message(tg_chat_id, f'{lesson_title}\n*Работа проверена!*\n\n{is_negative}')



def check_dvmn_result(dvmn_token, tg_token, tg_chat_id):
    header = {'Authorization': f'Token {dvmn_token}'}
    payload = {}

    while True:
        url = 'https://dvmn.org/api/long_polling/'
        try:
            response = requests.get(url, headers=header, params=payload, timeout=60)
            if response.ok:
                response_hh = response.json()
                if 'timestamp_to_request' in response_hh:
                    timestamp = response_hh['timestamp_to_request']

                if 'last_attempt_timestamp' in response_hh:
                    timestamp = response_hh['last_attempt_timestamp']
                    send_message(tg_token, tg_chat_id, response_hh['new_attempts'])

                payload = {'timestamp': timestamp}
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError as e:
            sys.stderr.write('No Internet Connection \n')
            print(sys.stderr , e)
            sleep(60)


def main():
    load_dotenv()

    dvmn_token = os.getenv('DVMN_TOKEN')
    tg_token = os.getenv('TG_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')

    check_dvmn_result(dvmn_token, tg_token, tg_chat_id)


if __name__ == '__main__':
    main()
