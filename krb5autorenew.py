# python script to obtain password for kerberos credentials, and
# then indefinitely keep renewing those credentials.  Used primarily
# for long-running processes where code is expected to be able to
# read/write to NFSv4 file shares
#
# Initial revision: March 20, 2019
# Author: Greg Oster
# Email: oster@cs.usask.ca


from __future__ import print_function
import argparse
import getpass
from subprocess import Popen, PIPE
import os
import pexpect
import time

# Talk to kinit with the given principal and password and obtain tickets
#
# Paths to /usr/bin/kinit and /usr/bin/klist are made explicit, as this
# code will happily send the password to any program that prints a ":".
# 
def renew_ticket(principal,password):
    
    kinit = pexpect.spawn('/usr/bin/kinit ' + principal)
    kinit.expect(':')
    kinit.sendline(password)
    kinit.readlines()
    kinit.expect(pexpect.EOF)

    if kinit.exitstatus == 0:
        print(os.system('/usr/bin/klist'))
        return 1
    return 0


# Grab an NSID from command-line arguments, if provided
parser = argparse.ArgumentParser()
parser.add_argument("--NSID",help="The NSID you wish you use with Kerberos")
args = parser.parse_args()
nsid = args.NSID

# If an NSID is not provided, determine who is running the script by
# executing 'whoami'
if nsid == None:
    whoami = Popen(["whoami"], stdout=PIPE)
    (out,err) = whoami.communicate()
    nsid=str(out.decode('ascii')).rstrip()

# Build the principal to use
principal=nsid+"@USASK.CA"

# Obtain a password, and validate it against the realm
while True:
    password = getpass.getpass("Password for "+principal+": ").encode('ascii')

    if renew_ticket(principal, password):
        break;

# keep running, and renew tickets after a fixed amount of time
while True:
    # sleep for 2 hours
    time.sleep(7200)
    res = renew_ticket(principal, password)
    if res == 0:
        print("Unable to renew ticket!")

        
# XXX TODO:
# - error checking on whoami and kinit processes
