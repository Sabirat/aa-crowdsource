#!/usr/bin/python
activate_this = '/home/grad05/rubya001/AAmeeting/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/grad05/rubya001/AAmeeting/aa-crowdsource/")
from app import app as application
if __name__ == "__main__":
    app.run()
application.secret_key = 'Add your secret key'
