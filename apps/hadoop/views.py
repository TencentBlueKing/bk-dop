# -*- coding:utf-8 _*-
from django.http import JsonResponse

from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action

from apps.hadoop.get_monitor_data import (
    get_data_in_datanode_monitor,
    get_data_in_namenode_monitor,
    get_data_in_nm_monitor,
    get_data_in_rm_monitor,
)
from apps.hadoop.hadoop_flow import (
    add_datanode_flow,
    add_dir_flow,
    deploy_cluster_flow,
    destroy_cluster_flow,
    input_cluster_flow,
    install_hadoop_cluster_monitor_flow,
    remove_datanode_flow,
)
from apps.hadoop.models import ClusterDetail, ClusterInfo
from apps.hadoop.parameter import (
    retrieval_hadoop_add_dir_param,
    retrieval_hadoop_add_node_param,
    retrieval_hadoop_deploy_param,
    retrieval_hadoop_destroy_param,
    retrieval_hadoop_install_monitor_param,
    retrieval_hadoop_remove_node_param,
)
from apps.hadoop.serializers import HadoopClusterSerializers, HadoopDetailSerializers
from blueapps.utils.logger import logger
from common.utils.common import get_cc_app_id_by_user, machine_statistics, machine_statistics_group_app_id_top_five
from common.utils.custom_auth import CsrfExemptSessionAuthentication
from common.utils.utils import ApiMixin


