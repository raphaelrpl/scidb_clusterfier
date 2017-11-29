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
import sys
import json


def usage(app_name):
    print("usage: {} config.file.json start|stop|status".format(app_name))


def validate_config(config):
    # TODO validate config file
    if "name" not in config:
        raise ValueError('you must set a name to scidb cluster')


def create_scidb_config(config, server_id):
    for server in config["servers"]:
        if server["id"] == server_id:
            print("[{}]".format(server["host"]))


def test_ssh(config):
    # TODO
    return True

def test_docker(config):
    # TODO
    return True

def main():
    if len(sys.argv) < 3:
        usage(sys.argv[0])
        raise ValueError('invalid number of arguments')

    file_name = sys.argv[1]
    operation = sys.argv[2]

    if operation not in ("start", "stop", "status"):
        usage(sys.argv[0])
        raise ValueError('invalid operation: {}'.format(operation))

    config = json.load(open(file_name))

    validate_config(config)
    test_ssh(config)

    for server in config["servers"]:
        create_scidb_config(config, server["id"])


if __name__ == "__main__":
    main()
