# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 IBM Corp.
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


import webob.exc

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova import db
from nova.openstack.common.gettextutils import _

authorize = extensions.extension_authorizer('compute', 'cloudpipe_update')


class CloudpipeUpdateController(wsgi.Controller):
    """Handle updating the vpn ip/port for cloudpipe instances."""

    def __init__(self):
        super(CloudpipeUpdateController, self).__init__()

    @wsgi.action("update")
    def update(self, req, id, body):
        """Configure cloudpipe parameters for the project."""

        context = req.environ['nova.context']
        authorize(context)

        if id != "configure-project":
            msg = _("Unknown action %s") % id
            raise webob.exc.HTTPBadRequest(explanation=msg)

        project_id = context.project_id

        try:
            params = body['configure_project']
            vpn_ip = params['vpn_ip']
            vpn_port = params['vpn_port']
        except (TypeError, KeyError):
            raise webob.exc.HTTPUnprocessableEntity()

        networks = db.project_get_networks(context, project_id)
        for network in networks:
            db.network_update(context, network['id'],
                              {'vpn_public_address': vpn_ip,
                               'vpn_public_port': int(vpn_port)})
        return webob.exc.HTTPAccepted()


class Cloudpipe_update(extensions.ExtensionDescriptor):
    """Adds the ability to set the vpn ip/port for cloudpipe instances."""

    name = "CloudpipeUpdate"
    alias = "os-cloudpipe-update"
    namespace = "http://docs.openstack.org/compute/ext/cloudpipe-update/api/v2"
    updated = "2012-11-14T00:00:00+00:00"

    def get_controller_extensions(self):
        controller = CloudpipeUpdateController()
        extension = extensions.ControllerExtension(self, 'os-cloudpipe',
                                                   controller)
        return [extension]
