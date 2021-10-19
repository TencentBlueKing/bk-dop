<template>
    <div class="main-grid">
        <div class="wrapper flex">
            
            <bk-container flex :col="15">
                <bk-row>
                    <bk-col :span="6"><div class="home-card-layout">
                        <div class="card-title">平台公告</div>
                        <div ref="swiper" id="swiper">
                            <bk-swiper :list="list" ext-cls="swiper-boby" :width="swiperWidth" v-if="update">
                                <template slot-scope="item">
                                    <div class="swiper-content">
                                        <p>{{item.data}}</p>
                                    </div>
                                </template>
                            </bk-swiper>
                        </div>
   
                    </div></bk-col>
                    <bk-col :span="9">
                        <bk-row>
                            <bk-col :span="3">
                                <div class="home-card-layout" v-bkloading="{ isLoading: clusterNumLoading, title: '数据加载中', zIndex: 10 }">
                                    <div class="card-title">各组件集群数量比例</div>
                                    <div class="no-data-card" v-show="cluster_pie_data.data.length === 0">暂无数据</div>
                                    <div id="clusternum" class="echart_style" v-show="cluster_pie_data.data.length !== 0"></div>
                                </div>
                            </bk-col>
                            <bk-col :span="3">
                                <div class="home-card-layout" v-bkloading="{ isLoading: machineNumLoading, title: '数据加载中', zIndex: 10 }">
                                    <div class="card-title">各组件投入机器数量比例</div>
                                    <div class="no-data-card" v-show="machine_pie_data.data.length === 0">暂无数据</div>
                                    <div id="machinenum" class="echart_style" v-show="machine_pie_data.data.length !== 0"></div>
                                </div>
                            </bk-col>
                                
                            <bk-col :span="3">
                                <div class="home-card-layout" v-bkloading="{ isLoading: taskNumLoading, title: '数据加载中', zIndex: 10 }">
                                    <div class="card-title">各组件执行任务数量比例</div>
                                    <div class="no-data-card" v-show="task_pie_data.data.length === 0">暂无数据</div>
                                    <div id="tasknum" class="echart_style" v-show="task_pie_data.data.length !== 0"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                        
                    </bk-col>
                </bk-row>
                <bk-row>
                    <bk-col :span="9">
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout" v-bkloading="{ isLoading: esBarTopLoading, title: '数据加载中', zIndex: 10 }">
                                    <div id="es_chart" class="card-title">ES各业务资源统计TOP5</div>
                                    <div class="no-data-bar" v-show="es_data.length === 0">
                                        <bk-link @click="pageToEsNew" theme="primary" icon="bk-icon icon-plus-square" v-bk-tooltips.right="'点击可快速进入Es部署导航页面'"><p style="font-size:25px;">暂无数据</p></bk-link>
                                    </div>
                                    
                                    <div id="es_bar_top_5" class="bar-style" v-show="es_data.length !== 0"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout" v-bkloading="{ isLoading: hadoopBarTopLoading, title: '数据加载中', zIndex: 10 }">
                                    <div class="card-title">Hadoop各业务资源统计TOP5</div>
                                    <div class="no-data-bar" v-show="hadoop_data.length === 0">
                                        <bk-link @click="pageToHadoopNew" theme="primary" icon="bk-icon icon-plus-square" v-bk-tooltips.right="'点击可快速进入Hadoop部署导航页面'"><p style="font-size:25px;">暂无数据</p></bk-link>
                                    </div>
                                    <div id="hadoop_bar_top_5" class="bar-style" v-show="hadoop_data.length !== 0"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout" v-bkloading="{ isLoading: kafkaBarTopLoading, title: '数据加载中', zIndex: 10 }">
                                    <div class="card-title">Kafka各业务资源统计TOP5</div>
                                    <div class="no-data-bar" v-show="kafka_data.length === 0">
                                        <bk-link @click="pageToKafkaNew" theme="primary" icon="bk-icon icon-plus-square" v-bk-tooltips.right="'点击可快速进入Kafka部署导航页面'"><p style="font-size:25px;">暂无数据</p></bk-link>
                                    </div>
                                    <div id="kafka_bar_top_5" class="bar-style" v-show="kafka_data.length !== 0"></div>
                                </div>
                            </bk-col>
                        </bk-row>
                    </bk-col>
                    
                    <bk-col :span="6">
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout" v-bkloading="{ isLoading: RuntaskLoading, title: '数据加载中', zIndex: 10 }">
                                    <a @click="pageTorunTask" class="work-statistics-box">
                                        <div class="work-flag">
                                            <bk-icon type="pc-shape" svg style="width: 1em; height: 1.7em; font-size: xxx-large; color:#5470c6">
                                            </bk-icon>
                                        </div>
                                        <div class="work-total"><span>{{ runTask }}</span></div>
                                        <div class="work-name"><span>正在执行任务数</span></div>
                                    </a>
                                    
                                </div>
                            </bk-col>
                        </bk-row>
                        <bk-row>
                            <bk-col :span="12">
                                <div class="home-card-layout" v-bkloading="{ isLoading: tableLoading, title: '数据加载中', zIndex: 10 }">
                                    <div class="card-title">
                                        <p>异常任务信息列表</p>
                                    </div>
                  
                                    <div class="history-record-box">
                                        <bk-table
                                            :data="tableData"
                                            :size="size"
                                            :outer-border="false"
                                            :header-border="false"
                                            :header-cell-style="{ background: '#fff' }"
                                            :pagination="pagination"
                                            :limit-list="pagination.limitList"
                                            @row-mouse-enter="handleRowMouseEnter"
                                            @row-mouse-leave="handleRowMouseLeave"
                                            @page-change="handlePageChange"
                                            @page-limit-change="handleLimitChange">
                                            <bk-table-column label="集群名称" prop="cluster_name"></bk-table-column>
                                            <bk-table-column label="组件名称" prop="db_type"></bk-table-column>
                                            <bk-table-column label="任务类型" prop="task_type"></bk-table-column>
                                            <bk-table-column label="操作人" prop="op_user"></bk-table-column>
                                            <bk-table-column label="任务状态" prop="task_status" sortable></bk-table-column>
                                            <bk-table-column label="操作">
                                                <template slot-scope="props">
                                                    <bk-button theme="danger" size="small" @click="check(props.row)">查看</bk-button>
                                                </template>
                                            </bk-table-column>
                                        </bk-table>
                                    </div>
                                    
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
                clusterNumLoading: true,
                machineNumLoading: true,
                taskNumLoading: true,
                esBarTopLoading: true,
                hadoopBarTopLoading: true,
                kafkaBarTopLoading: true,
                RuntaskLoading: true,
                tableLoading: true,
                esTopChart: null,
                hadoopTopChart: null,
                kafkaTopChart: null,
                clsuterChart: null,
                taskChart: null,
                machineChart: null,
                runTask: 0,
                size: 'small',
                swiperWidth: 0,
                update: false,
                pagination: {
                    small: true,
                    current: 1,
                    count: 0,
                    limit: 5,
                    limitList: [5, 10, 15]
                },
                list: [
                    'DOP平台基于蓝鲸开发，集成了ES、Hadoop、Kafka等常用大数据组件，\n旨在提高大数据组件的运维效率和安全效率',
                    '平台不仅提供”集群新建“模式来管控属于你的业务的集群，\n还能通过”集群录入“模式来管理非平台本身创建的集群',
                    '待部署的机器必须所属于你选择的业务,\n并且需要安装JOB平台GSE权限',
                    '用户若在部署、录入、查询集群过程中无法选择到对应的业务名称，\n则需要查看配置平台和权限中心是否有该业务的权限',
                    '目前平台对通过录入的第三方集群尚未适配管控功能，未来版本会开放，敬请期待'
                    
                ],
                failTaskData: [],
                runTaskDetail: [],
                es_data: [],
                hadoop_data: [],
                kafka_data: [],
                cluster_pie_data: {
                    text: '各组件集群数量比例',
                    data: []
                },
                machine_pie_data:
                    {
                        text: '各组件机器数量比例',
                        data: []
                    },
                task_pie_data: {
                    text: '各组件执行任务数比例',
                    data: []
                },
                pie_sample: {
                    tooltip: {
                        trigger: 'item',
                        textStyle: {
                            fontSize: 10
                        }
                    },
                  
                    series: [
                        {
                            name: '',
                            type: 'pie',
                            radius: ['40%', '70%'],
                            avoidLabelOverlap: false,
                            itemStyle: {
                                borderRadius: 10,
                                borderColor: '#fff',
                                borderWidth: 2
                            },
                            label: {
                                show: false,
                                position: 'center'
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
                rose_sample: {
                
                    tooltip: {
                        trigger: 'item',
                        textStyle: {
                            fontSize: 10
                        },
                        formatter: '{a} <br/>{b} : {c} ({d}%)'
                    },
                    legend: {
                        top: 'middle',
                        left: 0,
                        orient: 'vertical'
                    },
                    toolbox: {
                        show: true,
                        feature: {
                            mark: { show: true },
                            dataView: { show: true, readOnly: true },
                            restore: { show: true },
                            saveAsImage: { show: true }
                        }
                    },
                    series: [
                        {
                            name: '机器数量',
                            type: 'pie',
                            radius: [55, 100],
                            center: ['50%', '50%'],
                            roseType: 'area',
                            itemStyle: {
                                borderRadius: 10
                            },
                            data: []
                        }
                    ]
                }
            }
        },
        computed: {
            tableData: function () {
                const start = (this.pagination.current - 1) * this.pagination.limit
                const end = start + this.pagination.limit < this.pagination.count ? start + this.pagination.limit : this.pagination.count
                return this.failTaskData.slice(start, end)
            }
        },
        mounted () {
            this.getTaskStatistics()
            this.getClusterStatistics()
            this.getMachineStatistics()
            this.getEsMachineStatisticsTop5()
            this.getHadoopMachineStatisticsTop5()
            this.getKafkaMachineStatisticsTop5()
            this.getRunTaskCount()
            this.getFailTaskInfo()
            this.swiperpage()
        },
        methods: {
            swiperpage () {
                const that = this
                const object = document.getElementById('swiper')
                const Resize = elementResize({
                    strategy: 'scroll', // <- 推荐监听滚动，提升性能
                    callOnAdd: true // 添加侦听器时是否应调用,默认true
                })
                Resize.listenTo(object, function (element) {
                    that.update = false
                    that.swiperWidth = object.clientWidth
                    that.$nextTick(() => {
                        that.update = true
                    })
                })
            },

            PieChart (chart, divId, xdata) {
                const Data = this.pie_sample
                Data.series[0].name = xdata.text
                Data.series[0].data = xdata.data
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
            RoseChart (topChart, divId, xdata) {
                const Data = this.rose_sample
                const object = document.getElementById(divId)

                Data.series[0].data = xdata
                topChart = echarts.init(object)
                topChart.setOption(Data)
                const Resize = elementResize({
                    strategy: 'scroll', // <- 推荐监听滚动，提升性能
                    callOnAdd: true // 添加侦听器时是否应调用,默认true
                })
                Resize.listenTo(object, function (element) {
                    echarts.init(object).resize() // 当元素尺寸发生改变是会触发此事件，刷新图表
                })
            },
            handlePageChange (page) {
                this.pagination.current = page
            },
            handleLimitChange (limit) {
                this.pagination.limit = limit
                this.handlePageChange(1)
            },
            async getTaskStatistics () {
                try {
                    const res = await this.$store.dispatch('common/getTaskStatistics')
                    this.task_pie_data.data = res.data
                    this.PieChart(this.taskChart, 'tasknum', this.task_pie_data)
                    this.taskNumLoading = false
                } catch (e) {
                    console.error(e)
                    this.taskNumLoading = false
                }
            },
            async getClusterStatistics () {
                try {
                    const esRes = await this.$store.dispatch('es/getEsData')
                    const hadoopRes = await this.$store.dispatch('hadoop/getHadoopData')
                    const kafkaRes = await this.$store.dispatch('kafka/getKafkaData')
                    if (esRes.data.length !== 0 || hadoopRes.data.length !== 0 || kafkaRes.data.length !== 0) {
                        const data = [
                            { value: esRes.data.length, name: 'ES集群数量' },
                            { value: hadoopRes.data.length, name: 'Hadoop集群数量' },
                            { value: kafkaRes.data.length, name: 'Kafka集群数量' }
                        ]
                        this.cluster_pie_data.data = data
                    }
                    this.PieChart(this.clsuterChart, 'clusternum', this.cluster_pie_data)
                    this.clusterNumLoading = false
                } catch (e) {
                    console.error(e)
                    this.clusterNumLoading = false
                }
            },
            async getMachineStatistics () {
                try {
                    const esRes = await this.$store.dispatch('es/getMachineCount')
                    const hadoopRes = await this.$store.dispatch('hadoop/getMachineCount')
                    const kafkaRes = await this.$store.dispatch('kafka/getMachineCount')
                    if (esRes.data !== '0' || hadoopRes.data !== '0' || kafkaRes.data !== '0') {
                        const data = [
                            { value: esRes.data, name: 'ES投入机器数量' },
                            { value: hadoopRes.data, name: 'Hadoop投入机器数量' },
                            { value: kafkaRes.data, name: 'Kafka投入机器数量' }
                        ]
                        this.machine_pie_data.data = data
                    }
                    this.PieChart(this.machineChart, 'machinenum', this.machine_pie_data)
                    this.machineNumLoading = false
                } catch (e) {
                    console.error(e)
                    this.machineNumLoading = false
                }
            },
            async getEsMachineStatisticsTop5 () {
                try {
                    const esRes = await this.$store.dispatch('es/getMachineCountTop5')
                    this.es_data = esRes.data
                    this.RoseChart(this.esTopChart, 'es_bar_top_5', this.es_data)
                    this.esBarTopLoading = false
                } catch (e) {
                    console.error(e)
                    this.esBarTopLoading = false
                }
            },
            async getHadoopMachineStatisticsTop5 () {
                try {
                    const hadoopRes = await this.$store.dispatch('hadoop/getMachineCountTop5')
                    this.hadoop_data = hadoopRes.data
                    this.RoseChart(this.hadoopTopChart, 'hadoop_bar_top_5', this.hadoop_data)
                    this.hadoopBarTopLoading = false
                } catch (e) {
                    console.error(e)
                    this.hadoopBarTopLoading = false
                }
            },
            async getKafkaMachineStatisticsTop5 () {
                try {
                    const kafkaRes = await this.$store.dispatch('kafka/getMachineCountTop5')
                    this.kafka_data = kafkaRes.data

                    this.RoseChart(this.kafkaTopChart, 'kafka_bar_top_5', this.kafka_data)
                    this.kafkaBarTopLoading = false
                } catch (e) {
                    console.error(e)
                    this.kafkaBarTopLoading = false
                }
            },
            async getRunTaskCount () {
                try {
                    const res = await this.$store.dispatch('common/getTaskRecord', { 'task_status': 2 })
                    this.runTask = res.data.length
                    this.runTaskDetail = res.data
                    this.RuntaskLoading = false
                } catch (e) {
                    console.error(e)
                    this.RuntaskLoading = false
                }
            },
            async getFailTaskInfo () {
                try {
                    const res = await this.$store.dispatch('common/getTaskRecord', { 'task_status': 4 })
                    this.failTaskData = res.data
                    this.pagination.count = res.data.length
                    this.tableLoading = false
                } catch (e) {
                    console.error(e)
                    this.tableLoading = false
                }
            },
            check (row) {
                this.$router.push(
                    {
                        name: 'taskrecord', query: { 'row': [row] }
                    }
                )
            },
            pageTorunTask () {
                if (this.runTask !== 0) {
                    this.$router.push(
                        {
                            name: 'taskrecord', query: { 'row': this.runTaskDetail }
                        }
                    )
                }
            },
            pageToEsNew () {
                this.$router.push(
                    {
                        name: 'esnew'
                    }
                )
            },
            pageToHadoopNew () {
                this.$router.push(
                    {
                        name: 'hadoopnew'
                    }
                )
            },
            pageToKafkaNew () {
                this.$router.push(
                    {
                        name: 'kafkanew'
                    }
                )
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
        
        .history-record-box {
            position: relative;
            width: 100%;
            height: 742px;

        }
        .card-title {
                  margin-bottom: 20px;
                  font-size: 14px;
                  font-weight: 700;
                  line-height: 1;
                  color: #313238;
                 
                  }
        .no-data-card{
            font-size: 25px;
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
