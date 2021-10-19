<template>
    
    <div class="main-grid">
        <div>
            <bk-sideslider :is-show.sync="defaultSettings.isShow" :quick-close="true" :width="800">
                <div slot="header">{{ defaultSettings.title }}</div>
                <div class="p20" slot="content">
                   
                    <bk-alert style="margin-top: 10px;" type="info" title="1> ES集群录入目前只支持手动录入模式，根据录入的ES集群的URL来识别集群信息，同步到平台"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="2> 待录入的集群所有节点都需要绑定你选择的业务上，否则后台录入时会出现异常"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="3> 用户选择业务时只能选择在配置平台已有权限的业务"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="4> 出于安全考虑，平台暂不支持对待录入集群的密码保存"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="5> 部署的机器IP需要先安装gse_agent,具有业务job执行权限"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="6> 录入的集群暂不支持扩容或缩容等运维功能。"></bk-alert>
                
                </div>
            </bk-sideslider>
        </div>
        <div class="wrapper flex">
            
            <bk-container :col="12">
                <bk-form :label-width="180" :model="formData" :rules="rules" ref="validateForm1">
                    <bk-row>
                        <bk-col :span="12">
                            <bk-alert type="info">
                                <bk-button slot="title" text @click="defaultSettings.isShow = true">查看ES集群录入说明指引请点击</bk-button>
                            </bk-alert>
                        </bk-col>
                    </bk-row>
                
                    <bk-row>
                    
                        <bk-col :span="12">
                            <div class="home-card-layout">

                                <div class="card-title">待录入集群基本信息</div>
                                <div style="width: 800px">
                                
                                    <bk-form-item label="业务名称" :required="true" :property="'app'" :error-display-type="'normal'">
                                        <bk-select v-model="formData.app_id" searchable placeholder="请选择对应的业务名称">
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
                                    <bk-form-item label="ES集群httpUrl" :required="true" :property="'input_http_url'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.input_http_url" placeholder="请输入集群的url（非域名），用户获取es的集群状态信息">
                                            <template slot="prepend">
                                                <div class="group-text">http://</div>
                                            </template>
                                        </bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                    <bk-form-item label="集群版本" :required="true" :property="'version'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.version" placeholder="请输入对应的版本编号，输入格式：0.0.0"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
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
                                <div class="card-title">待录入集群账号密码信息</div>
                                <div style="width: 800px">
                                    <bk-form-item label="是否输入集群账号">
                                        <bk-button
                                            theme="primary"
                                            :outline="true"
                                            icon="plus"
                                            class="mr10"
                                            @click="isUser = true">
                                            添加账号信息
                                        </bk-button>
                                        <bk-button
                                            theme="danger"
                                            :outline="true"
                                            icon="minus"
                                            class="mr10"
                                            @click="closeUserInfo()">
                                            删除账号信息
                                        </bk-button>
                                    </bk-form-item>
                                    <bk-form-item label="用户名" v-show="isUser">
                                        <bk-input v-model="formData.account" placeholder="若存在登录账号，则填写登录账号"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                    <bk-form-item label="密码" v-show="isUser">
                                        <bk-input v-model="formData.password" :type="'password'" placeholder="填写登录账号密码"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
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
        
        data () {
            return {
                defaultSettings: {
                    isShow: false,
                    title: 'ES集群录入说明'
                },
                formData: {
                    cluster_name: '',
                    input_http_url: '',
                    version: '',
                    description: '',
                    app: '',
                    app_id: '',
                    account: '',
                    password: ''
                },
                submitLoading: false,
                appList: [],
                isChecking: false,
                isUser: false,
                rules: {
                    cluster_name: [
                        {
                            required: true,
                            pattern: /^[a-z0-9]+[a-z0-9-]+[a-z0-9]+$/,
                            message: '请输入集群名称(只能包含小写字母，数字，-)',
                            trigger: 'change'
                        },
                        { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'change' }
                        
                    ],
                    input_http_url: [
                        {
                            required: true,
                            message: '请输入正确的url地址',
                            trigger: 'change'
                        }
                    ],
                    version: [
                        {
                            required: true,
                            message: '版本不能为空',
                            trigger: 'change'
                        }
                    ],
                    app: [
                        {
                            required: true,
                            message: '请选择对应的业务名称',
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
                this.formData.app = querydata.app
                this.formData.app_id = querydata.app_id
                this.formData.cluster_name = querydata.cluster_name
                this.formData.input_http_url = querydata.input_http_url
                this.formData.version = querydata.version
                if (querydata.account !== '') {
                    this.formData.account = querydata.account
                    this.isUser = true
                }
                this.formData.description = querydata.description
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
            closeUserInfo () {
                this.isUser = false
                this.formData.account = ''
                this.formData.password = ''
            },
            async submitnewclusterForm () {
                try {
                    const res = await this.$store.dispatch('es/inputEsCluster', this.formData)
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
