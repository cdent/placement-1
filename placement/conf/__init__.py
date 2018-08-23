# Copyright 2015 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# This package got introduced during the Mitaka cycle in 2015 to
# have a central place where the config options of Nova can be maintained.
# For more background see the blueprint "centralize-config-options"
from __future__ import absolute_import

from oslo_config import cfg

# FIXME(cdent): this needs to be more fully trimmed, what's been done now is
# just to get tests to run

from placement.conf import api
from placement.conf import base
from placement.conf import cache
from placement.conf import cells
from placement.conf import cinder
from placement.conf import conductor
from placement.conf import configdrive
from placement.conf import console
from placement.conf import consoleauth
from placement.conf import database
from placement.conf import devices
from placement.conf import ephemeral_storage
from placement.conf import flavors
from placement.conf import guestfs
from placement.conf import hyperv
from placement.conf import key_manager
from placement.conf import mks
from placement.conf import notifications
from placement.conf import novnc
from placement.conf import osapi_v21
from placement.conf import paths
from placement.conf import pci
from placement.conf import placement
from placement.conf import powervm
from placement.conf import quota
from placement.conf import rdp
from placement.conf import remote_debug
from placement.conf import rpc
from placement.conf import serial_console
from placement.conf import service
from placement.conf import service_token
from placement.conf import servicegroup
from placement.conf import spice
from placement.conf import upgrade_levels
from placement.conf import vendordata
from placement.conf import vnc
from placement.conf import workarounds
from placement.conf import wsgi
from placement.conf import xenserver

CONF = cfg.CONF

api.register_opts(CONF)
base.register_opts(CONF)
cache.register_opts(CONF)
cells.register_opts(CONF)
cinder.register_opts(CONF)
conductor.register_opts(CONF)
configdrive.register_opts(CONF)
console.register_opts(CONF)
consoleauth.register_opts(CONF)
database.register_opts(CONF)
devices.register_opts(CONF)
ephemeral_storage.register_opts(CONF)
flavors.register_opts(CONF)
guestfs.register_opts(CONF)
hyperv.register_opts(CONF)
mks.register_opts(CONF)
key_manager.register_opts(CONF)
notifications.register_opts(CONF)
novnc.register_opts(CONF)
osapi_v21.register_opts(CONF)
paths.register_opts(CONF)
pci.register_opts(CONF)
placement.register_opts(CONF)
powervm.register_opts(CONF)
quota.register_opts(CONF)
rdp.register_opts(CONF)
rpc.register_opts(CONF)
serial_console.register_opts(CONF)
service.register_opts(CONF)
service_token.register_opts(CONF)
servicegroup.register_opts(CONF)
spice.register_opts(CONF)
upgrade_levels.register_opts(CONF)
vendordata.register_opts(CONF)
vnc.register_opts(CONF)
workarounds.register_opts(CONF)
wsgi.register_opts(CONF)
xenserver.register_opts(CONF)

remote_debug.register_cli_opts(CONF)
