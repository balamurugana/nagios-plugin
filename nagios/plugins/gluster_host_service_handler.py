#!/usr/bin/python
#
# gluster_host_service_handler.py -- Event handler which checks the 
# status of defined services and accordingly changes the host status
#
# Copyright (C) 2014 Red Hat Inc
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
# 


import os
import sys
import datetime
import socket

STATUS_OK = "OK"
STATUS_WARNING = "WARNING"
STATUS_CRITICAL = "CRITICAL"
STATUS_UNKNOWN = "UNKNOWN"
SRVC_STATE_TYPE_SOFT = "SOFT"
SRVC_STATE_TYPE_HARD = "HARD"
statusCodes = {STATUS_OK: 0, STATUS_WARNING: 1, STATUS_CRITICAL: 2, STATUS_UNKNOWN: 3}
NAGIOS_COMMAND_FILE = "/var/spool/nagios/cmd/nagios.cmd"
SRVC_LIST = ['Disk Utilization', 'Cpu Utilization', 'Memory Utilization', 'Swap Utilization', 'Network Utilization']
_socketPath='/var/spool/nagios/cmd/live'

# Shows the usage of the script
def showUsage():
    usage = "Usage: %s <Service State (OK/WARNING/CRITICAL/UNKNOWN)> <Service State Type (SOFT/HARD)> <No of Service attempts> <Host Address> <Service Description>\n" % os.path.basename(sys.argv[0])
    sys.stderr.write(usage)


# Method to change the host status
def update_host_state(hostAddr, srvcName, statusCode):
    now = datetime.datetime.now()
    cmdStr = "[%s] PROCESS_HOST_CHECK_RESULT;%s;%s;Host Status WARNING - Some of the services in CRITICAL state\n" % (now, hostAddr, statusCode)
    f = open(NAGIOS_COMMAND_FILE, "w")
    f.write(cmdStr)
    f.close()


# Method to execute livestatus
def checkLiveStatus(hostAddr, srvc):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(_socketPath)

    # Write command to socket
    cmd = "GET services\nColumns: state\nFilter: description = %s\nFilter: host_address = %s\n" % (srvc, hostAddr)
    s.send(cmd)

    # Close socket
    s.shutdown(socket.SHUT_WR)

    # Read the answer
    answer = s.recv(1000)

    # Parse the answer into a table
    table = [line.split(';') for line in answer.split('\n')[:-1]]

    if len(table) > 0 and len(table[0]) > 0:
        return int(table[0][0])
    else:
        return STATUS_UNKNOWN


# Method to change the host state to UP based on other service type status
def check_and_update_host_state_to_up(hostAddr, srvcName):
    finalState = 0
    for item in SRVC_LIST:
        if item != srvcName:
            finalState = finalState | checkLiveStatus(hostAddr, item)

    if finalState == statusCodes[STATUS_OK]:
        update_host_state(hostAddr, srvcName, STATUS_OK)


# Main method
if __name__ == "__main__":
    # Check the command line arguments
    if len(sys.argv) < 6:
        showUsage()
        sys.exit(-1)

    srvcState = sys.argv[1]
    srvcStateType = sys.argv[2]
    attempts = sys.argv[3]
    hostAddr = sys.argv[4]
    # Service description might contain spaces
    srvcName = ''
    for count in range(5, len(sys.argv)):
        srvcName += sys.argv[count] + ' '
    srvcName = srvcName.strip()

    # Swicth over the service state values and do the needful
    if srvcState == STATUS_CRITICAL:
        if srvcStateType == SRVC_STATE_TYPE_SOFT:
            if int(attempts) == 3:
                print "Updating the host status to warning (3rd SOFT critical state)..."
                update_host_state(hostAddr, srvcName, statusCodes[STATUS_WARNING])
        elif srvcStateType == SRVC_STATE_TYPE_HARD:
            print "Updating the host status to warning..."
            update_host_state(hostAddr, srvcName, statusCodes[STATUS_WARNING])
    elif srvcState == STATUS_OK:
        check_and_update_host_state_to_up(hostAddr, srvcName)

    sys.exit(0)

