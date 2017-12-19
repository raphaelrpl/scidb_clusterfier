# -*- coding: utf-8 -*-
#
#   Copyright (C) 2017 National Institute For Space Research (INPE) - Brazil.
#
#  This file is part of scidb_cluster toolkit.
#
#  scidb_cluster toolkit is free software: you can
#  redistribute it and/or modify it under the terms of the
#  GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License,
#  or (at your option) any later version.
#
#  scidb_cluster toolkit is distributed in the hope that
#  it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with scidb_cluster toolkit. See LICENSE. If not, write to
#  e-sensing team at <esensing-team@dpi.inpe.br>.
#
import json
import argparse
import subprocess
from os import path
from io import BytesIO as StringIO
from stream import NonBlockingStreamReader


class SSH(object):
    user = None
    host = None

    def __init__(self, host, user):
        """
        Initializes SSH Object
        :param host: Host address
        :param user: User to connect
        """
        self.host = host
        self.user = user
        self._stream = None
        self._stdout = None

    def _uri(self):
        """
        Utility function to retrieve SSH connection string
        """
        return "{0}@{1}".format(self.user, self.host)

    def _read(self):
        data = ""

        while True:
            output = self._stdout.read_line(0.3)

            if not output:
                break

            data += output
        return data

    def open(self):
        uri = self._uri()

        self._stream = subprocess.Popen(['ssh', '-T', uri],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True)

        self._stdout = NonBlockingStreamReader(self._stream.stdout)

        if self._stream.stdin.closed:
            raise StandardError("No connection. Input and Output stream is closed")

        # Reading connection output
        self._read()

    def is_open(self):
        return self._stream.poll() is None

    def execute(self, command):
        if command is None or not isinstance(command, basestring):
            raise StandardError("Invalid command")

        if not self.is_open():
            raise StandardError("No connection alive")

        self._stream.stdin.write("{0}\n".format(command))

        a = self._read()
        print a

    def close(self):
        if self.is_open():
            self._stream.terminate()
            self._stream = None


def validate_config(config):
    # TODO validate config file
    if "name" not in config:
        raise ValueError('you must set a name to scidb cluster')


def create_scidb_config(config, server_id):
    """
    Args:
        config (dict): JSON configuration
        server_id (int): Current Server Identifier
    """
    output = StringIO()
    output.write("[{0}]\n".format(config["name"]))

    server = config["servers"][server_id]

    for serv in config["servers"]:
        workers_size = len(serv["workers"])
        output.write("server-{0}={1},{2}\n".format(serv["id"], serv["host"], workers_size))

    for (key, value) in config["config"].iteritems():
        output.write("{0}={0}\n".format(key, value))
    
    output.write("# server-{0}\n".format(server_id))
    
    workers_size = len(server["workers"])
    for worker_id in xrange(workers_size):
        worker = server["workers"][worker_id]
        output.write("data-dir-prefix-{0}-{1}={2}/{3}.{0}.{1}\n".format(server_id,
                                                                        worker_id,
                                                                        worker["host_dir"],
                                                                        config["name"]))

    data = output.getvalue()

    output.close()

    ssh = SSH(server["host"], server["user"])

    ssh.open()

    for worker in server["workers"]:
        absolute_file_path = path.join(worker["host_dir"], "{0}.ini".format(config["name"]))
        ssh.execute("echo \"{0}\" > {1}".format(data, absolute_file_path))

    ssh.close()


def test_ssh(config):
    for server in config["servers"]:
        ssh = SSH(server["host"], server["user"])
        ssh.open()
        ssh.execute("uptime")
        ssh.close()


def test_docker(config):
    # TODO
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="JSON file containing SciDB configuration")
    parser.add_argument("operation", help="Operation")
    args = parser.parse_args()

    file_name = args.filename
    operation = args.operation

    if operation not in ("start", "stop", "status"):
        raise ValueError('invalid operation: {}'.format(operation))

    config = json.load(open(file_name))

    validate_config(config)
    test_ssh(config)

    for server in config["servers"]:
        create_scidb_config(config, server["id"])


if __name__ == "__main__":
    main()
