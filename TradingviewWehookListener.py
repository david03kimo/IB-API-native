from flask import Flask, request, abort
import sys

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_data(as_text=True)
    print('webhook'); sys.stdout.flush()
    print(data)
    # print('Sending:', data['symbol'], data['type'], data['side'], data['amount'], calc_price(data['price']))
    if request.method == 'POST':
        print(request.json)
        return '', 200
    else:
        abort(400)

if __name__ == '__main__':
    app.run()

