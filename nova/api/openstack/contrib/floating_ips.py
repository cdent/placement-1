# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# Copyright 2011 Grid Dynamics
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
#    under the License
from webob import exc

from nova import exception
from nova import network
from nova.api.openstack import faults
from nova.api.openstack import extensions

def _translate_floating_ip_detail_view(context, floating_ip):
    #TODO(enugaev) implement view
    return None

def _translate_floating_ips_view(context, floating_ips):
    #TODO(adiantum) implement view
    return []

class FloatingIPController(object):
    """The Volumes API controller for the OpenStack API."""

    _serialization_metadata = {
        'application/xml': {
            "attributes": {
                "floating_ip": [
                    "id",
                    "ip",
                    "instance_id",
                    "fixed_ip",
                    ]}}}

    def __init__(self):
        self.network_api = network.API()
        super(FloatingIPController, self).__init__()

    def show(self, req, id):
        """Return data about the given volume."""
        context = req.environ['nova.context']

        try:
            floating_ip = self.network_api.get(context, id)
        except exception.NotFound:
            return faults.Fault(exc.HTTPNotFound())

        return {'floating_ips': _translate_floating_ip_detail_view(context,
                                                             floating_ip)}

    def index(self, req):
        context = req.environ['nova.context']

        floating_ips = self.network_api.list(context)

        return {'floating_ips' : _translate_floating_ips_view(context,
                                                              floating_ips)}


class Floating_ips(extensions.ExtensionDescriptor):
    def get_name(self):
        return "Floating_ips"

    def get_alias(self):
        return "FLOATING_IPS"

    def get_description(self):
        return "Floating IPs support"

    def get_namespace(self):
        return "http://docs.openstack.org/ext/floating_ips/api/v1.1"

    def get_updated(self):
        return "2011-06-16T00:00:00+00:00"

    def get_resources(self):
        resources = []

        res = extensions.ResourceExtension('floating_ips',
                                        FloatingIPController(),
                                        collection_actions={})
        resources.append(res)

        return resources

