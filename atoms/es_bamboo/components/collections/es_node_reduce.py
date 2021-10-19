# -*- coding:utf-8 _*-
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service


class EsNodeReduceService(Service):

    def execute(self, data, parent_data):
        data.outputs.result_message = "success"
        return True

    def inputs_format(self):
        return [
            Service.InputItem(name='dict action_info', key='act_info', type='dict', required=True),
        ]

    def outputs_format(self):
        return [

            Service.OutputItem(name='job_instance_id', key='job_instance_id', type='int'),
            Service.OutputItem(name='result_message', key='result_message', type='str'),
            Service.OutputItem(name='target_ips', key='target_ips', type='list')
        ]


class InputEsClusterComponent(Component):
    name = __name__
    code = 'es_node_reduce_action'
    bound_service = EsNodeReduceService
