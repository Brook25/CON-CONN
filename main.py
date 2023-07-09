#!/usr/bin/env python3

from web_flask import create_app


app = create_app()



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
