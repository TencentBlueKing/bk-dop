<template>
    
    <div class="main-grid">
        <div>
            <bk-sideslider :is-show.sync="defaultSettings.isShow" :quick-close="true" :width="800">
                <div slot="header">{{ defaultSettings.title }}</div>
                <div class="p20" slot="content">
                   
                    <bk-alert style="margin-top: 10px;" type="info" title="1> Kafka集群录入支持两种模式：手动模式和ZK检测模式，和根据自己的需求来选择其中一种"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="2> 如果选择ZK检测模式，待录入broker信息只需填写一个，且安装python2.7以上版本"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="3> 待部署集群的所有待纳管节点信息都需要绑定你选择的业务上，否则后台检测任务失败"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="4> 用户在选择业务时只能选择在配置平台已有权限的业务"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="5> 部署的机器IP需要先安装gse_agent,具有业务job执行权限"></bk-alert>
                    
                </div>
            </bk-sideslider>
        </div>
        <div class="wrapper flex">
            
            <bk-container :col="12">
                <bk-form :label-width="180" :model="formData" :rules="rules" ref="validateForm1">
                    <bk-row>
                        <bk-col :span="12">
                            <bk-alert type="info">
                                <bk-button slot="title" text @click="defaultSettings.isShow = true">查看Kafka集群录入说明指引请点击</bk-button>
                            </bk-alert>
                        </bk-col>
                    </bk-row>
                
                    <bk-row>
                    
                        <bk-col :span="12">
                            <div class="home-card-layout">

                                <div class="card-title">集群录入基本信息</div>
                                <div style="width: 800px">
                                
                                    <bk-form-item label="业务名称" :required="true" :property="'app'" :error-display-type="'normal'">
                                        <bk-select v-model="formData.app_id" searchable>
                                            <bk-option v-for="option in appList"
                                                :key="option.bk_biz_id"
                                                :id="option.bk_biz_id"
                                                :name="option.bk_biz_name">
                                            </bk-option>
                                        </bk-select>
                                    </bk-form-item>
                                    <bk-form-item label="集群名称" :required="true" :property="'cluster_name'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.cluster_name" placeholder="请输入集群名称" :clearable="true" :maxlength="100" :show-word-limit="true"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                    <bk-form-item label="版本类型" :required="true" :property="'version_type'" :error-display-type="'normal'">
                                        <bk-select v-model="formData.version_type">
                                            <bk-option v-for="option in versionTypeList"
                                                :key="option.id"
                                                :id="option.id"
                                                :name="option.name">
                                            </bk-option>
                                        </bk-select>
                                    </bk-form-item>
                                    <bk-form-item label="版本编号" :required="true" :property="'version_no'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.version_no" placeholder="请输入对应的版本编号，输入格式: 0.0.0"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item label="项目描述">
                                        <bk-input type="textarea" v-model="formData.description" :clearable="true" :maxlength="100" :show-word-limit="true"></bk-input>
                                    </bk-form-item>
                                </div>
                            
                            </div>
                        </bk-col>
            
                    </bk-row>
                    <bk-row>
                        <bk-col :span="12">
                            <div class="home-card-layout">
                                <div class="card-title">集群录入模式</div>
                                <div style="width: 800px">
                                    <bk-form-item label="选择模式" :required="true" :property="'spec'" :error-display-type="'normal'">
                                        <div class="bk-button-group">
                                            <bk-popover placement="top" content="通过提供的zookeeper集群信息去检测kafka集群，适合规格比较大，并且依赖zk的集群">
                                                <bk-button @click="selectZkMode()" :class="formData.is_check_by_zk === 1 ? 'is-selected' : ''">ZK检测模式</bk-button>
                                            </bk-popover>
                                            <bk-popover placement="top" content="通过手动填写kafka的broker信息和topic信息的方式去做录入，适合规格小，并且没有依赖zk的集群">
                                                <bk-button @click="selectManualMode()" :class="formData.is_check_by_zk === 0 ? 'is-selected' : ''">手动模式</bk-button>
                                            </bk-popover>
                                            
                                        </div>
                                    </bk-form-item>
                                    <bk-form-item v-if="formData.is_check_by_zk === 1" label="ZK节点信息" :required="true" :property="'kafka_zk_list'" :error-display-type="'normal'">
                                        <bk-input type="textarea" v-model="formData.kafka_zk_list" placeholder="请输入kafka注册的zookeeper集群节点信息列表,用英文逗号或者空行隔开,该节点信息不做业务所属检测"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item v-if="formData.is_check_by_zk === 1" label="ZK访问端口" :required="true" :property="'kafka_zk_port'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.kafka_zk_port" placeholder="请输入kafka注册的zookeeper集群访问端口,若没有设置则不需要填写"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item v-show="formData.is_check_by_zk === 1" label="ZK chroot信息">
                                        <bk-input v-model="formData.chroot" placeholder="请输入kafka在zk的别名信息,若没有设置则不需要填写"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item label="broker端口" :required="true" :property="'broker_port'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.broker_port" placeholder="请输入broker访问端口号"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item label="broker节点信息" :required="true" :property="'broker_list'" :error-display-type="'normal'">
                                        <bk-input type="textarea" v-model="formData.broker_list" placeholder="请输入broker的IP列表，用英文逗号或者空行隔开，如果选择‘ZK检测模式’,则填写一个节点信息即可"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item v-show="formData.is_check_by_zk === 0" label="topic信息">
                                        <bk-input type="textarea" v-model="formData.topic_list" placeholder="请输入topic信息列表，用英文逗号或者空行隔开，若没有设置则不需要填写"></bk-input>
                                    </bk-form-item>
                      
                                </div>
                            </div>
                        </bk-col>
                    </bk-row>
                    <bk-row v-if="formData.is_check_by_zk === 0">
                        <bk-col :span="12">
                            <div class="home-card-layout">
                                <div class="card-title">待录入ZK信息</div>
                                <div style="width: 800px">
                                    <bk-form-item label="是否关联ZK集群">
                                        <bk-button
                                            theme="primary"
                                            :outline="true"
                                            icon="plus"
                                            class="mr10"
                                            @click="isShow = true">
                                            添加ZK集群
                                        </bk-button>
                                        <bk-button
                                            theme="danger"
                                            :outline="true"
                                            icon="minus"
                                            class="mr10"
                                            @click="closeZkInfo()">
                                            删除ZK集群
                                        </bk-button>
                                    </bk-form-item>
                                    <bk-form-item label="ZK节点信息" v-show="isShow">
                                        <bk-input v-model="formData.kafka_zk_list" placeholder="请输入kafka注册的zookeeper集群节点信息列表,用英文逗号或者空行隔开"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                    <bk-form-item label="ZK访问端口" v-show="isShow">
                                        <bk-input v-model="formData.kafka_zk_port" placeholder="请输入kafka注册的zookeeper集群访问端口"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                   
                                </div>
                            </div>
                        </bk-col>
                    </bk-row>
                    <bk-row>
                        <bk-col :span="12">
                            <div class="home-card-layout">
                                <div class="card-title">集群监控信息</div>
                                <div style="width: 800px">
                                    <bk-form-item label="是否添加监控" :required="true" :property="'is_create_bk_monitor'" :error-display-type="'normal'" :desc-type="'icon'" :desc="monitorTips">
                                        <bk-radio-group v-model="formData.is_create_bk_monitor">
                                            <bk-radio :value="'0'">不添加</bk-radio>
                                            <bk-radio :value="'1'">添加</bk-radio>
                                        </bk-radio-group>
                                    </bk-form-item>
                                   
                                </div>
                            </div>
                        </bk-col>
                    </bk-row>
                    <bk-row>
                        <bk-col :span="12">
                        
                            <bk-form-item>
                                <bk-button ext-cls="mr5" theme="primary" title="提交" :loading="isChecking" @click.stop.prevent="checkData">提交</bk-button>
                                <bk-button ext-cls="mr5" theme="default" title="取消" @click.stop.prevent="clearError">取消</bk-button>
                            </bk-form-item>
                       
                        </bk-col>
                    
                    </bk-row>
                </bk-form>
            </bk-container>
        </div>
    </div>
