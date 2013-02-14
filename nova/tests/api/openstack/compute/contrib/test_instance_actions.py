# Copyright 2013 Rackspace Hosting
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

import copy
import uuid

from lxml import etree
from webob import exc

from nova.api.openstack.compute.contrib import instance_actions
from nova import db
from nova import exception
from nova.openstack.common import policy
from nova import test
from nova.tests.api.openstack import fakes
from nova.tests import fake_instance_actions

FAKE_UUID = fake_instance_actions.FAKE_UUID
FAKE_REQUEST_ID = fake_instance_actions.FAKE_REQUEST_ID1


def format_action(action):
    '''Remove keys that aren't serialized.'''
    if 'id' in action:
        del(action['id'])
    if 'finish_time' in action:
        del(action['finish_time'])
    return action


def format_event(event):
    '''Remove keys that aren't serialized.'''
    if 'id' in event:
        del(event['id'])
    return event


class InstanceActionsPolicyTest(test.TestCase):
    def setUp(self):
        super(InstanceActionsPolicyTest, self).setUp()
        self.controller = instance_actions.InstanceActionsController()

    def test_list_actions_restricted_by_project(self):
        rules = policy.Rules({'compute:get': policy.parse_rule(''),
                              'compute_extension:instance_actions':
                               policy.parse_rule('project_id:%(project_id)s')})
        policy.set_rules(rules)

        def fake_instance_get_by_uuid(context, instance_id):
            return {'name': 'fake', 'project_id': '%s_unequal' %
                                                            context.project_id}

        self.stubs.Set(db, 'instance_get_by_uuid', fake_instance_get_by_uuid)
        req = fakes.HTTPRequest.blank('/v2/123/servers/12/os-instance-actions')
        self.assertRaises(exception.NotAuthorized, self.controller.index, req,
                          str(uuid.uuid4()))

    def test_get_action_restricted_by_project(self):
        rules = policy.Rules({'compute:get': policy.parse_rule(''),
                              'compute_extension:instance_actions':
                               policy.parse_rule('project_id:%(project_id)s')})
        policy.set_rules(rules)

        def fake_instance_get_by_uuid(context, instance_id):
            return {'name': 'fake', 'project_id': '%s_unequal' %
                                                            context.project_id}

        self.stubs.Set(db, 'instance_get_by_uuid', fake_instance_get_by_uuid)
        req = fakes.HTTPRequest.blank(
                                    '/v2/123/servers/12/os-instance-actions/1')
        self.assertRaises(exception.NotAuthorized, self.controller.show, req,
                          str(uuid.uuid4()), '1')


class InstanceActionsTest(test.TestCase):
    def setUp(self):
        super(InstanceActionsTest, self).setUp()
        self.controller = instance_actions.InstanceActionsController()
        self.fake_actions = copy.deepcopy(fake_instance_actions.FAKE_ACTIONS)
        self.fake_events = copy.deepcopy(fake_instance_actions.FAKE_EVENTS)

        def fake_instance_get_by_uuid(context, instance_id):
            return {'name': 'fake', 'project_id': context.project_id}

        self.stubs.Set(db, 'instance_get_by_uuid', fake_instance_get_by_uuid)

    def test_list_actions(self):
        def fake_get_actions(context, uuid):
            return self.fake_actions[uuid].values()

        self.stubs.Set(db, 'actions_get', fake_get_actions)
        req = fakes.HTTPRequest.blank('/v2/123/servers/12/os-instance-actions')
        res_dict = self.controller.index(req, FAKE_UUID)
        for res in res_dict['instanceActions']:
            fake_action = self.fake_actions[FAKE_UUID][res['request_id']]
            fake_action = format_action(fake_action)
            self.assertEqual(fake_action, res)

    def test_get_action_with_events_allowed(self):
        def fake_get_action(context, uuid, request_id):
            return self.fake_actions[uuid][request_id]

        def fake_get_events(context, action_id):
            return self.fake_events[action_id]

        self.stubs.Set(db, 'action_get_by_request_id', fake_get_action)
        self.stubs.Set(db, 'action_events_get', fake_get_events)
        req = fakes.HTTPRequest.blank(
                                '/v2/123/servers/12/os-instance-actions/1',
                                use_admin_context=True)
        res_dict = self.controller.show(req, FAKE_UUID, FAKE_REQUEST_ID)
        fake_action = self.fake_actions[FAKE_UUID][FAKE_REQUEST_ID]
        fake_events = self.fake_events[fake_action['id']]
        fake_events = [format_event(event) for event in fake_events]
        fake_action = format_action(fake_action)
        fake_action['events'] = fake_events
        self.assertEqual(fake_action, res_dict['instanceAction'])

    def test_get_action_with_events_not_allowed(self):
        def fake_get_action(context, uuid, request_id):
            return self.fake_actions[uuid][request_id]

        def fake_get_events(context, action_id):
            return self.fake_events[action_id]

        self.stubs.Set(db, 'action_get_by_request_id', fake_get_action)
        self.stubs.Set(db, 'action_events_get', fake_get_events)
        rules = policy.Rules({'compute:get': policy.parse_rule(''),
                              'compute_extension:instance_actions':
                                policy.parse_rule(''),
                              'compute_extension:instance_actions:events':
                                policy.parse_rule('is_admin:True')})
        policy.set_rules(rules)
        req = fakes.HTTPRequest.blank(
                                '/v2/123/servers/12/os-instance-actions/1')
        res_dict = self.controller.show(req, FAKE_UUID, FAKE_REQUEST_ID)
        fake_action = self.fake_actions[FAKE_UUID][FAKE_REQUEST_ID]
        fake_action = format_action(fake_action)
        self.assertEqual(fake_action, res_dict['instanceAction'])

    def test_action_not_found(self):
        def fake_no_action(context, uuid, action_id):
            return None

        self.stubs.Set(db, 'action_get_by_request_id', fake_no_action)
        req = fakes.HTTPRequest.blank(
                                '/v2/123/servers/12/os-instance-actions/1')
        self.assertRaises(exc.HTTPNotFound, self.controller.show, req,
                          FAKE_UUID, FAKE_REQUEST_ID)


