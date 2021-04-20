#!/bin/bash

export PATH=$PATH:/usr/local/bin
export FLASK_APP="./generals_ai/online_bot.py"
flask run & node ./generals_ai/online_bot.js && fg
