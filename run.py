
import os

from grocery_list import app

def run():
    port = int(os.environ.get('PORT', 8000))
    app.run(host='127.0.0.1', port=port)

if __name__ == '__main__':
    run()

