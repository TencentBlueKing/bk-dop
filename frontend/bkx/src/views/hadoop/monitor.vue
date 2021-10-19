<template>
    <div class="main-grid">
        <div class="wrapper flex">
            <bk-container flex :col="12">
                <bk-row>
                    <bk-col :span="12">
                        <div class="home-card-layout">
                            
                            <span style="font-size: 20px; height :32px; line-height:32px;"><bk-icon type="apps"></bk-icon> {{ cluster_detail.cluster_name }} 集群仪表盘</span>
                            
                            <span class="fr">
                                <bk-date-picker
                                    v-model="timeRange"
                                    :shortcuts="shortcuts"
                                    :type="'datetimerange'"
                                    :shortcut-close="true"
                                    :use-shortcut-text="true"
                                    :clearable="false"
                                    :shortcut-selected-index="2"
                                    @shortcut-change="shortcutChange"
                                    @pick-success="refresh"></bk-date-picker>
                           
                                <bk-button icon="refresh" :hover-theme="'primary'" @click="refresh()"> 刷新</bk-button>
                                <bk-button icon="bar-chart" :hover-theme="'primary'" @click="toPageMonitor()"> 查看原始监控面板</bk-button>
                                <!-- <bk-button theme="primary" icon="plus" :loading="isChecking" @click="beforeSubmit()">监控添加</bk-button> -->
                            </span>
                            
                            <div style="margin-top: 50px">
                                <bk-form form-type="inline">
                                    <bk-form-item label="DataNode节点名称" v-show="active === 'dn_panel'">
                                        <bk-select style="width: 200px"
                                            searchable
                                            display-tag
                                            v-model="selectedDn">
                                            <bk-option v-for="option in nndata.datanode_info"
                                                :key="option.xferaddr"
                                                :id="option.xferaddr"
                                                :name="option.xferaddr">
                                            </bk-option>
                                        </bk-select>
                                    
                                    </bk-form-item>
                                    <bk-form-item label="NodeManager节点名称" v-show="active === 'nm_panel'">
                                        <bk-select style="width: 350px"
                                            searchable
                                            display-tag
                                            v-model="selectedNm">
                                            <bk-option v-for="option in nndata.node_manager_info"
                                                :key="option.host"
                                                :id="option.host"
                                                :name="'[主机名称]: ' + option.host">
                                            </bk-option>
                                        </bk-select>
                                    
                                    </bk-form-item>
                                    <bk-button
                                        :hover-theme="'primary'"
                                        v-show="active === 'dn_panel' || active === 'nm_panel'"
                                        @click="refresh()"> 查询</bk-button>
                                </bk-form>
                                
                            </div>
                        </div>
                    </bk-col>
                </bk-row>
                <bk-row>
                    <bk-col :span="12">
                        <bk-tab :active.sync="active" type="unborder-card" :before-toggle="gettab">
                            <bk-tab-panel
                                v-for="(panel, index) in panels"
                                v-bind="panel"
                                :key="index">
                            </bk-tab-panel>
                        </bk-tab>
                    </bk-col>
                </bk-row>
                <bk-row v-show="active === 'nn_panel'">
                    <bk-col :span="12" v-bkloading="{ isLoading: nnLoading, title: '数据加载中', zIndex: 10 }">
                        <bk-row>
                            <bk-col :span="3">
                     
                                <div class="home-card-layout">
                                    <div class="card-title">总文件数量<p class="fr">{{ nndata.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (nndata.file_count) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="typeof (nndata.file_count) === 'number' "> {{ nndata.file_count }} </div>
                                </div>
                           
                            </bk-col>
                            
                            <bk-col :span="3">
                           
                                <div class="home-card-layout">
                                    <div class="card-title">总数据块数量<p class="fr">{{ nndata.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (nndata.block_count) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="typeof (nndata.block_count) === 'number' "> {{ nndata.block_count }} </div>
                                </div>
                           
                            </bk-col>
                            <bk-col :span="6">
                                <div class="home-card-layout">
                                    <div class="card-title">DataNode状态图<p class="fr">{{ nndata.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (nndata.nodes_mess) === 'undefined'">暂无数据</div>
                                    <div id="dn_state_bar" class="bar-style" v-show="typeof (nndata.nodes_mess) === 'object'"></div>
                                </div>
                            </bk-col>
                           
                        </bk-row>
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">HDFS容量使用情况(单位: GB)<p class="fr">当前HDFS容量最大值: {{ nndata.capacity_total_GB }}GB</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (nndata.capacity_used) === 'undefined'">暂无数据</div>
                                    <div id="capacity_used_bar" class="bar-style" v-show="typeof (nndata.capacity_used) === 'object'"></div>
                                </div>
                            </bk-col>

                        </bk-row>
                        <bk-row>
                            <bk-col :span="6">
                                <div class="home-card-layout">
                                    <div class="card-title">缺失数据块情况(missing_blocks)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (nndata.missing_blocks) === 'undefined'">暂无数据</div>
                                    <div id="missing_blocks_bar" class="bar-style" v-show="typeof (nndata.missing_blocks) === 'object'"></div>
                                </div>
                            </bk-col>
                            <bk-col :span="6">
                                <div class="home-card-layout">
                                    <div class="card-title">损坏数据块情况(corrupt_blocks)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (nndata.corrupt_blocks) === 'undefined'">暂无数据</div>
                                    <div id="cprrupt_blocks_bar" class="bar-style" v-show="typeof (nndata.corrupt_blocks) === 'object'"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                        <bk-row>
                            <bk-col :span="6">
                                <div class="home-card-layout">
                                    <div class="card-title">待删除数据块情况</div>
                                    <div class="no-monitor-data-card" v-show="typeof (nndata.pending_deletion_blocks) === 'undefined'">暂无数据</div>
                                    <div id="pending_deletion_blocks_bar" class="bar-style" v-show="typeof (nndata.pending_deletion_blocks) === 'object'"></div>
                                </div>
                            </bk-col>
                            <bk-col :span="6">
                                <div class="home-card-layout">
                                    <div class="card-title">待复制副本的数据块情况</div>
                                    <div class="no-monitor-data-card" v-show="typeof (nndata.pending_replication_blocks) === 'undefined'">暂无数据</div>
                                    <div id="pending_replication_blocks_bar" class="bar-style" v-show="typeof (nndata.pending_replication_blocks) === 'object'"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                        <bk-row>
                            <bk-col :span="6">
                                <div class="home-card-layout">
                                    <div class="card-title">需要复制副本的数据块情况</div>
                                    <div class="no-monitor-data-card" v-show="typeof (nndata.under_replicated_blocks) === 'undefined'">暂无数据</div>
                                    <div id="under_replicated_blocks_bar" class="bar-style" v-show="typeof (nndata.under_replicated_blocks) === 'object'"></div>
                                </div>
                            </bk-col>
                            <bk-col :span="6">
                                <div class="home-card-layout">
                                    <div class="card-title">HA切换后当前延迟复制的块数情况</div>
                                    <div class="no-monitor-data-card" v-show="typeof (nndata.postponed_misreplicated_blocks) === 'undefined'">暂无数据</div>
                                    <div id="postponed_misreplicated_blocks_bar" class="bar-style" v-show="typeof (nndata.postponed_misreplicated_blocks) === 'object'"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                        
                    </bk-col>
                </bk-row>
                <bk-row v-show="active === 'dn_panel'">
                    <bk-col :span="12" v-bkloading="{ isLoading: dnLoading, title: '数据加载中', zIndex: 10 }">
                        <bk-row>
                            <bk-col :span="4">
                     
                                <div class="home-card-layout">
                                    <div class="card-title">DataNode状态<p class="fr">{{ dndata.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (dndata.state) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="dndata.state === 1 "> 上线中 </div>
                                    <div class="monitor-data-card" v-show="dndata.state === 0 "> 下线中 </div>
                                    <div class="monitor-data-card" v-show="dndata.state > 1 "> 未知状态 </div>
                                </div>
                           
                            </bk-col>
                            
                            <bk-col :span="4">
                           
                                <div class="home-card-layout">
                                    <div class="card-title">DataNode容量<p class="fr">{{ dndata.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (dndata.capacity_GB) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="typeof (dndata.capacity_GB) === 'number' "> {{ dndata.capacity_GB }} GB</div>
                                </div>
                           
                            </bk-col>
                            <bk-col :span="4">
                                <div class="home-card-layout">
                                    <div class="card-title">blocks容量使用百分比<p class="fr">{{ dndata.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (dndata.used_percent) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="typeof (dndata.used_percent) === 'number' "> {{ dndata.used_percent }} % </div>
                                </div>
                            </bk-col>
                           
                        </bk-row>
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">容量使用情况(单位: GB)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (dndata.capacity_used) === 'undefined'">暂无数据</div>
                                    <div id="dn_capacity_used_bar" class="bar-style" v-show="typeof (dndata.capacity_used) === 'object'"></div>
                                </div>
                            </bk-col>

                        </bk-row>
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">DataNode上一次心跳响应时间间隔情况(单位: s)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (dndata.last_contact) === 'undefined'">暂无数据</div>
                                    <div id="dn_last_contact_bar" class="bar-style" v-show="typeof (dndata.last_contact) === 'object'"></div>
                                </div>
                            </bk-col>

                        </bk-row>
                    </bk-col>

                </bk-row>
                <bk-row v-show="active === 'rm_panel'">
                    <bk-col :span="12" v-bkloading="{ isLoading: rmLoading, title: '数据加载中', zIndex: 10 }">
                        <bk-row>
                            <bk-col :span="4">
                     
                                <div class="home-card-layout">
                                    <div class="card-title">总集群内存<p class="fr">{{ rmdata.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (rmdata.total_memory_GB) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="typeof (rmdata.total_memory_GB) === 'number' "> {{ rmdata.total_memory_GB }} GB</div>
                                </div>
                           
                            </bk-col>
                            
                            <bk-col :span="4">
                           
                                <div class="home-card-layout">
                                    <div class="card-title">总虚拟CPU数量<p class="fr">{{ rmdata.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (rmdata.total_virtual_cores) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="typeof (rmdata.total_virtual_cores) === 'number' "> {{ rmdata.total_virtual_cores }} </div>
                                </div>
                           
                            </bk-col>
                            <bk-col :span="4">
                                <div class="home-card-layout">
                                    <div class="card-title">node manager节点数<p class="fr">{{ rmdata.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (rmdata.total_nodes) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="typeof (rmdata.total_nodes) === 'number' "> {{ rmdata.total_nodes }} </div>
                                </div>
                            </bk-col>
                           
                        </bk-row>
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">yarn apps 状态图(单位: 个)<p class="fr">{{ rmdata.last_time }}</p> </div>
                                    <div class="no-monitor-data-card" v-show="typeof (rmdata.apps_state) === 'undefined'">暂无数据</div>
                                    <div id="rm_apps_state_bar" class="bar-style" v-show="typeof (rmdata.apps_state) === 'object'"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                        <bk-row>
                          
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">yarn nodemanager 状态图(单位:个)<p class="fr">{{ rmdata.last_time }}</p> </div>
                                    <div class="no-monitor-data-card" v-show="typeof (rmdata.nodes_state) === 'undefined'">暂无数据</div>
                                    <div id="nm_state_bar" class="bar-style" v-show="typeof (rmdata.nodes_state) === 'object'"></div>
                                </div>
                            </bk-col>

                        </bk-row>
                        <bk-row>
                            <bk-col :span="4">
                                <div class="home-card-layout">
                                    <div class="card-title">yarn containers 已分配数动态情况(单位: 个) </div>
                                    <div class="no-monitor-data-card" v-show="typeof (rmdata.container_allocated) === 'undefined'">暂无数据</div>
                                    <div id="container_allocated_bar" class="bar-style" v-show="typeof (rmdata.container_allocated) === 'object'"></div>
                                </div>
                            </bk-col>
                            <bk-col :span="4">
                                <div class="home-card-layout">
                                    <div class="card-title">yarn containers 预留数动态情况(单位: 个) </div>
                                    <div class="no-monitor-data-card" v-show="typeof (rmdata.container_pending) === 'undefined'">暂无数据</div>
                                    <div id="container_pending_bar" class="bar-style" v-show="typeof (rmdata.container_pending) === 'object'"></div>
                                </div>
                            </bk-col>
                            <bk-col :span="4">
                                <div class="home-card-layout">
                                    <div class="card-title">yarn containers 待处理数动态情况(单位: 个) </div>
                                    <div class="no-monitor-data-card" v-show="typeof (rmdata.container_reserved) === 'undefined'">暂无数据</div>
                                    <div id="container_reserved_bar" class="bar-style" v-show="typeof (rmdata.container_reserved) === 'object'"></div>
                                </div>
                            </bk-col>

                        </bk-row>
                        <bk-row>
                            <bk-col :span="4">
                                <div class="home-card-layout">
                                    <div class="card-title">yarn 内存已分配容量动态情况(单位:MB) </div>
                                    <div class="no-monitor-data-card" v-show="typeof (rmdata.allocated_mb) === 'undefined'">暂无数据</div>
                                    <div id="yarn_allocated_mb_bar" class="bar-style" v-show="typeof (rmdata.allocated_mb) === 'object'"></div>
                                </div>
                            </bk-col>
                            <bk-col :span="4">
                                <div class="home-card-layout">
                                    <div class="card-title">yarn 内存可用容量动态情况(单位:MB) </div>
                                    <div class="no-monitor-data-card" v-show="typeof (rmdata.available_mb) === 'undefined'">暂无数据</div>
                                    <div id="yarn_available_mb_bar" class="bar-style" v-show="typeof (rmdata.available_mb) === 'object'"></div>
                                </div>
                            </bk-col>
                            <bk-col :span="4">
                                <div class="home-card-layout">
                                    <div class="card-title">yarn 内存已预留容量动态情况(单位:MB) </div>
                                    <div class="no-monitor-data-card" v-show="typeof (rmdata.reserved_mb) === 'undefined'">暂无数据</div>
                                    <div id="yarn_reserved_mb_bar" class="bar-style" v-show="typeof (rmdata.reserved_mb) === 'object'"></div>
                                </div>
                            </bk-col>

                        </bk-row>

                    </bk-col>
                    
                </bk-row>
                <bk-row v-show="active === 'nm_panel'">
                    <bk-col :span="12" v-bkloading="{ isLoading: nmLoading, title: '数据加载中', zIndex: 10 }">
                        <bk-row>
                            <bk-col :span="4">
                     
                                <div class="home-card-layout">
                                    <div class="card-title">node manager 状态<p class="fr">{{ nmdata.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (nmdata.state) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="nmdata.state === 1 ">新加入中</div>
                                    <div class="monitor-data-card" v-show="nmdata.state === 2 ">运行中</div>
                                    <div class="abnormal-data-card" v-show="nmdata.state === 3 ">不健康</div>
                                    <div class="abnormal-data-card" v-show="nmdata.state === 4 ">已退役</div>
                                    <div class="abnormal-data-card" v-show="nmdata.state === 5 ">失联中</div>
                                    <div class="abnormal-data-card" v-show="nmdata.state === 6 ">重启中</div>
                                    <div class="abnormal-data-card" v-show="nmdata.state > 6 ">未知状态</div>
                                </div>
                           
                            </bk-col>
                            
                            <bk-col :span="8">
                           
                                <div class="home-card-layout">
                                    <div class="card-title">NM containers 数量动态情况(单位: 个)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (nmdata.nm_containers_num) === 'undefined'">暂无数据</div>
                                    <div id="nm_containers_num_bar" class="bar-style" v-show="typeof (nmdata.nm_containers_num) === 'object'"></div>
                                </div>
                           
                            </bk-col>
                           
                        </bk-row>
                        <bk-row>
                            <bk-col :span="6">
                           
                                <div class="home-card-layout">
                                    <div class="card-title">NM 已分配CPU资源动态情况(单位: 个)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (nmdata.nm_used_virtual_cores) === 'undefined'">暂无数据</div>
                                    <div id="nm_used_virtual_cores_bar" class="bar-style" v-show="typeof (nmdata.nm_used_virtual_cores) === 'object'"></div>
                                </div>
                           
                            </bk-col>
                            <bk-col :span="6">
                           
                                <div class="home-card-layout">
                                    <div class="card-title">NM 未分配CPU资源动态情况(单位: 个)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (nmdata.nm_available_virtual_cores) === 'undefined'">暂无数据</div>
                                    <div id="nm_available_virtual_cores_bar" class="bar-style" v-show="typeof (nmdata.nm_available_virtual_cores) === 'object'"></div>
                                </div>
                           
                            </bk-col>

                        </bk-row>
                        <bk-row>
                            <bk-col :span="6">
                           
                                <div class="home-card-layout">
                                    <div class="card-title">NM 已分配内存资源动态情况(单位: MB)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (nmdata.nm_used_memory_mb) === 'undefined'">暂无数据</div>
                                    <div id="nm_used_memory_mb_bar" class="bar-style" v-show="typeof (nmdata.nm_used_memory_mb) === 'object'"></div>
                                </div>
                           
                            </bk-col>
                            <bk-col :span="6">
                           
                                <div class="home-card-layout">
                                    <div class="card-title">NM 未分配内存资源动态情况(单位: MB)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (nmdata.nm_avail_memory_mb) === 'undefined'">暂无数据</div>
                                    <div id="nm_avail_memory_mb_bar" class="bar-style" v-show="typeof (nmdata.nm_avail_memory_mb) === 'object'"></div>
                                </div>
                           
                            </bk-col>

                        </bk-row>

                    </bk-col>
                </bk-row>
            </bk-container>
        </div>
    </div>
</template>
<script>
    import * as echarts from 'echarts'
    import elementResize from 'element-resize-detector'
    // import { formatDate } from '@/common/dateformat.js'
    export default {
      
        data () {
            return {
                cluster_detail: {},
                confirmFnTip: false,
                isChecking: false,
                nnLoading: true,
                dnLoading: true,
                rmLoading: true,
                nmLoading: false,
                dnStateChart: null,
                nnCapacityUsedChart: null,
                missingBlocksChart: null,
                corruptBlocksChart: null,
                pendingDeletionBlocksChart: null,
                pendingReplicationBlocksChart: null,
                underReplicatedBlocksChart: null,
                postponedMisReplicatedBlocksChart: null,
                dnCapacityUsedChart: null,
                dnLastContactChart: null,
                rmAppsStateChart: null,
                nmStateChart: null,
                containerAllocatedChart: null,
                containerPendingChart: null,
                containerReservedChart: null,
                yarnMbAllocatedChart: null,
                yarnMbAvailableChart: null,
                yarnMbReservedChart: null,
                nmContainersSumChart: null,
                nmUsedVcoreChart: null,
                nmAvailVcoreChart: null,
                nmUsedMemChart: null,
                nmAvailMemChart: null,

                panels: [
                    { name: 'nn_panel', label: 'NameNode面板' },
                    { name: 'dn_panel', label: 'DataNode面板' },
                    { name: 'rm_panel', label: 'Yran-RM面板' },
                    { name: 'nm_panel', label: 'Yarn-NM面板' }
                ],
                active: 'nn_panel',
                currentPosition: 'top',
                timeRange: [],
                timeRangeTimestamp: [],
                shortcuts: [
                    {
                        text: '近5分钟',
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 60 * 5 * 1000)
                            return [start, end]
                        }
                    },
                    {
                        text: '近10分钟',
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 60 * 10 * 1000)
                            return [start, end]
                        }
                    },
                    {
                        text: '近30分钟',
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 60 * 30 * 1000)
                            return [start, end]
                        }
                    },
                    {
                        text: '近1小时',
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 1000)
                            return [start, end]
                        }
                    },
                    {
                        text: '近6小时',
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 6 * 1000)
                            return [start, end]
                        }
                    },
                    {
                        text: '近12小时',
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 12 * 1000)
                            return [start, end]
                        }
                    },
                    {
                        text: '进24小时',
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 24 * 1000)
                            return [start, end]
                        }
 
                    },
                    {
                        text: '近7天',
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
                            return [start, end]
                        }
                    },
                    {
                        text: '近15天',
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 15)
                            return [start, end]
                        }
                    },
                    {
                        text: '近30天',
                        value () {
                            const end = new Date()
                            const start = new Date()
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
                            return [start, end]
                        }
                    }
                    
                ],
                shortcutsIndex: {},
                nndata: {},
                dndata: {},
                rmdata: {},
                nmdata: {},
                selectedDn: '',
                selectedNm: '',
                pie_sample: {
                    tooltip: {
                        trigger: 'item',
                        textStyle: {
                            fontSize: 10
                        }
                    },
                  
                    series: [
                        {
                            name: '容量(单位: MB)',
                            type: 'pie',
                            avoidLabelOverlap: false,
                            itemStyle: {
                                borderRadius: 10,
                                borderColor: '#fff',
                                borderWidth: 2
                            },
                            emphasis: {
                                label: {
                                    show: true,
                                    fontSize: '15',
                                    fontWeight: 'normal'
                                    
                                }
                            },
                            labelLine: {
                                show: true
                            },
                            data: []
                        }
                    ]
                },
                category_sample: {
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross',
                            label: {
                                backgroundColor: '#6a7985'
                            }
                        }
                    },
                    dataset: {
                        dimensions: [],
                        source: []
                    },
                    grid: {
                        top: '5%',
                        left: '3%',
                        right: '3%',
                        bottom: '5%',
                        containLabel: true
                    },
                    
                    xAxis: [
                        {
                            type: 'category',
                            boundaryGap: false,
                            axisTick: {
                                alignWithLabel: false
                            }
                            
                        }
                    ],
                    yAxis: [
                        {
                            type: 'value'
                        }
                    ],
                    series: []
                }

            }
        },
        watch: {
            
            'timeRange': function (val) {
                this.timeRangeTimestamp[0] = val[0].getTime()
                this.timeRangeTimestamp[1] = val[1].getTime()
            }
        },

        beforeRouteLeave (to, from, next) {
            if (to.name !== 'hadoopdetail') {
                localStorage.removeItem('hadoop_condition')
            }
            
            next()
        },
        mounted () {
            const condition = localStorage.getItem('hadoop_condition')
            if (condition != null) {
                this.cluster_detail = JSON.parse(condition)
                this.iscreatedMonitor()
            } else {
                this.cluster_detail = this.$route.query.row
                if (typeof (this.cluster_detail) === 'object' && this.cluster_detail.cluster_name !== '') {
                    localStorage.setItem('hadoop_condition', JSON.stringify(this.cluster_detail))
                    this.iscreatedMonitor()
                } else {
                    // 非法请求提示后跳转到info界面
                    this.$bkMessage({
                        message: '检测不到传入的集群名称，非法请求! 1秒后跳转到hadoop集群管理界面',
                        theme: 'error'
                    })
                    setTimeout(() => {
                        this.$router.push(
                            {
                                name: 'hadoopinfo'
                            }
                        )
                    }, 1000)
                }
            }
        },
        methods: {
            iscreatedMonitor () {
                //  如果集群已经部署监控，则默认查询近30分钟数据
                if (this.cluster_detail.bk_data_id !== 0) {
                    const end = new Date().getTime()
                    const start = new Date().getTime() - 60 * 30 * 1000
                    this.timeRangeTimestamp = [start, end]
                    this.shortcutsIndex = this.shortcuts[2]
                    this.getNNMonitorData()
                } else {
                    // 如果检测集群尚未添加监控，则需要弹出提示框提示用户先添加监控才能查看数据
                    this.beforeSubmit()
                }
            },
            toPageMonitor () {
                const url = window.PROJECT_CONFIG.BKPAAS_URL + 'o/bk_monitorv3/?bizId=' + this.cluster_detail.app_id + '#/custom-escalation-view/' + this.cluster_detail.bk_group_id
                window.open(url)
            },
            closeDialog () {
                this.$router.push(
                    {
                        name: 'hadooprecord'
                    }
                )
            },
            getClusterDetail () {
                this.$router.push(
                    {
                        name: 'hadoopdetail', query: { 'row': this.cluster_detail }
                    }
                )
            },

            beforeSubmit () {
                this.isChecking = true
                this.$bkInfo({
                    width: 600,
                    type: 'warning',
                    closeIcon: false,
                    title: '检测到尚未部署监控！是否提交创建集群监控任务？',
                    subTitle: '待创建集群名称：' + this.cluster_detail.cluster_name,
                    okText: '添加监控',
                    cancelText: '返回上一级页面',
                    confirmLoading: true,
                    confirmFn: async () => {
                        this.confirmFnTip = true
                        const param = {
                            'cluster_name': this.cluster_detail.cluster_name
                        }
                        try {
                            const res = await this.$store.dispatch('hadoop/createHadoopMonitor', param)
                            if (res.code === 0) {
                                const config = { theme: 'success' }
                                config.message = '提交成功, 跳转到hadoop执行记录中查看部署详情！'
                                config.offsetY = 80
                                this.$bkMessage(config)
                                this.closeDialog()
                            } else {
                                const config = { theme: 'error' }
                                config.message = res.message
                                config.offsetY = 80
                                this.$bkMessage(config)
                            }
                        } catch (err) {
                            this.$bkMessage({
                                message: err.message ? err.message : err,
                                theme: 'error'
                            })
                        }
                    },
                    afterLeaveFn: () => {
                        if (this.confirmFnTip === false) {
                            this.getClusterDetail()
                        }
                    }
                })
            },
      
            shortcutChange (index) {
                // 当快捷项发送变更，则同步到shortcutsIndex
                this.shortcutsIndex = index
            },
            gettab (panelName) {
                // 当前端切换tab时，进行一次查询数据
                this.active = panelName
                this.refresh()
                return true
            },
            refresh () {
                // 刷新当前快捷项的当前时间范围,并且拿最新数据查询数据（静态数据无需刷新时间）
                if (this.shortcutsIndex) {
                    this.timeRange = this.shortcutsIndex.value()
                }
                if (this.active === 'nn_panel') {
                    this.nnLoading = true
                    this.getNNMonitorData()
                } else if (this.active === 'dn_panel') {
                    this.dnLoading = true
                    if (this.selectedDn !== '') {
                        this.getDNMonitorData()
                    } else {
                        this.dnLoading = false
                    }
                } else if (this.active === 'rm_panel') {
                    this.rmLoading = true
                    this.getRMMonitorData()
                } else if (this.active === 'nm_panel') {
                    this.nmLoading = true
                    if (this.selectedNm !== '') {
                        this.getNMMonitorData()
                    } else {
                        this.nmLoading = false
                    }
                } else {
                    console.log('tab error')
                }
            },
           
            PieChart (chart, divId, xdata) {
                // 适配饼状态图例子
                const Data = this.pie_sample
                Data.series[0].data = xdata
                const object = document.getElementById(divId)

                chart = echarts.init(object)
                chart.setOption(Data)
                const Resize = elementResize({
                    strategy: 'scroll', // <- 推荐监听滚动，提升性能
                    callOnAdd: true // 添加侦听器时是否应调用,默认true
                })
                Resize.listenTo(object, function (element) {
                    echarts.init(object).resize() // 当元素尺寸发生改变是会触发此事件，刷新图表
                })
            },
            
            categoryChart (chart, divId, dimensions, data, isMuti, chartType) {
                // 适配单线图和多线图的初始化
                const Data = this.category_sample
                Data.dataset.dimensions = dimensions
                Data.dataset.source = data
                Data.series = []
                if (isMuti === false) {
                    this.$set(Data, 'color', ['rgb(86, 166, 75)']) // 单线图统一使用绿色
                } else {
                    this.$delete(Data, 'color') // 多线图随机颜色
                }
                if (chartType === 'bar') {
                    Data.xAxis[0].boundaryGap = true
                    Data.xAxis[0].axisTick.alignWithLabel = false
                } else if (chartType === 'line') {
                    Data.xAxis[0].boundaryGap = false
                    Data.xAxis[0].axisTick.alignWithLabel = false
                }
                for (const i in dimensions) {
                    if (i !== '0') {
                        Data.series.push(
                            {
                                name: dimensions[i],
                                type: chartType,
                                stack: '总量',
                                areaStyle: {}
                            }
                        )
                    }
                }
                
                const object = document.getElementById(divId)
                chart = echarts.init(object)
                chart.setOption(Data)
                const Resize = elementResize({
                    strategy: 'scroll', // <- 推荐监听滚动，提升性能
                    callOnAdd: true // 添加侦听器时是否应调用,默认true
                })
                Resize.listenTo(object, function (element) {
                    echarts.init(object).resize() // 当元素尺寸发生改变是会触发此事件，刷新图表
                })
            },

            async getNNMonitorData () {
                const param = {
                    'app_id': this.cluster_detail.app_id,
                    'get_type': 'NameNode',
                    'bk_data_id': this.cluster_detail.bk_data_id,
                    'access_token': this.cluster_detail.access_token,
                    'time_range': this.timeRangeTimestamp }
                try {
                    const res = await this.$store.dispatch('hadoop/getMonitorData', param)
                    if (res.result) {
                        this.nndata = res.data
                        this.categoryChart(this.dnStateChart, 'dn_state_bar', res.data.nodes_mess_dimensions, res.data.nodes_mess, false, 'bar')
                        this.categoryChart(this.nnCapacityUsedChart, 'capacity_used_bar', res.data.capacity_used_dimensions, res.data.capacity_used, true, 'line')
                        this.categoryChart(this.missingBlocksChart, 'missing_blocks_bar', res.data.common_dimensions, res.data.missing_blocks, false, 'line')
                        this.categoryChart(this.corruptBlocksChart, 'cprrupt_blocks_bar', res.data.common_dimensions, res.data.corrupt_blocks, false, 'line')
                        this.categoryChart(this.pendingDeletionBlocksChart, 'pending_deletion_blocks_bar', res.data.common_dimensions, res.data.pending_deletion_blocks, false, 'line')
                        this.categoryChart(this.pendingReplicationBlocksChart, 'pending_replication_blocks_bar', res.data.common_dimensions, res.data.pending_replication_blocks, false, 'line')
                        this.categoryChart(this.underReplicatedBlocksChart, 'under_replicated_blocks_bar', res.data.common_dimensions, res.data.under_replicated_blocks, false, 'line')
                        this.categoryChart(this.postponedMisReplicatedBlocksChart, 'postponed_misreplicated_blocks_bar', res.data.common_dimensions, res.data.postponed_misreplicated_blocks, false, 'line')
                    } else {
                        const config = { theme: 'error' }
                        config.message = res.message
                        config.offsetY = 80
                        this.$bkMessage(config)
                    }

                    this.nnLoading = false
                } catch (e) {
                    console.error(e)
                    
                    this.nnLoading = false
                }
            },
            async getDNMonitorData () {
                const param = {
                    'app_id': this.cluster_detail.app_id,
                    'get_type': 'DataNode',
                    'bk_data_id': this.cluster_detail.bk_data_id,
                    'access_token': this.cluster_detail.access_token,
                    'time_range': this.timeRangeTimestamp,
                    'selected_datanode': this.selectedDn }
                try {
                    const dnres = await this.$store.dispatch('hadoop/getMonitorData', param)
                    if (dnres.result) {
                        this.dndata = dnres.data
                        this.categoryChart(this.dnCapacityUsedChart, 'dn_capacity_used_bar', dnres.data.capacity_used_dimensions, dnres.data.capacity_used, true, 'line')
                        this.categoryChart(this.dnLastContactChart, 'dn_last_contact_bar', dnres.data.common_dimensions, dnres.data.last_contact, false, 'line')
                    } else {
                        const config = { theme: 'error' }
                        config.message = dnres.message
                        config.offsetY = 80
                        this.$bkMessage(config)
                    }

                    this.dnLoading = false
                } catch (e) {
                    console.error(e)
                    
                    this.dnLoading = false
                }
            },
            async getRMMonitorData () {
                const param = {
                    'app_id': this.cluster_detail.app_id,
                    'get_type': 'yarn-RM',
                    'bk_data_id': this.cluster_detail.bk_data_id,
                    'access_token': this.cluster_detail.access_token,
                    'time_range': this.timeRangeTimestamp }
                try {
                    const rmres = await this.$store.dispatch('hadoop/getMonitorData', param)
                    if (rmres.result) {
                        this.rmdata = rmres.data
                        this.categoryChart(this.rmAppsStateChart, 'rm_apps_state_bar', rmres.data.nodes_state_dimensions, rmres.data.apps_state, false, 'bar')
                        this.categoryChart(this.nmStateChart, 'nm_state_bar', rmres.data.nodes_state_dimensions, rmres.data.nodes_state, false, 'bar')
                        this.categoryChart(this.containerAllocatedChart, 'container_allocated_bar', rmres.data.common_dimensions, rmres.data.container_allocated, false, 'line')
                        this.categoryChart(this.containerPendingChart, 'container_pending_bar', rmres.data.common_dimensions, rmres.data.container_pending, false, 'line')
                        this.categoryChart(this.containerReservedChart, 'container_reserved_bar', rmres.data.common_dimensions, rmres.data.container_reserved, false, 'line')
                        this.categoryChart(this.yarnMbAllocatedChart, 'yarn_allocated_mb_bar', rmres.data.common_dimensions, rmres.data.allocated_mb, false, 'line')
                        this.categoryChart(this.yarnMbAvailableChart, 'yarn_available_mb_bar', rmres.data.common_dimensions, rmres.data.available_mb, false, 'line')
                        this.categoryChart(this.yarnMbReservedChart, 'yarn_reserved_mb_bar', rmres.data.common_dimensions, rmres.data.reserved_mb, false, 'line')
                    } else {
                        const config = { theme: 'error' }
                        config.message = rmres.message
                        config.offsetY = 80
                        this.$bkMessage(config)
                    }

                    this.rmLoading = false
                } catch (e) {
                    console.error(e)
                    
                    this.rmLoading = false
                }
            },
            async getNMMonitorData () {
                const param = {
                    'app_id': this.cluster_detail.app_id,
                    'get_type': 'yarn-NM',
                    'bk_data_id': this.cluster_detail.bk_data_id,
                    'access_token': this.cluster_detail.access_token,
                    'time_range': this.timeRangeTimestamp,
                    'selected_nm': this.selectedNm }
                try {
                    const nmres = await this.$store.dispatch('hadoop/getMonitorData', param)
                    if (nmres.result) {
                        this.nmdata = nmres.data
                        this.categoryChart(this.nmContainersSumChart, 'nm_containers_num_bar', nmres.data.common_dimensions, nmres.data.nm_containers_num, false, 'line')
                        this.categoryChart(this.nmUsedVcoreChart, 'nm_used_virtual_cores_bar', nmres.data.common_dimensions, nmres.data.nm_used_virtual_cores, false, 'line')
                        this.categoryChart(this.nmAvailVcoreChart, 'nm_available_virtual_cores_bar', nmres.data.common_dimensions, nmres.data.nm_available_virtual_cores, false, 'line')
                        this.categoryChart(this.nmUsedMemChart, 'nm_used_memory_mb_bar', nmres.data.common_dimensions, nmres.data.nm_used_memory_mb, false, 'line')
                        this.categoryChart(this.nmAvailMemChart, 'nm_avail_memory_mb_bar', nmres.data.common_dimensions, nmres.data.nm_avail_memory_mb, false, 'line')
                    } else {
                        const config = { theme: 'error' }
                        config.message = nmres.message
                        config.offsetY = 80
                        this.$bkMessage(config)
                    }

                    this.nmLoading = false
                } catch (e) {
                    console.error(e)
                    
                    this.nmLoading = false
                }
            }
        }
        
    }
</script>
<style lang="postcss">
    .home-card-layout {
        
        height: 100%;
        width: 100%;
        padding: 18px 20px;
        background: #fff;
        color: #63656e;
        -webkit-box-shadow: 0 1px 2px 0 rgb(0 0 0 / 10%);
        box-shadow: 0 1px 2px 0 rgb(0 0 0 / 10%);
        border-radius: 2px;
        
        .table-box {
            width: 100%;
            height: 220px;

        }
        .card-title {
                  margin-bottom: 20px;
                  font-size: 14px;
                  font-weight: 700;
                  line-height: 1;
                  color: #313238;
                  p {
                       margin-right: auto;
                       font-size: 8px;
                       color: #979ba5;
                     }
                  }
        .no-monitor-data-card{
            color:rgb(86, 166, 75);
            font-size: 45px;
            height: 220px;
            width: 100%;
            text-align: center;
            line-height:220px
        }
        .monitor-data-card{
            color:rgb(86, 166, 75);
            font-size: 45px;
            height: 220px;
            width: 100%;
            text-align: center;
            line-height:220px
        }
        .abnormal-data-card{
            color:rgb(245, 108, 108);
            font-size: 100px;
            height: 220px;
            width: 100%;
            text-align: center;
            line-height:220px
        }
        .swiper-boby {
             font-size: 12px;
             margin-top: 50px;
             height: 180px;
             margin-right: auto;
             margin-left: auto;

             .swiper-content{
                height: 100%;
                width: 100%;
                white-space: pre-wrap;
                text-align: left;
                line-height: 30px;
             }
        }
        .bar-style {
            width: 100%;
            height: 250px;
            margin-right: auto;
            margin-left: auto;
           }
        .no-data-bar{
            font-size: 25px;
            height: 250px;
            width: 100%;
            text-align: center;
            line-height:250px
        }
        .echart_style {
            width:100%;
            height:220px;
            margin-right: auto;
            margin-left: auto;
    }
      
    }

    .main-grid {
        .wrapper {
            overflow: hidden;
            /* border: 1px solid #ddd; */
            border-radius: 2px;
            padding: 20px 0;
        }
        .bk-grid-row {
        }

        .bk-grid-row + .bk-grid-row {
            margin-top: 30px;
        }

        .flex {
            .bk-grid-row + .bk-grid-row {
                margin-top: 20px;
            }
        }
        
    }
    .work-statistics-box {
        -webkit-box-orient: vertical;
        -webkit-box-direction: normal;
        -ms-flex-direction: column;
        flex-direction: column;
        -webkit-box-align: center;
        -ms-flex-align: center;
        align-items: center;
        padding-top: 18px;
        text-align: center;
        cursor: pointer;
        .work-flag {
            position: relative;
            width: 100px;
            height: 60px;
            margin-bottom: 15px;
            margin-left: auto;
            margin-right: auto;
        }
        .work-total {
            font-size: 24px;
            color: #313238;
            font-weight: 700;
        }
        .work-name {
            margin-top: 2px;
            color: #979ba5;
        }
    
    }

</style>
