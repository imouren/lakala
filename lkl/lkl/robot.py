# -*- coding: utf-8 -*-
from lkl import config
import werobot

robot = werobot.WeRoBot(token=config.TOKEN)

robot.config["APP_ID"] = config.APP_ID
robot.config["APP_SECRET"] = config.APP_SECRET
robot.config['ENCODING_AES_KEY'] = config.ENCODING_AES_KEY


@robot.handler
def hello(message):
    return 'Hello World!'


# 让服务器监听在 0.0.0.0:80
# robot.config['HOST'] = '0.0.0.0'
# robot.config['PORT'] = 8082
# robot.run()