class InstanceActionsSerializerTest(test.TestCase):
    def setUp(self):
        super(InstanceActionsSerializerTest, self).setUp()
        self.fake_actions = copy.deepcopy(fake_instance_actions.FAKE_ACTIONS)
        self.fake_events = copy.deepcopy(fake_instance_actions.FAKE_EVENTS)

    def _verify_instance_action_attachment(self, attach, tree):
        for key in attach.keys():
            if key != 'events':
                self.assertEqual(attach[key], tree.get(key),
                                 '%s did not match' % key)

    def _verify_instance_action_event_attachment(self, attach, tree):
        for key in attach.keys():
            self.assertEqual(attach[key], tree.get(key),
                             '%s did not match' % key)

    def test_instance_action_serializer(self):
        serializer = instance_actions.InstanceActionTemplate()
        action = self.fake_actions[FAKE_UUID][FAKE_REQUEST_ID]
        text = serializer.serialize({'instanceAction': action})
        tree = etree.fromstring(text)

        action = format_action(action)
        self.assertEqual('instanceAction', tree.tag)
        self._verify_instance_action_attachment(action, tree)
        found_events = False
        for child in tree:
            if child.tag == 'events':
                found_events = True
        self.assertFalse(found_events)

    def test_instance_action_events_serializer(self):
        serializer = instance_actions.InstanceActionTemplate()
        action = self.fake_actions[FAKE_UUID][FAKE_REQUEST_ID]
        event = self.fake_events[action['id']][0]
        action['events'] = [event, event]
        text = serializer.serialize({'instanceAction': action})
        tree = etree.fromstring(text)

        action = format_action(action)
        self.assertEqual('instanceAction', tree.tag)
        self._verify_instance_action_attachment(action, tree)

        event = format_event(event)
        found_events = False
        for child in tree:
            if child.tag == 'events':
                found_events = True
                for key in event:
                    self.assertEqual(event[key], child.get(key))
        self.assertTrue(found_events)

    def test_instance_actions_serializer(self):
        serializer = instance_actions.InstanceActionsTemplate()
        action_list = self.fake_actions[FAKE_UUID].values()
        text = serializer.serialize({'instanceActions': action_list})
        tree = etree.fromstring(text)

        action_list = [format_action(action) for action in action_list]
        self.assertEqual('instanceActions', tree.tag)
        self.assertEqual(len(action_list), len(tree))
        for idx, child in enumerate(tree):
            self.assertEqual('instanceAction', child.tag)
            request_id = child.get('request_id')
            self._verify_instance_action_attachment(
                                    self.fake_actions[FAKE_UUID][request_id],
                                    child)
