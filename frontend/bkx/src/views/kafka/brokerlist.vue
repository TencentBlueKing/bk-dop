<template>
    
    <div class="example1-wrapper">
        <bk-container :col="2">
            <bk-row>
                <bk-card title="集群信息" :is-collapse="true" :show-foot="true" :position="'right'">
                    <bk-row>
                        <bk-col :span="1">
                            <p>集群名称: {{ cluster_detail.cluster_name }}</p>
                            <p>集群版本: {{ cluster_detail.version }}</p>
                            <p>集群状态: {{ cluster_detail.cluster_status }}</p>
                            <p>添加模式: {{ cluster_detail.add_type }}</p>
                            <p>集群描述: {{ cluster_detail.description }}</p>
                        </bk-col>
                        <bk-col :span="1">
                            <p>zookeeper集群节点列表: {{ cluster_detail.zk_list }} </p>
                            <p>zookeeper集群访问端口: {{ cluster_detail.zk_port }} </p>
                            <p>broker节点数量: {{ cluster_detail.broker_cnt}}</p>
                            <p v-show=" cluster_detail.bk_data_id !== 0">添加蓝鲸监控: <bk-tag theme="success">已添加</bk-tag></p>
                            <p v-show=" cluster_detail.bk_data_id === 0">添加蓝鲸监控: <bk-tag theme="warning">未添加</bk-tag></p>
                        </bk-col>
                    </bk-row>
                    <div slot="footer" class="foot-main">
                        <span><i class="bk-icon icon-edit"></i> 信息修改</span>
                        <span @click="monitor"><i class="bk-icon icon-monitors"></i> 集群监控</span>
                    </div>
                </bk-card>
            </bk-row>
            <bk-row style="margin-top: 15px;">
                <bk-tab :active.sync="active" type="unborder-card" :before-toggle="gettab">
                    <bk-tab-panel
                        v-for="(panel, index) in panels"
                        v-bind="panel"
                        :key="index">
                    </bk-tab-panel>
                </bk-tab>
            </bk-row>

            <bk-row v-show="tab === 'broker'">
                <bk-alert class="mb10" type="info" title="目前通过平台录入的集群暂不开放集群管理操作" closable></bk-alert>
                <div class="mb10">
                    <bk-button size="large" :title="'集群扩容'" :disabled="isOpen" :hover-theme="'primary'" @click="addNoteSettings.isShow = true" class="mr10">集群扩容</bk-button>
                </div>
                <bk-table :data="tableData" v-bkloading="dataLoading">
                    <bk-table-column label="broker ip" prop="ip"></bk-table-column>
                    <bk-table-column label="broker部署端口" prop="broker_port"></bk-table-column>
                    <bk-table-column label="版本信息" prop="version"></bk-table-column>
                    <bk-table-column label="设备类型" prop="device_class"></bk-table-column>
                    <bk-table-column label="硬件信息" prop="hard_memo"></bk-table-column>
                </bk-table>
            </bk-row>

            <bk-row v-show="tab === 'topic'">
                <bk-alert class="mb10" type="info" title="创建topic任务是同步任务，暂时在任务记录没有记录" closable></bk-alert>
                <div class="mb10">
                    <bk-button size="large" :title="'创建Topic'" :disabled="isOpen" :hover-theme="'primary'" @click="addTopicSettings.isShow = true" class="mr10">创建Topic</bk-button>
                </div>
                <bk-table :data="tableData" v-bkloading="dataLoading">
                    <bk-table-column label="topic名称" prop="topic"></bk-table-column>
                    <bk-table-column label="创建人" prop="create_by"></bk-table-column>
                    <bk-table-column label="创建时间" prop="create_time"></bk-table-column>
                    <bk-table-column label="操作">
                        <template slot-scope="props">
                            <bk-button theme="primary" size="small" :disabled="isOpen" @click="checkTopic(props.row)">参数查看</bk-button>
                        </template>
                    </bk-table-column>
                </bk-table>
            </bk-row>
        </bk-container>
        <bk-sideslider
            :is-show.sync="addNoteSettings.isShow"
            :width="800"
            :before-close="beforeClose">
            <div slot="header">{{cluster_detail.cluster_name}}： {{ addNoteSettings.title }}</div>
            
            <div class="p20" slot="content">
                <div>
                    <bk-alert style="margin-top: 10px;" type="info" title="1> 待添加的节点都需要绑定你选择的业务上，否则后台检测任务失败" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="2> 部署的机器IP需要先安装gse_agent,具有业务job执行权限" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="3> 待添加的节点必须是新节点，扩容的IP必须尚未部署kafka进程，且/data/kafkaenv部署目录为空" closable></bk-alert>
                </div>
                <bk-divider type="dashed" style="margin-top: 50px;">填写待扩容信息</bk-divider>
                <div style="width: 600px; height: 500px ; margin-top: 50px;">
                    <bk-form :label-width="170" :model="addNodeformData" :rules="addNoderules" ref="addNodeForm">
                        <bk-form-item label="待扩容节点IP" :required="true" :property="'ips'" :error-display-type="'normal'">
                            <bk-input type="textarea" v-model="addNodeformData.ips" placeholder="待扩容的ip列表，用英文逗号或者空行隔开"></bk-input>
                        </bk-form-item>
                        <bk-form-item>
                            <bk-button ext-cls="mr5" theme="primary" title="提交" @click.stop.prevent="checkData('addNode')" :loading="isAddChecking">提交</bk-button>
                            <bk-button ext-cls="mr5" theme="default" title="取消" @click="beforeClose">取消</bk-button>
                        </bk-form-item>
                    </bk-form>

                </div>
            </div>
            
        </bk-sideslider>
        <bk-sideslider
            :is-show.sync="addTopicSettings.isShow"
            :width="800"
            :before-close="beforeClose">
            <div slot="header">{{cluster_detail.cluster_name}}：{{ addTopicSettings.title }}</div>
            <div class="p20" slot="content">
                <div>
                   
                    <bk-alert style="margin-top: 10px;" type="info" title="1> topic创建功能目前支持两种模式：默认模式和自定义模式"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="2> 默认模式下topic级别参数默认采取平台设定的参数，直接输入待创建topic名称即可"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="3> 自定义模式下可以根据业务场景情况来调整topic参数并创建"></bk-alert>
                </div>
            
                <bk-divider type="dashed" style="margin-top: 50px;">填写待添加topic信息</bk-divider>
                <div style="width: 600px; height: 500px ; margin-top: 50px;">
                    <bk-form :label-width="200" :model="newTopicForm" :rules="addTopicrules" ref="addTopicForm">
                        <bk-form-item label="添加模式">
                            <div class="bk-button-group">
                                <bk-button @click="selectManualMode" :class="newTopicForm.is_readonly === true ? 'is-selected' : ''">默认模式</bk-button>
                                <bk-button @click="selectCustomizeMode" :class="newTopicForm.is_readonly === false ? 'is-selected' : ''">自定义模式</bk-button>
                                            
                            </div>
                        </bk-form-item>
                        <bk-form-item label="待添加topic名称" :required="true" :property="'topic'" :error-display-type="'normal'">
                            <bk-input v-model="newTopicForm.topic" placeholder="请输入英文名称" :clearable="true" :maxlength="30" :show-word-limit="true"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="topic分区数" :required="true" :property="'topic_partition_sum'" :error-display-type="'normal'">
                            <bk-input v-model="newTopicForm.topic_partition_sum" placeholder="输入topic的分区数量" :readonly="newTopicForm.is_readonly"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="topic分区副本数" :required="true" :property="'topic_replication_factor'" :error-display-type="'normal'">
                            <bk-input v-model="newTopicForm.topic_replication_factor" placeholder="输入topic的分区副本数量" :readonly="newTopicForm.is_readonly"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="消息最大保存上限" :required="true" :property="'max_day'" :error-display-type="'normal'" :desc-type="'icon'" :desc="maxDayTips">
                            <bk-input v-model="newTopicForm.max_day" placeholder="请输入英文名称" :readonly="newTopicForm.is_readonly">
                                <template slot="append">
                                    <div class="group-text">天</div>
                                </template>
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item label="消息最大容量上限" :required="true" :property="'max_capacity_GB'" :error-display-type="'normal'" :desc-type="'icon'" :desc="maxCapacityTips">
                            <bk-input v-model="newTopicForm.max_capacity_GB" placeholder="请输入英文名称" :readonly="newTopicForm.is_readonly">
                                <template slot="append">
                                    <div class="group-text">GB</div>
                                </template>
                            </bk-input>
                        </bk-form-item>
                        
                        <bk-form-item label="正常消息接收长度上限" :required="true" :property="'max_message_MB'" :error-display-type="'normal'" :desc-type="'icon'" :desc="maxMessageTips">
                            
                            <bk-input v-model="newTopicForm.max_message_MB" placeholder="请输入英文名称" :readonly="newTopicForm.is_readonly">
                                <template slot="append">
                                    <div class="group-text">MB</div>
                                </template>
                            </bk-input>
                        </bk-form-item>

                        <bk-form-item>
                            <bk-button ext-cls="mr5" theme="primary" title="提交" @click.stop.prevent="checkData('createTopic')" :loading="isAddChecking">提交</bk-button>
                            <bk-button ext-cls="mr5" theme="default" title="取消" @click="beforeClose">取消</bk-button>
                        </bk-form-item>
                    </bk-form>

                </div>
            </div>
            
        </bk-sideslider>
        <bk-sideslider :is-show.sync="checkTopicSettings.isShow" :width="checkTopicSettings.width" @hidden="closeSideslider">
            <div slot="header">{{ checkTopicSettings.title }} -> 当前选择的topic名称：{{ checkTopicSettings.topic }}</div>
            <div class="p30" slot="content">
                <bk-container :col="12">
                    
                    <bk-row>
                        <bk-alert type="warning" title="topic级别参数查询是通过JOB平台调度到集群查询，建议避免频繁刷新" closable></bk-alert>
                    </bk-row>
                    <bk-row style="margin-top: 20px">
                        <bk-table
                            :data="topicParamDetails"
                            :outer-border="false"
                            :header-border="false"
                            v-bkloading="topicParamLoading">
                            <bk-table-column type="index" label="序列" width="100"></bk-table-column>
                            <bk-table-column label="topic级别参数名称" prop="param_name"></bk-table-column>
                            <bk-table-column label="参数值" prop="param_value"></bk-table-column>
                            
                        </bk-table>
                    </bk-row>

                </bk-container>
            </div>
        </bk-sideslider>
    </div>
