#!/usr/bin/env python
# -*- coding: utf-8

import pytest
from fiaas_deploy_daemon.deployer.kubernetes.service import ServiceDeployer
from fiaas_deploy_daemon.config import Configuration
from mock import create_autospec
from requests import Response

SELECTOR = {'app': 'testapp'}
LABELS = {"service": "pass through"}
SERVICES_URI = '/api/v1/namespaces/default/services/'


class TestServiceDeployer(object):
    @pytest.fixture(params=("ClusterIP", "NodePort", "LoadBalancer"))
    def service_type(self, request):
        return request.param

    @pytest.fixture
    def deployer(self, service_type):
        config = create_autospec(Configuration([]), spec_set=True)
        config.service_type = service_type
        return ServiceDeployer(config)

    def test_deploy_new_service(self, deployer, service_type, post, app_spec):
        deployer.deploy(app_spec, SELECTOR, LABELS)

        expected_service = {
            'spec': {
                'selector': SELECTOR,
                'type': service_type,
                "loadBalancerSourceRanges": [
                ],
                'ports': [{
                    'protocol': 'TCP',
                    'targetPort': 8080,
                    'name': 'http',
                    'port': 80
                }],
                'sessionAffinity': 'None'
            },
            'metadata': pytest.helpers.create_metadata('testapp', labels=LABELS)
        }

        pytest.helpers.assert_any_call(post, SERVICES_URI, expected_service)

    def test_deploy_new_service_with_multiple_ports(self, deployer, service_type, post, app_spec_thrift_and_http):
        deployer.deploy(app_spec_thrift_and_http, SELECTOR, LABELS)

        expected_service = {
            'spec': {
                'selector': SELECTOR,
                'type': service_type,
                "loadBalancerSourceRanges": [],
                'ports': [
                    {
                        'protocol': 'TCP',
                        'targetPort': 8080,
                        'name': 'http',
                        'port': 80
                    },
                    {
                        'protocol': 'TCP',
                        'targetPort': 7999,
                        'name': 'thrift',
                        'port': 7999
                    },
                ],
                'sessionAffinity': 'None'
            },
            'metadata': pytest.helpers.create_metadata('testapp', labels=LABELS,
                                                       annotations={"fiaas/tcp_port_names": "thrift"})
        }
        pytest.helpers.assert_any_call(post, SERVICES_URI, expected_service)

    def test_deploy_new_service_with_multiple_tcp_ports(self, deployer, service_type, post,
                                                        app_spec_multiple_thrift_ports):
        deployer.deploy(app_spec_multiple_thrift_ports, SELECTOR, LABELS)

        expected_service = {
            'spec': {
                'selector': SELECTOR,
                'type': service_type,
                "loadBalancerSourceRanges": [],
                'ports': [
                    {
                        'protocol': 'TCP',
                        'targetPort': 7999,
                        'name': 'thrift1',
                        'port': 7999
                    },
                    {
                        'protocol': 'TCP',
                        'targetPort': 8000,
                        'name': 'thrift2',
                        'port': 8000
                    },
                ],
                'sessionAffinity': 'None'
            },
            'metadata': pytest.helpers.create_metadata('testapp', labels=LABELS,
                                                       annotations={"fiaas/tcp_port_names": "thrift1,thrift2"})
        }
        pytest.helpers.assert_any_call(post, SERVICES_URI, expected_service)

    def test_update_service(self, deployer, service_type, get, post, put, app_spec):
        mock_response = create_autospec(Response)
        mock_response.json.return_value = {
            'spec': {
                'selector': SELECTOR,
                'type': service_type,
                "loadBalancerSourceRanges": [
                ],
                'ports': [{
                    'protocol': 'TCP',
                    'targetPort': 8081,
                    'name': 'http',
                    'port': 81,
                    'nodePort': 34567
                }],
                'sessionAffinity': 'None'
            },
            'metadata': pytest.helpers.create_metadata('testapp', labels=LABELS)
        }
        get.side_effect = None
        get.return_value = mock_response

        deployer.deploy(app_spec, SELECTOR, LABELS)

        expected_service = {
            'spec': {
                'selector': SELECTOR,
                'type': service_type,
                "loadBalancerSourceRanges": [
                ],
                'ports': [{
                    'protocol': 'TCP',
                    'targetPort': 8080,
                    'name': 'http',
                    'port': 80,
                    'nodePort': 34567
                }],
                'sessionAffinity': 'None'
            },
            'metadata': pytest.helpers.create_metadata('testapp', labels=LABELS)
        }

        pytest.helpers.assert_no_calls(post)
        pytest.helpers.assert_any_call(put, SERVICES_URI + "testapp", expected_service)
