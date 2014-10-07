# Copyright 2011 OpenStack Foundation
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

import webob.exc

from nova.api.openstack import common
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api.openstack import xmlutil
from nova import compute
from nova import exception
from nova.i18n import _


authorize = extensions.extension_authorizer('compute', 'server_diagnostics')
sd_nsmap = {None: wsgi.XMLNS_V11}


class ServerDiagnosticsTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('diagnostics')
        elem = xmlutil.SubTemplateElement(root, xmlutil.Selector(0),
                                          selector=xmlutil.get_items)
        elem.text = 1
        return xmlutil.MasterTemplate(root, 1, nsmap=sd_nsmap)


class ServerDiagnosticsController(object):
    def __init__(self):
        self.compute_api = compute.API()

    @wsgi.serializers(xml=ServerDiagnosticsTemplate)
    def index(self, req, server_id):
        context = req.environ["nova.context"]
        authorize(context)
        try:
            instance = self.compute_api.get(context, server_id,
                want_objects=True)
        except exception.InstanceNotFound as e:
            raise webob.exc.HTTPNotFound(explanation=e.format_message())

        try:
            return self.compute_api.get_diagnostics(context, instance)
        except exception.InstanceInvalidState as state_error:
            common.raise_http_conflict_for_instance_invalid_state(state_error,
                    'get_diagnostics', server_id)
        except NotImplementedError:
            msg = _("Unable to get diagnostics, functionality not implemented")
            raise webob.exc.HTTPNotImplemented(explanation=msg)


class Server_diagnostics(extensions.ExtensionDescriptor):
    """Allow Admins to view server diagnostics through server action."""

    name = "ServerDiagnostics"
    alias = "os-server-diagnostics"
    namespace = ("http://docs.openstack.org/compute/ext/"
                 "server-diagnostics/api/v1.1")
    updated = "2011-12-21T00:00:00Z"

    def get_resources(self):
        parent_def = {'member_name': 'server', 'collection_name': 'servers'}
        # NOTE(bcwaldon): This should be prefixed with 'os-'
        ext = extensions.ResourceExtension('diagnostics',
                                           ServerDiagnosticsController(),
                                           parent=parent_def)
        return [ext]