</template>

<script>

    export default {
       
        data () {
            return {
                defaultSettings: {
                    isShow: false,
                    title: 'Kafka集群录入说明'
                },
                formData: {
                    cluster_name: '',
                    version_type: '',
                    version_no: '',
                    broker_port: '9092',
                    broker_list: '',
                    topic_list: '',
                    description: '',
                    app: '',
                    app_id: '',
                    is_check_by_zk: 1,
                    kafka_zk_list: '',
                    kafka_zk_port: '',
                    chroot: '',
                    is_create_bk_monitor: '0'

                },
                isShow: false,
                appList: [],
                isChecking: false,
                versionTypeList: [
                    {
                        id: 'apache',
                        name: 'apache'
                    },
                    {
                        id: 'confluent',
                        name: 'confluent'
                    }
                ],
                monitorTips: {
                    width: 300,
                    content: '添加监控在独立的后台任务，主要联动蓝鲸监控平台针对此集群添加监控配置信息,若有属于独立蓝鲸监控平台之外的一套监控体系，可以选择不部署'
                },
                
                rules: {
                    app: [
                        {
                            required: true,
                            message: '选择对应的业务名称',
                            trigger: 'change'
                        }
                    ],
                    cluster_name: [
                        {
                            required: true,
                            pattern: /^[a-z0-9]+[a-z0-9-]+[a-z0-9]+$/,
                            message: '请输入集群名称(只能包含小写字母，数字，-)',
                            trigger: 'change'
                        },
                        {
                            min: 2,
                            max: 100,
                            message: '长度在 2 到 100 个字符',
                            trigger: 'change'
                        }
                        
                    ],
                    version_type: [
                        {
                            required: true,
                            message: '请选择对应的版本类型',
                            trigger: 'change'
                        }
                    ],
                    version_no: [
                        {
                            required: true,
                            message: '请填写对应的版本编号',
                            trigger: 'change'
                        }
                    ],
                    broker_list: [
                        {
                            required: true,
                            message: 'broker节点为空',
                            trigger: 'change'
                        }
                    ],
                    broker_port: [
                        {
                            required: true,
                            message: 'broker端口节点为空',
                            trigger: 'change'
                        }
                    ],
                    kafka_zk_list: [
                        {
                            required: true,
                            message: '请输入集群初始用户名称',
                            trigger: 'change'
                        }
                    ],
                    kafka_zk_port: [
                        {
                            required: true,
                            message: '请输入集群初始用户密码',
                            trigger: 'change'
                        }
                    ],
                    is_create_bk_monitor: [
                        {
                            required: true,
                            message: '选择是否部署监控',
                            trigger: 'change'
                        }
                    ]
                }
            }
        },
        watch: {
            'formData.app_id': function (val) {
                this.formData.app_id = val
                this.appList.forEach(item => {
                    if (this.formData.app_id === item.bk_biz_id) {
                        this.formData.app = item.bk_biz_name
                        return true
                    }
                }
                )
            }
        },
        created () {
            this.getCc()
            if (this.$route.query.row) {
                const querydata = JSON.parse(this.$route.query.row)
                this.formData.cluster_name = querydata.cluster_name
                this.formData.version_type = querydata.version_type
                this.formData.version_no = querydata.version_no
                this.formData.broker_port = querydata.broker_port
                this.formData.broker_list = querydata.target_ips
                this.formData.topic_list = querydata.topic_list
                this.formData.is_check_by_zk = querydata.is_check_by_zk
                this.formData.kafka_zk_list = querydata.broker_str
                this.formData.kafka_zk_port = querydata.kafka_zk_port
                this.formData.description = querydata.description
                this.formData.app = querydata.app
                this.formData.app_id = querydata.app_id
                this.formData.is_create_bk_monitor = querydata.is_create_bk_monitor.toString()
                if (querydata.is_check_by_zk === 0 && querydata.kafka_zk_port !== 0) {
                    this.isShow = true
                }
            }
        },
        methods: {
            closeDialog () {
                this.$router.push(
                    {
                        path: 'record'
                    }
                )
            },
            closeZkInfo () {
                this.isShow = false
                this.formData.kafka_zk_list = ''
                this.formData.kafka_zk_port = ''
            },
            selectZkMode () {
                this.formData.is_check_by_zk = 1
                this.formData.kafka_zk_list = ''
                this.formData.kafka_zk_port = ''
                this.formData.chroot = ''
                this.formData.broker_list = ''
                this.formData.topic_list = ''
            },
            selectManualMode () {
                this.formData.is_check_by_zk = 0
                this.formData.kafka_zk_list = ''
                this.formData.kafka_zk_port = ''
                this.formData.chroot = ''
                this.formData.broker_list = ''
                this.formData.topic_list = ''
            },
            async submitnewclusterForm () {
                try {
                    const res = await this.$store.dispatch('kafka/inputKafkaCluster', this.formData)
                    if (res.code === 0) {
                        this.isChecking = false
                        const config = { theme: 'success' }
                        config.message = '提交成功, 跳转到Kafka执行记录中查看部署详情！'
                        config.offsetY = 80
                        this.$bkMessage(config)
                        this.closeDialog()
                    } else {
                        this.isChecking = false
                        const config = { theme: 'error' }
                        config.message = res.message
                        config.offsetY = 80
                        this.$bkMessage(config)
                    }
                } catch (err) {
                    this.isChecking = false
                    this.$bkMessage({
                        message: err.message ? err.message : err,
                        theme: 'error'
                    })
                }
            },
            async getCc () {
                try {
                    const res = await this.$store.dispatch('kafka/getAppList')
                    this.appList = res.data.info
                } catch (e) {
                    console.error(e)
                }
            },
            beforeSubmit () {
                this.$bkInfo({
                    title: '请确认是否提交任务',
                    subTitle: '待录入集群名称：' + this.formData.cluster_name,
                    confirmFn: () => {
                        this.submitnewclusterForm()
                        return true
                    },
                    cancelFn: () => {
                        this.isChecking = false
                    }
                })
            },
            checkData () {
                this.$refs.validateForm1.validate().then(validator => {
                    this.isChecking = true
                    this.beforeSubmit()
                }, validator => {
                    this.isChecking = false
                })
            },
            clearError () {
                this.$refs.validateForm1.clearError()
            }
        }
    }
</script>

<style lang="postcss">
    .bk-form-radio {
        margin-right: 30px;
    }
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
