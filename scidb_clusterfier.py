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
from io import BytesIO as StringIO


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

    print(output.getvalue())

    output.close()


def test_ssh(config):
    pass
    # for server in config["servers"]:
    #     address = "{user}@{host}".format(**{"user": server["user"], "host": server["host"]})
    #     ssh = subprocess.Popen(['ssh', address],
    #                            stdin=subprocess.PIPE,
    #                            stdout=subprocess.PIPE,
    #                            universal_newlines=True,
    #                            bufsize=0)
    #
    #     out, err = ssh.communicate()
    #
    #     if err:
    #         raise StandardError(err)
    #
    #     print(out)

    #### Using external library - install (paramiko) (import paramiko)
    # for server in config["servers"]:
    #     client = paramiko.SSHClient()
    #     client.load_system_host_keys()
    #     client.set_missing_host_key_policy(paramiko.WarningPolicy)
    #     client.connect(server["host"], username=server["user"])
    #     stdin, stdout, stderr = client.exec_command("uptime")
    #     print stdout.read()


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
