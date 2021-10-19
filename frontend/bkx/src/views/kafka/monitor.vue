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
                                    <bk-form-item label="topic名称" v-show="active === 'topic_panel' || active === 'consumer_group_panel'">
                                        <bk-select style="width: 200px"
                                            searchable
                                            display-tag
                                            v-model="selectedTopic">
                                            <bk-option v-for="option in cluster_data.topic_info"
                                                :key="option.topic_name"
                                                :id="option.topic_name"
                                                :name="option.topic_name">
                                            </bk-option>
                                        </bk-select>
                                    
                                    </bk-form-item>
                                    <bk-form-item label="消费组名称" v-show="active === 'consumer_group_panel'">
                                        <bk-select style="width: 200px"
                                            searchable
                                            display-tag
                                            v-model="selectedGroupId">
                                            <bk-option v-for="option in cluster_data.consumer_group_info"
                                                :key="option.group_id"
                                                :id="option.group_id"
                                                :name="option.group_id">
                                            </bk-option>
                                        </bk-select>
                                    
                                    </bk-form-item>
                                    <bk-button
                                        :hover-theme="'primary'"
                                        v-show="active === 'topic_panel' || active === 'consumer_group_panel'"
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
                <bk-row v-show="active === 'cluster_panel'">
                    <bk-col :span="12" v-bkloading="{ isLoading: clusterLoading, title: '数据加载中', zIndex: 10 }">
                        <bk-row>
                            <bk-col :span="3">
                                <bk-row>
                                    <bk-col :span="3">
                                        <div class="home-card-layout">
                                            <div class="card-title">broker online数量<p class="fr">{{ cluster_data.last_time }}</p></div>
                                            <div class="no-monitor-data-card" style="height: 90px; line-height:90px" v-show="typeof (cluster_data.online_broker_count) === 'undefined'">暂无数据</div>
                                            <div class="abnormal-data-card" style="height: 90px; line-height:90px " v-show="cluster_data.online_broker_count === 0">{{ cluster_data.online_broker_count }}</div>
                                            <div class="monitor-data-card" style="height: 90px; line-height:90px" v-show="cluster_data.online_broker_count > 0 ">{{ cluster_data.online_broker_count }}</div>
                                    
                                        </div>
                                    </bk-col>
                                </bk-row>
                                <bk-row>
                                    <bk-col :span="3">
                                        <div class="home-card-layout">
                                            <div class="card-title">消费组数量<p class="fr">{{ cluster_data.last_time }}</p></div>
                                            <div class="no-monitor-data-card" style="height: 90px; line-height:90px" v-show="typeof (cluster_data.consumer_group_length) === 'undefined'">暂无数据</div>
                                            <div class="monitor-data-card" style="height: 90px; line-height:90px" v-show="typeof (cluster_data.consumer_group_length) === 'number'">{{cluster_data.consumer_group_length }}</div>
                                    
                                        </div>
                                    </bk-col>
                                </bk-row>
                            </bk-col>
                            
                            <bk-col :span="3">
                                <bk-row>
                                    <bk-col :span="3">
                                        <div class="home-card-layout">
                                            <div class="card-title">集群版本<p class="fr">{{ cluster_data.last_time }}</p></div>
                                            <div class="no-monitor-data-card" style="height: 90px; line-height:90px" v-show="typeof (cluster_data.cluster_version) === 'undefined'">暂无数据</div>
                                            <div class="monitor-data-card" style="height: 90px; line-height:90px" v-show="typeof (cluster_data.cluster_version) === 'string'">{{ cluster_data.cluster_version }}</div>
                                    
                                        </div>
                                    </bk-col>
                                </bk-row>
                                <bk-row>
                                    <bk-col :span="3">
                                        <div class="home-card-layout">
                                            <div class="card-title">topic数量<p class="fr">{{ cluster_data.last_time }}</p></div>
                                            <div class="no-monitor-data-card" style="height: 90px; line-height:90px" v-show="typeof (cluster_data.topic_length) === 'undefined'">暂无数据</div>
                                            <div class="monitor-data-card" style="height: 90px; line-height:90px" v-show="typeof (cluster_data.topic_length) === 'number'">{{ cluster_data.topic_length }}</div>
                                    
                                        </div>
                                    </bk-col>
                                </bk-row>
                            </bk-col>
                            <bk-col :span="6">
                                <div class="home-card-layout">
                                    <div class="card-title">broker状态信息<p class="fr">{{ cluster_data.last_time }}</p></div>
                           
                                    <div class="table-box" style="overflow:auto">
                                       
                                        <bk-table
                                            :data="brokerData"
                                            :size="'small'"
                                            :outer-border="false"
                                            :header-border="false"
                                            :header-cell-style="{ background: '#fff' }">
                                            <bk-table-column type="index" label="序列" width="100"></bk-table-column>
                                            <bk-table-column label="broker address" prop="address"></bk-table-column>
                                            <bk-table-column label="broker port" prop="port"></bk-table-column>
                                            <bk-table-column label="broker id " prop="broker_id"></bk-table-column>
                                            <bk-table-column label="is_controller" prop="is_controller"></bk-table-column>
                                        </bk-table>
                                         
                                    </div>
                                </div>
                            </bk-col>
                           
                        </bk-row>
                        <bk-row>
                            <bk-col :span="6">
                                <div class="home-card-layout">
                                    <div class="card-title">broker日志容量对比<p class="fr">{{ cluster_data.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (cluster_data.log_size_info) === 'undefined' ">暂无数据</div>
                                    <div id="log_data_size" class="bar-style" v-show="typeof (cluster_data.topic_info) === 'object'"></div>
                                </div>
                            </bk-col>
                            <bk-col :span="6">
                                <div class="home-card-layout">
                                    <div class="card-title">每分钟产生message</div>
                                    <div class="no-monitor-data-card" v-show="typeof (cluster_data.message_in_rate) === 'undefined'">暂无数据</div>
                                    <div id="message_in_per_mins" class="bar-style" v-show="typeof (cluster_data.message_in_rate) === 'object'"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">每分钟集群sent请求数 单位(次数/min)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (cluster_data.requests_sent_rate) === 'undefined'">暂无数据</div>
                                    <div id="requests_sent_per_mins" class="bar-style" v-show="typeof (cluster_data.requests_sent_rate) === 'object'"></div>
                                </div>
                            </bk-col>
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">每分钟集群received请求数 单位(次数/min)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (cluster_data.requests_received_rate) === 'undefined'">暂无数据</div>
                                    <div id="requests_received_per_mins" class="bar-style" v-show="typeof (cluster_data.requests_received_rate) === 'object'"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">每分钟集群out流量 单位(KB/min)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (cluster_data.sent_bytes_rate) === 'undefined'">暂无数据</div>
                                    <div id="sent_bytes_per_mins" class="bar-style" v-show="typeof (cluster_data.sent_bytes_rate) === 'object'"></div>
                                </div>
                            </bk-col>
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">每分钟集群in流量 单位(KB/min)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (cluster_data.received_bytes_rate) === 'undefined'">暂无数据</div>
                                    <div id="received_bytes_per_mins" class="bar-style" v-show="typeof (cluster_data.received_bytes_rate) === 'object'"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                    </bk-col>
                    
                </bk-row>
                <bk-row v-show="active === 'topic_panel'">
                    <bk-col :span="12" v-bkloading="{ isLoading: topicLoading, title: '数据加载中', zIndex: 10 }">
                    
                        <bk-row>
                          
                            <bk-col :span="3">
                                <div class="home-card-layout">
                                    <div class="card-title">cleanup policy<p class="fr">{{ topic_data.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (topic_data.cleanup_policy) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" style="font-size: 45px;" v-show="typeof (topic_data.cleanup_policy) === 'string'">{{ topic_data.cleanup_policy }}</div>

                                </div>
                            </bk-col>

                            <bk-col :span="3">
                                <bk-row>
                                    <bk-col :span="3">
                                        <div class="home-card-layout">
                                            <div class="card-title">partition 数量<p class="fr">{{ topic_data.last_time }}</p></div>
                                            <div class="no-monitor-data-card" style="height: 90px; line-height:90px" v-show=" typeof (topic_data.partition_count) === 'undefined'">暂无数据</div>
                                            <div class="monitor-data-card" style="height: 90px; line-height:90px" v-show=" typeof (topic_data.partition_count) === 'number'">{{ topic_data.partition_count }}</div>
                                    
                                        </div>
                                    </bk-col>
                                </bk-row>
                                <bk-row>
                                    <bk-col :span="3">
                                        <div class="home-card-layout">
                                            <div class="card-title">replication_foctor 数量<p class="fr">{{ topic_data.last_time }}</p></div>
                                            <div class="no-monitor-data-card" style="height: 90px; line-height:90px" v-show="typeof (topic_data.replication_factor) === 'undefined'">暂无数据</div>
                                            <div class="monitor-data-card" style="height: 90px; line-height:90px" v-show="typeof (topic_data.replication_factor) === 'number'">{{ topic_data.replication_factor }}</div>
                                    
                                        </div>
                                    </bk-col>
                                </bk-row>
                            </bk-col>
                            <bk-col :span="6">
                                <div class="home-card-layout">
                                    <div class="card-title">Topic 消息写入增长情况(单位：消息数/每分钟)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (topic_data.topic_message_in_rate) === 'undefined'">暂无数据</div>
                                    <div id="topic_message_in" class="bar-style" v-show="typeof (topic_data.topic_message_in_rate) === 'object'"></div>
                                </div>
                            </bk-col>
                           
                        </bk-row>
                        
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">topic 容量使用情况(单位: MB)</div>
                                    <div class="no-monitor-data-card" v-show="typeof (topic_data.topic_log_size) === 'undefined'">暂无数据</div>
                                    <div id="topic_log_size" class="bar-style" v-show="typeof (topic_data.topic_log_size) === 'object'"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                        
                    </bk-col>
                    
                </bk-row>
                <bk-row v-show="active === 'consumer_group_panel'">
                  
                    <bk-col :span="12" v-bkloading="{ isLoading: consumerGroupLoading, title: '数据加载中', zIndex: 10 }">
                        <bk-row>
                            <bk-col :span="3">
                                <div class="home-card-layout">
                                    <div class="card-title">消费者数量<p class="fr">{{ consumer_group_data.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (consumer_group_data.member_count) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="typeof (consumer_group_data.member_count) === 'number'">{{ consumer_group_data.member_count }}</div>

                                </div>
                            </bk-col>
                            <bk-col :span="3">
                                <div class="home-card-layout">
                                    <div class="card-title">当前状态<p class="fr">{{ consumer_group_data.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (consumer_group_data.state) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="typeof (consumer_group_data.state) === 'string'">{{ consumer_group_data.state }}</div>

                                </div>
                            </bk-col>
                            <bk-col :span="3">
                                <div class="home-card-layout">
                                    <div class="card-title">分配协议<p class="fr">{{ consumer_group_data.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (consumer_group_data.protocol) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="typeof (consumer_group_data.protocol) === 'string'">{{ consumer_group_data.protocol }}</div>

                                </div>
                            </bk-col>
                            <bk-col :span="3">
                                <div class="home-card-layout">
                                    <div class="card-title">coordinator_id<p class="fr">{{ consumer_group_data.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (consumer_group_data.coordinator_id) === 'undefined'">暂无数据</div>
                                    <div class="monitor-data-card" v-show="typeof (consumer_group_data.coordinator_id) === 'string'">{{ consumer_group_data.coordinator_id }}</div>

                                </div>
                            </bk-col>
                        </bk-row>
                      
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">消费者组落后topic最新消息偏移进度</div>
                                    <div class="no-monitor-data-card" v-show="typeof (consumer_group_data.consumer_lag) === 'undefined'">暂无数据</div>
                                    <div id="message_behind_lag" class="bar-style" v-show="typeof (consumer_group_data.consumer_lag) === 'object'"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout">
                                    <div class="card-title">消费者组落后最新消息偏移进度(针对每个topic分区)<p class="fr">{{ consumer_group_data.last_time }}</p></div>
                                    <div class="no-monitor-data-card" v-show="typeof (consumer_group_data.consumer_lag_per_partition) === 'undefined' ">暂无数据</div>
                                    <div id="message_behind_lag_per_partition" class="bar-style" v-show="typeof (consumer_group_data.consumer_lag_per_partition) === 'object'"></div>
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
    export default {
      
        data () {
            return {
                confirmFnTip: false,
                isChecking: false,
                clusterLoading: true,
                topicLoading: true,
                consumerGroupLoading: true,
                logSizeChart: null,
                messageInRateChart: null,
                sentRateChart: null,
                receivedRateChart: null,
                receivedbytesRateChart: null,
                sentbytesRateChart: null,
                topicMessageChart: null,
                topicLogSizeChart: null,
                messageBehindLagChart: null,
                messageBehindLagPerPartitionChart: null,
                panels: [
                    { name: 'cluster_panel', label: '集群面板' },
                    { name: 'topic_panel', label: 'Topic面板' },
                    { name: 'consumer_group_panel', label: '消费组面板' }
                ],
                active: 'cluster_panel',
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
                cluster_detail: {},
                cluster_data: {},
                brokerData: [],
                topic_data: {},
                consumer_group_data: {},
                selectedTopic: '',
                selectedGroupId: '',
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
                        bottom: '3%',
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
            if (to.name !== 'kafkabroker') {
                localStorage.removeItem('kafka_condition')
            }
            
            next()
        },
        mounted () {
            const condition = localStorage.getItem('kafka_condition')
            if (condition != null) {
                this.cluster_detail = JSON.parse(condition)
                this.iscreatedMonitor()
            } else {
                this.cluster_detail = this.$route.query.row
                if (typeof (this.cluster_detail) === 'object' && this.cluster_detail.cluster_name !== '') {
                    localStorage.setItem('kafka_condition', JSON.stringify(this.cluster_detail))
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
                    this.getClusterMonitorData()
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
                        path: 'record'
                    }
                )
            },
            getClusterDetail () {
                this.$router.push(
                    {
                        path: 'broker', query: { 'row': this.cluster_detail }
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
                            const res = await this.$store.dispatch('kafka/createKafkaMonitor', param)
                            if (res.code === 0) {
                                const config = { theme: 'success' }
                                config.message = '提交成功, 跳转到Kafka执行记录中查看部署详情！'
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
                if (this.active === 'cluster_panel') {
                    this.clusterLoading = true
                    this.getClusterMonitorData()
                } else if (this.active === 'topic_panel') {
                    this.topicLoading = true
                    if (this.selectedTopic !== '') {
                        this.getTopicMonitorData()
                    } else {
                        this.topicLoading = false
                    }
                } else if (this.active === 'consumer_group_panel') {
                    this.consumerGroupLoading = true
                    if (this.selectedTopic !== '' && this.selectedGroupId !== '') {
                        this.getConsumerGroupMonitorData()
                    } else {
                        this.consumerGroupLoading = false
                    }
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
                    Data.xAxis[0].axisTick.alignWithLabel = true
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
            async getClusterMonitorData () {
                const param = {
                    'app_id': this.cluster_detail.app_id,
                    'cluster_name': this.cluster_detail.cluster_name,
                    'get_type': 'cluster',
                    'bk_data_id': this.cluster_detail.bk_data_id,
                    'access_token': this.cluster_detail.access_token,
                    'time_range': this.timeRangeTimestamp }
                try {
                    const res = await this.$store.dispatch('kafka/getMonitorData', param)
                    if (res.result) {
                        this.cluster_data = res.data
                        this.brokerData = res.data.broker_info
                        console.log(res.data.log_size_info)
                        console.log(res.data.message_in_rate)
                        this.PieChart(this.logSizeChart, 'log_data_size', res.data.log_size_info)
                        this.categoryChart(this.messageInRateChart, 'message_in_per_mins', res.data.dimensions, res.data.message_in_rate, false, 'line')
                        this.categoryChart(this.sentRateChart, 'requests_sent_per_mins', res.data.dimensions, res.data.requests_sent_rate, false, 'line')
                        this.categoryChart(this.receivedRateChart, 'requests_received_per_mins', res.data.dimensions, res.data.requests_received_rate, false, 'line')
                        this.categoryChart(this.receivedbytesRateChart, 'received_bytes_per_mins', res.data.dimensions, res.data.received_bytes_rate, false, 'line')
                        this.categoryChart(this.sentbytesRateChart, 'sent_bytes_per_mins', res.data.dimensions, res.data.sent_bytes_rate, false, 'line')
                    } else {
                        const config = { theme: 'error' }
                        config.message = res.message
                        config.offsetY = 80
                        this.$bkMessage(config)
                    }

                    this.clusterLoading = false
                } catch (e) {
                    console.error(e)
                    
                    this.clusterLoading = false
                }
            },
            async getTopicMonitorData () {
                const param = {
                    'app_id': this.cluster_detail.app_id,
                    'cluster_name': this.cluster_detail.cluster_name,
                    'get_type': 'topic',
                    'topic_name': this.selectedTopic,
                    'bk_data_id': this.cluster_detail.bk_data_id,
                    'access_token': this.cluster_detail.access_token,
                    'time_range': this.timeRangeTimestamp }
                
                try {
                    const res = await this.$store.dispatch('kafka/getMonitorData', param)
                    if (res.result) {
                        this.topic_data = res.data
                        this.categoryChart(this.topicMessageChart, 'topic_message_in', res.data.dimensions, res.data.topic_message_in_rate, false, 'line')
                        this.categoryChart(this.topicLogSizeChart, 'topic_log_size', res.data.topic_log_size_dimensions, res.data.topic_log_size, false, 'line')
                    } else {
                        const config = { theme: 'error' }
                        config.message = res.message
                        config.offsetY = 80
                        this.$bkMessage(config)
                    }
                    
                    this.topicLoading = false
                } catch (e) {
                    console.error(e)
                    this.topicLoading = false
                }
            },
            async getConsumerGroupMonitorData () {
                const param = {
                    'app_id': this.cluster_detail.app_id,
                    'cluster_name': this.cluster_detail.cluster_name,
                    'get_type': 'consumer_group',
                    'topic_name': this.selectedTopic,
                    'consumer_group_name': this.selectedGroupId,
                    'bk_data_id': this.cluster_detail.bk_data_id,
                    'access_token': this.cluster_detail.access_token,
                    'time_range': this.timeRangeTimestamp }
                
                try {
                    const res = await this.$store.dispatch('kafka/getMonitorData', param)
                    if (res.result) {
                        this.consumer_group_data = res.data
                        this.categoryChart(this.messageBehindLagChart, 'message_behind_lag', res.data.dimensions, res.data.consumer_lag, false, 'line')
                        this.categoryChart(this.messageBehindLagPerPartitionChart,
                                           'message_behind_lag_per_partition',
                                           res.data.consumer_lag_per_partition_dimensions,
                                           res.data.consumer_lag_per_partition,
                                           false,
                                           'bar')
                    } else {
                        const config = { theme: 'error' }
                        config.message = res.message
                        config.offsetY = 80
                        this.$bkMessage(config)
                    }
                    
                    this.consumerGroupLoading = false
                } catch (e) {
                    console.error(e)
                    this.consumerGroupLoading = false
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