</template>

<script>
    export default {
        components: {},
        data () {
            return {
                isOpen: false,
                isAddChecking: false,
                cluster_detail: {},
                tableData: [],
                topicParamDetails: [],
                tab: 'broker',
                addNoteSettings: {
                    isShow: false,
                    title: '集群扩容'
                },
                addTopicSettings: {
                    isShow: false,
                    title: 'topic创建'
                },
                checkTopicSettings: {
                    isShow: false,
                    title: 'topic级别参数配置查询',
                    width: 800,
                    topic: ''
                },
                addNodeformData: {
                    cluster_name: '',
                    ips: ''
                },
                dataLoading: {
                    isLoading: true,
                    zIndex: 10,
                    title: '数据加载中'
                },
                topicParamLoading: {
                    isLoading: true,
                    zIndex: 10,
                    title: '正在请求后端数据中'
                },
                newTopicForm: {
                    cluster_name: '',
                    topic: '',
                    is_readonly: true,
                    topic_partition_sum: 16,
                    topic_replication_factor: 3,
                    max_day: 7,
                    max_capacity_GB: -1,
                    max_message_MB: 1
                    
                },
                panels: [
                    { name: 'broker', label: 'broker信息' },
                    { name: 'topic', label: 'topic信息' }
                ],
                active: 'broker',
                addNoderules: {
                    ips: [
                        {
                            required: true,
                            message: '填写待扩容的IP列表',
                            trigger: 'blur'
                        }
                    ]
                },
                addTopicrules: {
                    topic: [
                        {
                            required: true,
                            message: '填写待添加的topic名称',
                            trigger: 'blur'
                        },
                        {
                            min: 3,
                            max: 30,
                            message: '长度在 3 到 50 个字符之间',
                            trigger: 'change'
                        }
                    ],
                    topic_partition_sum: [
                        {
                            required: true,
                            message: '填写topic的分区数量',
                            trigger: 'blur'
                        },
                        {
                            validator: function (val) {
                                return val > 0
                            },
                            message: '请输入大于0的数',
                            trigger: 'blur'
                        }

                    ],
                    topic_replication_factor: [
                        {
                            required: true,
                            message: '填写topic的分区副本数量',
                            trigger: 'blur'
                        },
                        {
                            validator: function (val) {
                                return val > 0
                            },
                            message: '请输入大于0的数',
                            trigger: 'blur'
                        }

                    ],
                    max_day: [
                        {
                            required: true,
                            message: '填写能保存最大天数',
                            trigger: 'blur'
                        },
                        {
                            validator: function (val) {
                                return val > 0
                            },
                            message: '请输入大于0的数',
                            trigger: 'blur'
                        }

                    ],
                    max_capacity_GB: [
                        {
                            required: true,
                            message: '填写能保存最大容量',
                            trigger: 'blur'
                        },
                        {
                            validator: function (val) {
                                return val === -1 || val === '-1' || val > 0
                            },
                            message: '请输入大于0的数,或者-1',
                            trigger: 'blur'
                        }
                    ],
                    max_message_MB: [
                        {
                            required: true,
                            message: '填写最大处理消息长度',
                            trigger: 'blur'
                        },
                        {
                            validator: function (val) {
                                return val >= 1
                            },
                            message: '请输入大于1的数',
                            trigger: 'blur'
                        }
                    ]
                },
                maxMessageTips: {
                    width: 350,
                    content: 'warning: 该参数建议小于broker的replica.fetch.max.bytes的值，这样保证复制性能正常；同时消费端参数 fetch.message.max.bytes 也需要做大于该参数的调整'
                },
                maxCapacityTips: {
                    content: '该参数默认值为-1，-1代表容量上没有限制'
                },
                maxDayTips: {
                    content: '该参数默认值为7天的记录'
                }
                
            }
        },
        beforeRouteLeave (to, from, next) {
            if (to.name === 'kafkamonitor') {
                next()
            } else {
                localStorage.removeItem('kafka_condition')
                next()
            }
        },
        mounted () {
            const condition = localStorage.getItem('kafka_condition')
            if (condition != null) {
                this.cluster_detail = JSON.parse(condition)
                this.addNodeformData.cluster_name = this.cluster_detail.cluster_name
            } else {
                const querydata = this.$route.query.row
                if (querydata.task_type === 10) {
                    // 表示任务记录重试扩容页面跳转过来，需要请求一次集群数据补全页面
                    this.addNoteSettings.isShow = true
                    this.addNodeformData.cluster_name = querydata.cluster_name
                    this.addNodeformData.ips = querydata.target_ips
                    this.cluster_detail.cluster_name = querydata.cluster_name
                    this.getKafkaData(this.cluster_detail.cluster_name)
                } else {
                    // 表示集群管理页面跳转过来，不需要请求
                    this.cluster_detail = querydata
                    this.addNodeformData.cluster_name = querydata.cluster_name
                }
            }
            if (this.cluster_detail.add_type === '平台录入') {
                this.isOpen = true
            }
            if (typeof (this.cluster_detail) === 'object' && this.cluster_detail.cluster_name !== '') {
                this.getKafkaBrokerInfo()
                localStorage.setItem('kafka_condition', JSON.stringify(this.cluster_detail))
            } else {
                // 非法请求提示后跳转到info界面
                this.$bkMessage({
                    message: '检测不到传入的集群名称，非法请求! 1秒后跳转到kafka集群管理界面',
                    theme: 'error'
                })
                setTimeout(() => {
                    this.$router.push(
                        {
                            name: 'kafkainfo'
                        }
                    )
                }, 1000)
            }
        },
        methods: {
            closeDialog () {
                this.$router.push(
                    {
                        name: 'kafkarecord'
                    }
                )
            },
            monitor () {
                this.$router.push({
                    name: 'kafkamonitor', query: { 'row': this.cluster_detail }
                })
            },
            selectCustomizeMode () {
                this.newTopicForm.is_readonly = false
                this.$refs.addTopicForm.clearError()
            },
            selectManualMode () {
                this.newTopicForm.is_readonly = true
                this.newTopicForm.topic = ''
                this.newTopicForm.max_day = 7
                this.newTopicForm.max_capacity_GB = -1
                this.newTopicForm.max_message_MB = 1
                this.$refs.addTopicForm.clearError()
            },
            beforeClose () {
                this.$bkInfo({
                    title: '请确认是否取消离开',
                    subTitle: '离开则丢失目前已填写好的信息',
                    confirmFn: () => {
                        this.addNodeformData.ips = ''
                        this.addNoteSettings.isShow = false
                        this.addTopicSettings.isShow = false
                        this.newTopicForm.is_readonly = true
                        this.newTopicForm.topic = ''
                        this.newTopicForm.max_day = 7
                        this.newTopicForm.max_capacity_GB = -1
                        this.newTopicForm.max_message_MB = 1
                        return true
                    }
                    
                })
            },
            closeSideslider () {
                this.topicParamDetails = []
                this.topicParamLoading.isLoading = true
                this.checkTopicSettings.topic = ''
            },
            beforeSubmit (val) {
                this.$bkInfo({
                    title: '请确认是否提交任务',
                    subTitle: '待操作集群名称：' + this.cluster_detail.cluster_name,
                    confirmFn: () => {
                        if (val === 'addNode') {
                            this.submitAddNodeData()
                        } else if (val === 'createTopic') {
                            this.submitNewTopic()
                        }
                        
                        return true
                    },
                    cancelFn: () => {
                        this.isAddChecking = false
                    }
                })
            },
            checkData (val) {
                if (val === 'addNode') {
                    this.$refs.addNodeForm.validate().then(validator => {
                        this.isAddChecking = true
                        this.beforeSubmit(val)
                    }, validator => {
                        this.isAddChecking = false
                    })
                } else if (val === 'createTopic') {
                    this.$refs.addTopicForm.validate().then(validator => {
                        this.isAddChecking = true
                        this.beforeSubmit(val)
                    }, validator => {
                        this.isAddChecking = false
                    })
                }
            },
            gettab (panelName) {
                this.tab = panelName
                if (this.tab === 'broker') {
                    this.getKafkaBrokerInfo()
                } else if (this.tab === 'topic') {
                    this.getKafkaTopicInfo()
                }

                return panelName
            },
           
            async getKafkaData (clusterName) {
                try {
                    const param = { 'cluster_name': clusterName }
                    const res = await this.$store.dispatch('kafka/getKafkaData', param)
                    if (res.data.length !== 0) {
                        this.cluster_detail = res.data[0]
                    
                        localStorage.setItem('kafka_condition', JSON.stringify(this.cluster_detail))
                    }
                } catch (e) {
                    console.error(e)
                }
            },
            async getKafkaBrokerInfo () {
                this.dataLoading.isLoading = true
                try {
                    const param = { 'cluster_name': this.cluster_detail.cluster_name }
                    const res = await this.$store.dispatch('kafka/getKafkaBroker', param)
                    this.tableData = res.data
                    this.dataLoading.isLoading = false
                } catch (e) {
                    this.dataLoading.isLoading = false
                    console.error(e)
                }
            },
            async getKafkaTopicInfo () {
                this.dataLoading.isLoading = true
                try {
                    const param = { 'cluster_name': this.cluster_detail.cluster_name }
                    const res = await this.$store.dispatch('kafka/listTopics', param)
                    this.tableData = res.data
                    this.dataLoading.isLoading = false
                } catch (e) {
                    this.dataLoading.isLoading = false
                    console.error(e)
                }
            },
            async submitNewTopic () {
                this.newTopicForm.cluster_name = this.cluster_detail.cluster_name
                try {
                    const res = await this.$store.dispatch('kafka/createTopic', this.newTopicForm)
                    if (res.code === 0) {
                        this.isAddChecking = false
                        this.$bkMessage({
                            message: 'topic创建成功',
                            theme: 'success'
                        })
                    } else {
                        this.isAddChecking = false
                        this.$bkMessage({
                            message: 'topic创建失败',
                            theme: 'error'
                        })
                    }
                } catch (e) {
                    this.isAddChecking = false
                    console.error('submit err: ', e)
                } finally {
                    this.addTopicSettings.isShow = false
                    this.newTopicForm.topic = ''
                    this.newTopicForm.max_day = 7
                    this.newTopicForm.max_capacity_GB = -1
                    this.newTopicForm.max_message_MB = 1
                    this.getKafkaTopicInfo()
                }
            },
            async submitAddNodeData () {
                try {
                    const res = await this.$store.dispatch('kafka/addBroker', this.addNodeformData)
                    if (res.code === 0) {
                        this.isAddChecking = false
                        const config = { theme: 'success' }
                        config.message = '提交成功, 跳转到Kafka执行记录中查看部署详情！'
                        config.offsetY = 80
                        this.$bkMessage(config)
                        this.closeDialog()
                    } else {
                        this.isAddChecking = false
                        const config = { theme: 'error' }
                        config.message = res.message
                        config.offsetY = 80
                        this.$bkMessage(config)
                    }
                } catch (e) {
                    this.isAddChecking = false
                    console.log(e)
                }
            },
            async checkTopic (row) {
                this.checkTopicSettings.isShow = true
                this.checkTopicSettings.topic = row.topic
                try {
                    const param = { 'cluster_name': row.cluster_name, 'topic': row.topic }
                    const res = await this.$store.dispatch('kafka/checkTopic', param)
                    this.topicParamDetails = res.data
                    this.topicParamLoading.isLoading = false
                } catch (e) {
                    this.topicParamLoading.isLoading = false
                    console.error(e)
                }
            }
            
        }
    }
</script>
<style lang="postcss">
    .foot-main {
        width: 100%;
        height: 100%;
        background: #fafbfd;
        color: #979ba5;
        
        span {
            display: inline-block;
            width: 50%;
            line-height: 50px;
            float: left;
            text-align: center;
            font-size: 15px;
        }
        span:hover {
            background: #f0f1f5;
            color: #63656e;
            cursor: pointer;
        }
    }
    .bk-card-body {
        p {
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 8px;
            &:last-child {
                margin-bottom: 0;
            }
        }
    }
</style>
