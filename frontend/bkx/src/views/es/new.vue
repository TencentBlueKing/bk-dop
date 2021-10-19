<template>
    
    <div class="main-grid">
        <div>
            <bk-sideslider :is-show.sync="defaultSettings.isShow" :quick-close="true" :width="800">
                <div slot="header">{{ defaultSettings.title }}</div>
                <div class="p20" slot="content">
                   
                    <bk-alert style="margin-top: 10px;" type="info" title="1> ES集群部署分别有混部模式和独立模式，不同部署模式具有不同标准，建议开发环境中使用混部模式部署，正式环境中使用独立模式部署"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="2> 待部署集群的所有填入节点都需要绑定你选择的业务上，否则后台检测任务失败"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="3> 用户在选择业务时只能选择在配置平台已有权限的业务"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="4> 混部模式表示ES实例可以负责多个核心节点角色，至少需要一台机器，一台机器只部署一个ES实例"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="5> 独立模式表示ES实例只能负责一个核心节点角色，一台机器只部署一个ES实例，最小集群标准需要5台机器：3台master node，2台data node"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="6> 请记住创建时的账号及密码，出于安全考虑，平台暂不支持密码保存"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="7> 部署的机器IP需要先安装gse_agent,具有业务job执行权限"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="8> 平台创建默认启动安全模式，需要初始化集群admin权限账号以及密码"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="9> 部署的节点必须是新加节点，且不存在ES进程，节点的环境目录/data/esenv必须为空，否则部署会失败"></bk-alert>
                    
                </div>
            </bk-sideslider>
        </div>
        <div class="wrapper flex">
            
            <bk-container :col="12">
                <bk-form :label-width="180" :model="formData" :rules="rules" ref="validateForm1">
                    <bk-row>
                        <bk-col :span="12">
                            <bk-alert type="info">
                                <bk-button slot="title" text @click="defaultSettings.isShow = true">查看ES集群创建说明指引请点击</bk-button>
                            </bk-alert>
                        </bk-col>
                    </bk-row>
                
                    <bk-row>
                    
                        <bk-col :span="12">
                            <div class="home-card-layout">

                                <div class="card-title">集群部署基本信息</div>
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
                                    <bk-form-item label="ES HTTP端口" :required="true" :property="'http_port'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.http_port" placeholder="请输入端口号 端口访问: 1-65535"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                    <bk-form-item label="版本选择" :required="true" :property="'version'" :error-display-type="'normal'">
                                        <bk-select v-model="formData.version" searchable>
                                            <bk-option v-for="option in versionList"
                                                :key="option.id"
                                                :id="option.id"
                                                :name="option.name">
                                            </bk-option>
                                        </bk-select>
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
                                <div class="card-title">集群账号密码初始化设置</div>
                                <div style="width: 800px">
                                    
                                    <bk-form-item label="用户名" :required="true" :property="'account'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.account" placeholder="请输入访问ES的账号，集群创建之后建立"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                    <bk-form-item label="密码" :required="true" :property="'password'" :error-display-type="'normal'">
                                        <bk-input :type="'password'" v-model="formData.password" placeholder="请输入访问ES的密码"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                   
                                </div>
                            </div>
                        </bk-col>
                    </bk-row>
                    <bk-row>
                        <bk-col :span="12">
                            <div class="home-card-layout">
                                <div class="card-title">集群部署选择</div>
                                <div style="width: 800px">
                                    
                                    <bk-form-item label="集群模式" :required="true" :property="'spec'" :error-display-type="'normal'">
                                        <div class="bk-button-group">
                                            <bk-button @click="formData.spec = 'mixed'" :class="formData.spec === 'mixed' ? 'is-selected' : ''">混部模式</bk-button>
                                            <bk-button @click="formData.spec = 'dedicated'" :class="formData.spec === 'dedicated' ? 'is-selected' : ''">独立模式</bk-button>
                                            
                                        </div>
                                    </bk-form-item>
                                    <bk-form-item label="master node" :required="true" :property="'master_list'" :error-display-type="'normal'">
                                        <bk-input type="textarea" v-model="formData.master_list" placeholder="请输入主节点IP列表，用英文逗号或者空行隔开"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item v-if="formData.spec === 'dedicated'" label="data node" :required="true" :property="'data_list'" :error-display-type="'normal'">
                                        <bk-input type="textarea" v-model="formData.data_list" placeholder="请输入数据节点IP列表，用英文逗号或者空行隔开"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item v-if="formData.spec === 'dedicated'" label="cold node" :property="'cold_list'">
                                        <bk-input type="textarea" v-model="formData.cold_list" placeholder="请输冷节点IP列表，用英文逗号或者空行隔开"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item v-if="formData.spec === 'dedicated'" label="client node" :property="'client_list'">
                                        <bk-input type="textarea" v-model="formData.client_list" placeholder="请输入协调节点IP列表，用英文逗号或者空行隔开"></bk-input>
                                    </bk-form-item>
                    
                                </div>
                            </div>
                        </bk-col>
                    </bk-row>
                    <bk-row>
                        <bk-col :span="12">
                        
                            <bk-form-item>
                                <bk-button ext-cls="mr5" theme="primary" title="提交" :loading="isChecking" @click.stop.prevent="checkData">提交</bk-button>
                                <bk-button ext-cls="mr5" theme="default" title="取消">取消</bk-button>
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
        components: {

        },
        data () {
            return {
                defaultSettings: {
                    isShow: false,
                    title: 'ES集群创建说明'
                },
                formData: {
                    cluster_name: '',
                    version: '',
                    master_list: '',
                    data_list: '',
                    cold_list: '',
                    client_list: '',
                    http_port: '9200',
                    description: '',
                    app: '',
                    app_id: '',
                    account: '',
                    password: '',
                    spec: 'mixed'
                },
                appList: [],
                versionList: [
                    // {
                    //     id: '5.4.0',
                    //     name: '5.4.0'
                    // },
                    {
                        id: '7.10.0',
                        name: '7.10.0'
                    }
                    // {
                    //     id: '6.8.1',
                    //     name: '6.8.1(暂不支持)'
                    // }
                ],
                isChecking: false,
                rules: {
                
                    cluster_name: [
                        {
                            required: true,
                            message: '请输入集群名称',
                            trigger: 'blur'
                        },
                        {
                            regex: /^[a-z0-9]+[a-z0-9-]+[a-z0-9]+$/,
                            message: '只能包含小写字母，数字，-, 长度不少于3',
                            trigger: 'change'
                        }
                    ],
                    version: [
                        {
                            required: true,
                            message: '请选择版本',
                            trigger: 'change'
                        }
                    ],
                    master_list: [
                        {
                            required: true,
                            message: '请输入作为master的IP列表',
                            trigger: 'change'
                        }
                    ],
                    data_list: [
                        {
                            required: true,
                            message: '请输入作为数据节点的IP列表',
                            trigger: 'blur'
                        }
                    ],
                    account: [
                        {
                            required: true,
                            message: '请输入集群初始用户名称',
                            trigger: 'change'
                        }
                    ],
                    password: [
                        {
                            required: true,
                            message: '请输入集群初始用户密码',
                            trigger: 'change'
                        }
                    ],
                    app: [
                        {
                            required: true,
                            message: '请选择对应的业务名称',
                            trigger: 'change'
                        }
                    ],
                    http_port: [
                        {
                            required: true,
                            message: '输入ES HTTP访问端口',
                            trigger: 'blur'
                        },
                        {
                            regex: /^([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$/,
                            message: '输入标准端口号访问：1-65535',
                            trigger: 'blur'
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
            console.log(require('process'))
            this.getCc()
            if (this.$route.query.row) {
                const querydata = JSON.parse(this.$route.query.row)
                this.formData.app = querydata.app
                this.formData.app_id = querydata.app_id
                this.formData.cluster_name = querydata.cluster_name
                this.formData.http_port = querydata.http_port
                this.formData.version = querydata.version
                this.formData.master_list = querydata.master_list
                this.formData.data_list = querydata.data_list
                this.formData.cold_list = querydata.cold_list
                this.formData.client_list = querydata.client_list
                this.formData.account = querydata.account
                this.formData.description = querydata.description
                if (querydata.spec) {
                    this.formData.spec = querydata.spec
                } else {
                    this.formData.spec = 'dedicated'
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
            async submitnewclusterForm () {
                try {
                    const res = await this.$store.dispatch('es/createEsCluster', this.formData)
                    if (res.code === 0) {
                        this.isChecking = false
                        const config = { theme: 'success' }
                        config.message = '提交成功, 跳转到ES执行记录中查看部署详情！'
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
                    const res = await this.$store.dispatch('es/getAppList')
                    this.appList = res.data.info
                } catch (e) {
                    console.error(e)
                }
            },
            beforeSubmit () {
                this.$bkInfo({
                    title: '请确认是否提交任务',
                    subTitle: '待部署集群名称：' + this.formData.cluster_name,
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
