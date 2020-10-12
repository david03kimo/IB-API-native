'''
This is for listener for tradingview alerts and call the sendorder function to place an order.
'''

from flask import Flask, request, abort
from SendMarketOrder import sendorder
import sys


app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        sendorder(data)
        return " ", 200
    else:
        abort(400)

if __name__ == '__main__':
    app.run()