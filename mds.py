import cyclone.web
import json
import re

class AccountHandler(cyclone.web.RequestHandler):

  def get(self, account):
    self.set_header("Content-Type", "text/json")

class MailboxHandler(cyclone.web.RequestHandler):
  def get(self, account, mailbox):
    self.set_header("Content-Type", "text/json")

class MessageHandler(cyclone.web.RequestHandler):

  def get(self, account, mailbox, uid, req):
    r = {"a": 1, "b": 2, "account": account,
      "mailbox": mailbox, "uid": uid, "extra":req}
    self.set_header("Content-Type", "text/json")
    self.write(json.dumps(r))
    


class MDS(cyclone.web.Application):
  def __init__(self):
    handlers = [
      ("/([^/]+)/", AccountHandler),
      ("/([^/]+)/([^/]+)/", MailboxHandler),
      ("/([^/]+)/([^/]+)/(\\d+)(.*)", MessageHandler)
    ]
    cyclone.web.Application.__init__(self, handlers)
