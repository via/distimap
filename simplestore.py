import email
import json
import os
import shutil
import types
import xattr


class SimpleStore:

  def __init__(self, storeroot="./accounts"):
    self.root = storeroot
    self.xattrname = 'user.flags.distimap'

  def process(self, command, callback, data):
    parsed = json.loads(command)
    if (type(parsed) == types.ListType):
      for c in parsed:
        callback(json.dumps(self._parse_command(c)), data)
    else:
      callback(json.dumps(self._parse_command(parsed)), data)

  def _parse_command(self, cmd):
    if cmd['command'] == "listmailboxes":
      return self._process_list_mailboxes(cmd['account'])
    if cmd['command'] == "listuids":
      return self._process_list_uids(cmd['account'], cmd['mailbox'])
    if cmd['command'] == "getflags":
      return self._process_get_flags(cmd['account'], cmd['mailbox'], cmd['uid'])
    if cmd['command'] == "getheaders":
      return self._process_get_headers(cmd['account'], cmd['mailbox'], cmd['uid'])
    if cmd['command'] == "getmessage":
      return self._process_get_message(cmd['account'], cmd['mailbox'], cmd['uid'])
    if cmd['command'] == "createmailbox":
      return self._process_create_mailbox(cmd['account'], cmd['mailbox'])
    if cmd['command'] == "deletemailbox":
      return self._process_delete_mailbox(cmd['account'], cmd['mailbox'])
    if cmd['command'] == "createmessage":
      return self._process_create_message(cmd['account'], cmd['mailbox'], cmd['uid'])
    if cmd['command'] == "deletemessage":
      return self._process_delete_message(cmd['account'], cmd['mailbox'], cmd['uid'])
    if cmd['command'] == "setflags":
      return self._process_set_flags(cmd['account'], cmd['mailbox'], cmd['uid'], cmd['flags'])

    # Do something about erroneous command
    return

  def _process_list_mailboxes(self, account):
    dirs = os.listdir("%s/%s/" % (self.root, account))
    return {"response":"listmailboxes", "account": account, "mailboxes":dirs}

  def _process_list_uids(self, account, mailbox):
    uids = os.listdir("%s/%s/%s/" % (self.root, account, mailbox))
    uids = [int(x) for x in uids]
    uids.sort()
    return {"response":"listuids", "account": account,
            "mailbox":mailbox, "uids": uids}

  def _process_get_flags(self, account, mailbox, uid):
    flags = xattr.getxattr('%s/%s/%s/%d' % (self.root, 
      account, mailbox, uid), self.xattrname).split()
    return {"response":"getflags", "account": account,
            "mailbox":mailbox, "uid": uid, "flags": flags}

  def _process_get_headers(self, account, mailbox, uid):
    parser = email.Parser.Parser()
    msg = parser.parse(open("%s/%s/%s/%d" % (self.root, account, mailbox, uid)),
                 headersonly=True)
    return {"response":"getheaders", "account": account,
            "mailbox":mailbox, "uid":uid, "headers": msg.items()}


  def _process_get_message(self, account, mailbox, uid):
    parser = email.Parser.Parser()
    msg = parser.parse(open("%s/%s/%s/%d" % (self.root, account, mailbox, uid)))
    return {"response":"getheaders", "account": account,
            "mailbox":mailbox, "uid":uid, "message": msg.as_string()}

  def _process_create_mailbox(self, account, mailbox):
    ret = {"response":"createmailbox", "account": account,
           "mailbox":mailbox} 
    try:
      os.mkdir("%s/%s/%s/" % (self.root, account, mailbox))
    except OSError as e:
      ret['status'] = e.strerror
      return ret
    ret['status'] = "OK"
    return ret

  def _process_delete_mailbox(self, account, mailbox):
    ret = {"response":"deletemailbox", "account": account,
           "mailbox":mailbox} 
    try:
      shutil.rmtree("%s/%s/%s/" % (self.root, account, mailbox))
    except OSError as e:
      ret['status'] = e.strerror
      return ret
    ret['status'] = "OK"
    return ret

  def _process_create_message(self, account, mailbox, uid):
    f = open("%s/%s/%s/%d" % (self.root, account, mailbox, uid), "w")
    f.close()
    ret = {"response":"createmessage", "account": account,
           "mailbox":mailbox, "uid": uid, "status": "OK"} 
    return ret

  def _process_delete_message(self, account, mailbox, uid):
    os.remove("%s/%s/%s/%d" % (self.root, account, mailbox, uid))
    ret = {"response":"deletemessage", "account": account,
           "mailbox":mailbox, "uid": uid, "status": "OK"} 
    return ret	 

  def _process_set_flags(self, account, mailbox, uid, flags):
    xattr.setxattr('%s/%s/%s/%d' % (self. root, account, mailbox, uid),
        self.xattrname, " ".join(flags))
    ret = {"response":"setflags", "account": account,
           "mailbox":mailbox, "uid": uid, "status": "OK",
	   "flags": flags} 
    return ret

def cb(response, d):
  print json.dumps(response)

if __name__ == "__main__":
  s = SimpleStore()

  testcommand = {"command": "listmailboxes", "account":"via@matthewvia.info"}
  s.process(json.dumps(testcommand), cb, None)

  testcommand = {"command": "listuids", "account":"via@matthewvia.info", "mailbox": "INBOX"}
  s.process(json.dumps(testcommand), cb, None)
  
  testcommand = {"command": "getflags", "account":"via@matthewvia.info", "mailbox": "INBOX", "uid": 1}
  s.process(json.dumps(testcommand), cb, None)
  
  testcommand = {"command": "getmessage", "account":"via@matthewvia.info", "mailbox": "INBOX", "uid": 1}
  s.process(json.dumps(testcommand), cb, None)

  testcommand = {"command": "createmailbox", "account":"via@matthewvia.info", "mailbox": "testB"}
  s.process(json.dumps(testcommand), cb, None)

  testcommand = {"command": "createmessage", "account":"via@matthewvia.info", "mailbox": "testB", "uid": 1}
  s.process(json.dumps(testcommand), cb, None)

  testcommand = {"command": "createmessage", "account":"via@matthewvia.info", "mailbox": "testB", "uid": 2}
  s.process(json.dumps(testcommand), cb, None)

  testcommand = {"command": "setflags", "account":"via@matthewvia.info", "mailbox": "testB", "uid": 2, "flags": ["\\Deleted", "\\Seen"]}
  s.process(json.dumps(testcommand), cb, None)
  
  testcommand = {"command": "getflags", "account":"via@matthewvia.info", "mailbox": "testB", "uid": 2}
  s.process(json.dumps(testcommand), cb, None)