class HadoopClusterViewSet(ApiMixin, viewsets.ModelViewSet):
    """
       hadoop集群表视图
    """
    serializer_class = HadoopClusterSerializers
    filter_fields = ('cluster_name', 'add_type',)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        """
            重写get_queryset方法，根据用户的业务权限来输出对应记录，用户隔离
        """
        app_id_list = self.request.query_params.get('selectedAppList')
        if not app_id_list:
            app_id_list = get_cc_app_id_by_user()
        else:
            app_id_list = app_id_list.split(',')

        return ClusterInfo.objects.filter(app_id__in=app_id_list).order_by("-create_time")

    @action(methods=['post'], detail=False)
    def create_cluster(self, request, *args, **kwargs):
        """
           POST /hadoop/create_cluster hadoop集群创建
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_hadoop_deploy_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            deploy_parameter = info['data']
            if deploy_cluster_flow(deploy_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "部署任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "部署任务失败"})

            # 部署任务，检测是否正常
        except Exception as e:
            logger.error(f'发布任务出现异常:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def add_node(self, request, *args, **kwargs):
        """
           POST /hadoop/add_node  hadoop集群添加node节点(datanode)
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_hadoop_add_node_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            deploy_parameter = info['data']
            if add_datanode_flow(deploy_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "部署任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "部署任务失败"})

            # 部署任务，检测是否正常
        except Exception as e:
            logger.error(f'发布任务出现异常:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def add_dir(self, request, *args, **kwargs):
        """
           POST /hadoop/add_dir  hadoop集群添加数据目录
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_hadoop_add_dir_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            deploy_parameter = info['data']
            if add_dir_flow(deploy_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "部署任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "部署任务失败"})

            # 部署任务，检测是否正常
        except Exception as e:
            logger.error(f'发布任务出现异常:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def remove_node(self, request, *args, **kwargs):
        """
           POST /hadoop/remove_node   hadoop集群回收node节点(datanode)
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_hadoop_remove_node_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            deploy_parameter = info['data']
            if remove_datanode_flow(deploy_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "部署任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "部署任务失败"})

            # 部署任务，检测是否正常
        except Exception as e:
            logger.error(f'发布任务出现异常:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def input_cluster(self, request, *args, **kwargs):
        """
           POST /hadoop/input_cluster   hadoop集群录入
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_hadoop_deploy_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            deploy_parameter = info['data']
            if input_cluster_flow(deploy_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "部署任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "部署任务失败"})

            # 部署任务，检测是否正常
        except Exception as e:
            logger.error(f'发布任务出现异常:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def destroy_cluster(self, request, *args, **kwargs):
        """
           POST /hadoop/destroy_cluster es集群回收
           集群回收操作只清空后端数据和监控配置，不作进程回收
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_hadoop_destroy_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            destroy_parameter = info['data']
            if destroy_cluster_flow(destroy_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "集群销毁任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "集群销毁任务失败"})

        except Exception as e:
            logger.error(f'create pipeline failed:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def create_monitor(self, request, *args, **kwargs):
        """
            POST /kafka/brokers/create_monitor
            部署集群监控
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_hadoop_install_monitor_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            install_parameter = info['data']
            if install_hadoop_cluster_monitor_flow(install_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "监控部署任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "监控部署任务失败"})

        except Exception as err:
            logger.error(f'创建集群监控失败:{err}')
            return JsonResponse({"result": False, "data": [], "message": f'{err}', "code": 1})

    @action(methods=['post'], detail=False)
    def get_hadoop_monitor_data(self, request, *args, **kwargs):
        """
            POST /kafka/brokers/monitor_data
            根据用户返回过滤条件，查询监控平台的监控数据并汇总到前端
            返回字典格式
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            get_type = post_data.get("get_type")
            if get_type == "NameNode":
                # 根据NameNode维度来获取监控数据
                data_result = get_data_in_namenode_monitor(post_data, bk_username)
            elif get_type == "DataNode":
                # 根据DataNode维度来获取监控数据
                data_result = get_data_in_datanode_monitor(post_data, bk_username)
            elif get_type == "yarn-RM":
                # 根据yarn resource manager维度来获取监控数据
                data_result = get_data_in_rm_monitor(post_data, bk_username)
            elif get_type == "yarn-NM":
                # 根据yarn node manager维度来获取监控数据
                data_result = get_data_in_nm_monitor(post_data, bk_username)
            else:
                logger.warning(f"匹配不到传入的维度，请检测: get_type:{get_type}")
                data_result = {}

            return JsonResponse({"result": True, "code": 0, "data": data_result, "message": "query success"})

        except Exception as err:
            logger.error(f'查询并汇总监控数据失败:{err}')
            return JsonResponse({'result': False, 'code': 1, 'data': {}, 'message': f'查询并汇总监控数据失败:{err}'})


class HadoopDetailViewSet(ApiMixin, viewsets.ModelViewSet):
    """
       hadoop集群节点视图
    """
    queryset = ClusterDetail.objects.all()
    serializer_class = HadoopDetailSerializers
    filter_fields = ('cluster_id', 'hadoop_group_name', 'process_name')
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @action(methods=['post'], detail=False)
    def get_machine_statistics(self, request, *args, **kwargs):
        """
           POST /hadoop/detail/get_machine_statistics 统计hadoop投入已使用的机器数量
        """
        try:
            app_id_list = get_cc_app_id_by_user()
            data_result = machine_statistics(table_set=ClusterDetail, field='process_ip', app_id_list=app_id_list)
            return JsonResponse({"result": True, "code": 0, "data": data_result, "message": "query success"})

        except Exception as err:
            logger.error(f'hadoop机器查询汇总失败:{err}')
            return JsonResponse({'result': False, 'code': 1, 'data': '0', 'message': f'{err}'})

    @action(methods=['post'], detail=False)
    def get_machine_statistics_top_five(self, request, *args, **kwargs):
        """
           POST /hadoop/detail/get_machine_statistics_top_five
           根据用户已有业务权限，查询每个业务的机器投入数量，输出TOP5
        """
        try:
            app_dict = get_cc_app_id_by_user(res="print_name")
            data_result = machine_statistics_group_app_id_top_five(
                table_set=ClusterDetail,
                field='process_ip',
                app_dict=app_dict)

            return JsonResponse({"result": True, "code": 0, "data": data_result, "message": "query success"})

        except Exception as err:
            logger.error(f'查询前5位业务的hadoop机器使用数量汇总失败:{err}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{err}'})
