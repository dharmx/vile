#!/usr/bin/env python3.10
"""
A python script that shows the number of inboxes
 - Needs to be used with EWW widgets
 - Add a custom app to your gmail account and then
   put the generated password in side-utils directory
   file.
"""

import sys
from imaplib import IMAP4_SSL
from os import getenv
from socket import gaierror

from dotenv import load_dotenv

load_dotenv(f"{getenv('XDG_CONFIG_HOME')}/eww/structs/side-utils/.email-env")
mail = None
try:
    mail: IMAP4_SSL = IMAP4_SSL("imap.gmail.com")
except gaierror as error:
    print("Offline")
    sys.exit(0)

mail.login(getenv("EMAIL"), getenv("PASSWORD"))
mail.select("INBOX")
inbox: int = len(mail.search(None, "UNSEEN")[1][0].split())

print("500+" if inbox > 500 else inbox)
mail.close()
mail.logout()

# vim:ft=python:nowrap:number:smartindent:smarttab:smartcase
