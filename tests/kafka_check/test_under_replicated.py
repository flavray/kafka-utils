# -*- coding: utf-8 -*-
# Copyright 2016 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from kafka.common import PartitionMetadata

from kafka_utils.kafka_check.commands.under_replicated import _prepare_host_list
from kafka_utils.kafka_check.commands.under_replicated import _process_topic_partition_metadata


BROKER_LIST_WITH_ONE = {
    1000: {
        'host': 'hostname00',
        'port': 1234,
    },
}

BROKER_LIST = {
    101: {
        'host': 'hostname1',
        'port': 1234,
    },
    100: {
        'host': 'hostname0',
        'port': 1234,
    },
    1001: {
        'host': 'hostname2',
        'port': 1234,
    },
}


def test__process_topic_partition_metadata_empty():
    assert _process_topic_partition_metadata({}, 10) == {}


def test__process_topic_partition_metadata_all_good():
    METADATA_RESPONSE = {
        'topic0': {
            0: PartitionMetadata(
                topic='topic0',
                partition=0,
                leader=13,
                replicas=(13, 100),
                isr=(13, 100),
                error=0,
            ),
            1: PartitionMetadata(
                topic='topic0',
                partition=1,
                leader=100,
                replicas=(13, 100),
                isr=(13, 100),
                error=0,
            ),
        },
        'topic1': {
            0: PartitionMetadata(
                topic='topic1',
                partition=0,
                leader=666,
                replicas=(300, 500, 666),
                isr=(300, 500, 666),
                error=0,
            ),
            1: PartitionMetadata(
                topic='topic1',
                partition=1,
                leader=300,
                replicas=(300, 500, 666),
                isr=(300, 500, 666),
                error=0,
            ),
        },
    }
    result = _process_topic_partition_metadata(METADATA_RESPONSE, 2)
    assert result == {}


def test__process_topic_partition_metadata():
    METADATA_RESPONSE = {
        'topic0': {
            0: PartitionMetadata(
                topic='topic0',
                partition=0,
                leader=13,
                replicas=(13, 100),
                isr=(13, 100),
                error=0,
            ),
            1: PartitionMetadata(
                topic='topic0',
                partition=1,
                leader=100,
                replicas=(13, 100),
                isr=(13, 100),
                error=0,
            ),
        },
        'topic1': {
            0: PartitionMetadata(
                topic='topic1',
                partition=0,
                leader=666,
                replicas=(300, 500, 666),  # one more replica
                isr=(500, 666),
                error=0,
            ),
            1: PartitionMetadata(
                topic='topic1',
                partition=1,
                leader=300,
                replicas=(300, 500, 666),
                isr=(300, 500, 666),
                error=0,
            ),
        },
    }
    result = _process_topic_partition_metadata(METADATA_RESPONSE, 2)
    assert result == {}

    result = _process_topic_partition_metadata(METADATA_RESPONSE, 3)
    assert result == {300: [('topic1', 0)]}


def test__process_topic_partition_metadata_few_for_one_broker():
    METADATA_RESPONSE = {
        'topic0': {
            0: PartitionMetadata(
                topic='topic0',
                partition=0,
                leader=100,
                replicas=(13, 100),
                isr=(100,),
                error=0,
            ),
            1: PartitionMetadata(
                topic='topic0',
                partition=1,
                leader=100,
                replicas=(13, 100),
                isr=(13, 100),
                error=0,
            ),
        },
        'topic1': {
            0: PartitionMetadata(
                topic='topic1',
                partition=0,
                leader=666,
                replicas=(13, 500, 666),
                isr=(13, 500, 666),
                error=0,
            ),
            1: PartitionMetadata(
                topic='topic1',
                partition=1,
                leader=666,
                replicas=(13, 500, 666),
                isr=(666,),
                error=0,
            ),
        },
    }
    result = _process_topic_partition_metadata(METADATA_RESPONSE, 2)

    expected = {13: [('topic0', 0), ('topic1', 1)], 500: [('topic1', 1)]}

    result_ordered = {}
    for k, v in result.items():
        result_ordered[k] = sorted(v)
    assert result_ordered == expected


def test__prepare_host_list():
    assert _prepare_host_list(BROKER_LIST) == 'hostname2:1234,hostname0:1234,hostname1:1234'


def test__prepare_host_list_only_one():
    assert _prepare_host_list(BROKER_LIST_WITH_ONE) == 'hostname00:1234'
