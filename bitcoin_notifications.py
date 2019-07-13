import requests
import time
from datetime import datetime

BITCOIN_PRICE_THRESHOLD = 10000
BITCOIN_API_URL = 'https://api.coinmarketcap.com/v1/ticker/bitcoin/'
USD_EXCHANGE_RATE = 'http://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json'
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/eA10OsKc3pmUM57uDrByvLRBiw_Uy1kLbrpTB_Dt3BD'


def get_latest_bitcoin_price():
    response = requests.get(BITCOIN_API_URL)
    response_json = response.json()
    exchange_rate_response = requests.get(USD_EXCHANGE_RATE)
    exchange_rate_response_json = exchange_rate_response.json()
    # Convert the price to a floating point number
    print(float(response_json[0]['price_usd']))
    rate_in_PLN = float(response_json[0]['price_usd'])*float(exchange_rate_response_json['rates'][0]['mid'])
    print(rate_in_PLN)
    return rate_in_PLN


def post_iftt_webhook(event, value):
    # The payload that will be sent to IFTTT service
    data = {'value1': value}
    # insert our desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)
    requests.post(ifttt_event_url, json=data)


def format_bitcoin_history(bitcoin_history):
    rows = []
    for bitcoin_price in bitcoin_history:
        date = bitcoin_price['date'].strftime('%d.%m.%Y %H:%M')
        price = bitcoin_price['price']
        row = '{}: <b>{}</b>PLN'.format(date, price)
        rows.append(row)
    return '<br>'.join(rows)


def main():
    bitcoin_history = []
    i = 1
    while True:
        print(i)
        price = get_latest_bitcoin_price()
        date = datetime.now()
        bitcoin_history.append({'date': date, 'price': price})

        # Send an emergency notification
        if price < BITCOIN_PRICE_THRESHOLD:
            post_iftt_webhook('bitcoin_price_emergency', price)

        # Send a Messenger notification
        # Once we have 5 items in our bitcoin_history send an update
        if len(bitcoin_history) == 5:
            post_iftt_webhook('bitcoin_price_update', format_bitcoin_history(bitcoin_history))
            # Reset the history
            bitcoin_history = []

        # Sleep for 5 seconds
        time.sleep(5)

        if i == 5:
            break
        i = i+1


if __name__ == '__main__':
    main()