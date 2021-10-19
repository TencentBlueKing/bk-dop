<template>
    
    <div class="main-grid">
        <div>
            <bk-sideslider :is-show.sync="defaultSettings.isShow" :quick-close="true" :width="800">
                <div slot="header">{{ defaultSettings.title }}</div>
                <div class="p20" slot="content">
                   
                    <bk-alert style="margin-top: 10px;" type="info" title="1> 部署hadoop最小集群只需要3台机器,进程可混合部署。需要在生产环境上线则建议根据业务场景情况后部署合适集群"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="2> 待部署集群的所有填入节点都需要绑定你选择的业务上，否则后台检测任务失败"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="3> 用户在选择业务时只能选择在配置平台已有权限的业务"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="4> 一套具有高可用特性的HDFS集群，需要1个NN节点、1个SNN节点、至少3个JN节点"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="5> 必须填写部署zookeeper集群，目的是支撑hadoop高可用特性"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="6> namenode节点和standbynamenode节点,需要部署到不同的IP上"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="7> 部署的机器IP需要先安装gse_agent,具有业务job执行权限"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="8> datanode节点必须大于或等于副本数量"></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="9> HDFS集群默认分块大小：128MB"></bk-alert>
                </div>
            </bk-sideslider>
        </div>
        <div class="wrapper flex">
            
            <bk-container :col="12">
                <bk-form :label-width="180" :model="formData" :rules="rules" ref="validateForm1">
                    <bk-row>
                        <bk-col :span="12">
                            <bk-alert type="info">
                                <bk-button slot="title" text @click="defaultSettings.isShow = true">查看Hadoop集群新建说明指引请点击</bk-button>
                            </bk-alert>
                        </bk-col>
                    </bk-row>
                
                    <bk-row>
                    
                        <bk-col :span="12">
                            <div class="home-card-layout">

                                <div class="card-title">集群部署基本信息</div>
                                <div style="width: 800px">
                                
                                    <bk-form-item label="业务名称" :required="true" :property="'app_id'" :error-display-type="'normal'">
                                        <bk-select v-model="formData.app_id" searchable>
                                            <bk-option v-for="option in appinfo"
                                                :key="option.bk_biz_id"
                                                :id="option.bk_biz_id"
                                                :name="option.bk_biz_name">
                                            </bk-option>
                                        </bk-select>
                                    </bk-form-item>
                                    <bk-form-item label="集群名称" :required="true" :property="'cluster_name'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.cluster_name" :clearable="true" :maxlength="50" :show-word-limit="true"
                                            placeholder="请输入集群名称"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                    <bk-form-item label="版本选择" :required="true" :property="'cluster_version'" :error-display-type="'normal'">
                                        <bk-select v-model="formData.cluster_version" searchable>
                                            <bk-option v-for="option in versionList"
                                                :key="option.id"
                                                :id="option.id"
                                                :name="option.name">
                                            </bk-option>
                                        </bk-select>
                                    </bk-form-item>
                                    <bk-form-item label="集群启动账号" :required="true" :property="'cluster_user'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.cluster_user" :readonly="true" placeholder="请输入集群启动账号，默认是hadoop用户"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>

                                    <bk-form-item label="集群安装目录" :required="true" :property="'base_dir'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.base_dir" :readonly="true" placeholder="请输入集群组件的安装目录，默认存放到/data/hadoop_env下"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                    <bk-form-item label="ssh远程端口" :required="true" :property="'ssh_port'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.ssh_port" placeholder="输入机器远程端口号,默认22"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                
                                </div>
                            
                            </div>
                        </bk-col>
            
                    </bk-row>
                    <bk-row>
                        <bk-col :span="12">
                            <div class="home-card-layout">
                                <div class="card-title">Zookeeper部署集群信息</div>
                                <div style="width: 800px">
                                    
                                    <bk-form-item label="ZooKeeper 访问端口" :required="true" :property="'zookeeperport'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.zookeeperport" :readonly="true" placeholder="请输入zookeeper集群对外访问端口,默认2181">
                                            <p class="mt5 mb0 f12" slot="tip"></p>
                                        </bk-input>
                                    </bk-form-item>
                                    <bk-form-item label="ZooKeeper 节点信息" :required="true" :property="'zookeepernode'" :error-display-type="'normal'">
                                        <bk-input type="textarea" v-model="formData.zookeepernode" placeholder="请输入对应的ZookeeperNode节点IP列表,多个可以用英文逗号或者空格隔开"></bk-input>
                                    </bk-form-item>
                                   
                                </div>
                            </div>
                        </bk-col>
                    </bk-row>
                    <bk-row>
                        <bk-col :span="12">
                            <div class="home-card-layout">
                                <div class="card-title">HDFS部署集群信息</div>
                                <div style="width: 800px">
                               
                                    <bk-form-item label="hdfs白名单路径" :required="true" :property="'hdfs_includes'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.hdfs_includes" :readonly="true" placeholder="请输入hdfs的白名单配置路径"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                    <bk-form-item label="hdfs黑名单路径" :required="true" :property="'hdfs_excludes'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.hdfs_excludes" :readonly="true" placeholder="请输入hdfs的黑名单配置路径"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                    <bk-form-item label="hdfs数据目录" :required="true" :property="'hdfs_dir'" :error-display-type="'normal'">
                                        <bk-input v-model="formData.hdfs_dir" placeholder="请输入hdfs数据盘列表，多个目录可以用英文逗号隔开"></bk-input>
                                        <p class="mt5 mb0 f12" slot="tip"></p>
                                    </bk-form-item>
                                    <bk-form-item label="hdfs副本数量" :required="true" :property="'repl_number'" :error-display-type="'normal'">
                                        <bk-select v-model="formData.repl_number" placeholder="输入副本数量" searchable>
                                            <bk-option v-for="option in replnumberlist"
                                                :key="option.id"
                                                :id="option.id"
                                                :name="option.name">
                                            </bk-option>
                                        </bk-select>
                                    </bk-form-item>
                                    <bk-form-item label="NN 节点信息" :required="true" :property="'namenode'" :error-display-type="'normal'">
                                        <bk-input type="textarea" v-model="formData.namenode" placeholder="请输入NameNode节点IP列表"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item label="SNN 节点信息" :required="true" :property="'standbynamenode'" :error-display-type="'normal'">
                                        <bk-input type="textarea" v-model="formData.standbynamenode" placeholder="请输入StandNameNode节点IP列表"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item label="DN 节点信息" :required="true" :property="'datanode'" :error-display-type="'normal'">
                                        <bk-input type="textarea" v-model="formData.datanode" placeholder="请输入DataNode节点IP列表"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item label="JN 节点信息" :required="true" :property="'journalnode'" :error-display-type="'normal'">
                                        <bk-input type="textarea" v-model="formData.journalnode" placeholder="请输入JournalNode节点IP列表, 至少需要三台机器"></bk-input>
                                    </bk-form-item>
                               
                                </div>
                            </div>
                        </bk-col>
                    </bk-row>
                    <bk-row>
                        <bk-col :span="12">
                            <div class="home-card-layout">
                                <div class="card-title">YRAN集群部署信息</div>
                                <div style="width: 800px">
                               
                                    <bk-form-item label="是否部署YARN集群">
                                        <bk-button
                                            theme="primary"
                                            :outline="true"
                                            icon="plus"
                                            class="mr10"
                                            @click="isDeployYarn = true">
                                            添加YARN信息
                                        </bk-button>
                                        <bk-button
                                            theme="danger"
                                            :outline="true"
                                            icon="minus"
                                            class="mr10"
                                            @click="colseYarnInfo()">
                                            删除YARN信息
                                        </bk-button>
                                    </bk-form-item>
                                    <bk-form-item label="RM 节点信息" v-show="isDeployYarn">
                                        <bk-input type="textarea" v-model="formData.resourcemanagernode" placeholder="请输入ResourceManager节点IP列表"></bk-input>
                                    </bk-form-item>
                                    <bk-form-item label="NM 节点信息" v-show="isDeployYarn">
                                        <bk-input type="textarea" v-model="formData.nodemanagernode" placeholder="请输入NodeManager节点IP列表"></bk-input>
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
                formData: {
                    app_id: '',
                    app: '',
                    cluster_name: '',
                    cluster_version: '',
                    cluster_user: 'hadoop',
                    base_dir: '/data/hadoop_env',
                    hdfs_includes: '/data/hadoop_env/hadoop/etc/hadoop/includes',
                    hdfs_excludes: '/data/hadoop_env/hadoop/etc/hadoop/excludes',
                    hdfs_dir: '',
                    clean_data_force: '',
                    repl_number: '',
                    ssh_port: '',
                    namenode: '',
                    standbynamenode: '',
                    datanode: '',
                    journalnode: '',
                    zookeeperport: '2181',
                    zookeepernode: '',
                    resourcemanagernode: '',
                    nodemanagernode: '',
                    add_type: '1',
                    is_create_bk_monitor: '0',
                    desc: ''
                    
                },
                defaultSettings: {
                    isShow: false,
                    title: 'HDFS集群新建说明'
                },
                isDeployYarn: false,
                versionList: [
                    {
                        id: '2.6.0',
                        name: '2.6.0'
                    },
                    {
                        id: '3.2.0',
                        name: '3.2.0'
                    }
                ],
                appinfo: [],
                replnumberlist: [
                    {
                        id: '1',
                        name: '1'
                    },
                    {
                        id: '2',
                        name: '2'
                    },
                    {
                        id: '3',
                        name: '3'
                    }
                ],
                isChecking: false,
                rules: {
                    app_id: [
                        {
                            required: true,
                            message: '选择对应业务',
                            trigger: 'blur'
                        }
                    ],
                    cluster_name: [
                        {
                            required: true,
                            message: '必填项',
                            trigger: 'blur'
                        },
                        {
                            min: 3,
                            message: function (val) {
                                return `${val}不能小于3个字符`
                            },
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: '不能多于50个字符',
                            trigger: 'blur'
                        },
                        {
                            regex: /^[A-Za-z0-9]+$/,
                            message: '不能存在特殊符号',
                            trigger: 'blur'
                        }
                        
                    ],
                    cluster_version: [
                        {
                            required: true,
                            message: '选择对应的安装版本',
                            trigger: 'blur'
                        }
                    ],
                    cluster_user: [
                        {
                            required: true,
                            message: '选择对应的部署用户',
                            trigger: 'blur'
                        },
                        {
                            regex: /^[A-Za-z0-9]+$/,
                            message: '不能存在特殊符号',
                            trigger: 'blur'
                        }
                    ],
                    base_dir: [
                        {
                            required: true,
                            message: '输入安装目录，只能输入一个目录',
                            trigger: 'blur'
                        },
                        {
                            regex: /^\/[\w-.\/?]+$/,
                            message: '输入正确绝对路径表达方式，如: /xxxx/xxxx/，目录名称支持数字+字符+下划线+中划线组合',
                            trigger: 'blur'
                        }
                    ],
                    hdfs_includes: [
                        {
                            required: true,
                            message: '输入安装目录，只能输入一个目录',
                            trigger: 'blur'
                        },
                        {
                            regex: /^\/[\w-.\/?]+$/,
                            message: '输入正确绝对路径表达方式，如: /xxxx/xxxx/，目录名称支持数字+字符+下划线+中划线+点号组合',
                            trigger: 'blur'
                        }
                    ],
                    hdfs_excludes: [
                        {
                            required: true,
                            message: '输入安装目录，只能输入一个目录',
                            trigger: 'blur'
                        },
                        {
                            regex: /^\/[\w-.\/?]+$/,
                            message: '输入正确绝对路径表达方式，如: /xxxx/xxxx/，目录名称支持数字+字符+下划线+中划线+点号组合',
                            trigger: 'blur'
                        }
                    ],
                    hdfs_dir: [
                        {
                            required: true,
                            message: '输入hdfs数据存储目录',
                            trigger: 'blur'
                        }
                    ],
                    repl_number: [
                        {
                            required: true,
                            message: '输入hdfs文件副本数',
                            trigger: 'blur'
                        }
                    ],
                    ssh_port: [
                        {
                            required: true,
                            message: '输入远程端口号',
                            trigger: 'blur'
                        },
                        {
                            regex: /^([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$/,
                            message: '输入标准端口号访问：1-65535',
                            trigger: 'blur'
                        }
                    ],
                    namenode: [
                        {
                            required: true,
                            message: '请输入namenode',
                            trigger: 'blur'
                        }
                    ],
                    standbynamenode: [
                        {
                            required: true,
                            message: '请输入standbynamenode',
                            trigger: 'blur'
                        }
                    ],
                    datanode: [
                        {
                            required: true,
                            message: '请输入datanode',
                            trigger: 'blur'
                        }
                    ],
                    journalnode: [
                        {
                            required: true,
                            message: '请输入journalnode',
                            trigger: 'blur'
                        }
                    ],
                    zookeeperport: [
                        {
                            required: true,
                            message: '输入zookeeper端口号',
                            trigger: 'blur'
                        },
                        {
                            regex: /^([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$/,
                            message: '输入标准端口号访问：1-65535',
                            trigger: 'blur'
                        }
                    ],
                    zookeepernode: [
                        {
                            required: true,
                            message: '请输入zookeepernode',
                            trigger: 'blur'
                        }
                    ]

                }
            }
        },
        watch: {
            'formData.app_id': function (val) {
                this.formData.app_id = val
                this.appinfo.forEach(item => {
                    if (this.formData.app_id === item.bk_biz_id) {
                        this.formData.app = item.bk_biz_name
                        return true
                    }
                }
                )
            }
        },
        created () {
            this.getInfoData()
            if (this.$route.query.row) {
                const querydata = JSON.parse(this.$route.query.row)
                this.formData.app = querydata.app
                this.formData.app_id = querydata.app_id
                this.formData.cluster_name = querydata.cluster_name
                this.formData.cluster_user = querydata.cluster_user
                this.formData.cluster_version = querydata.cluster_version
                this.formData.hdfs_dir = querydata.data_disk_dir_list
                this.formData.namenode = querydata.namenode
                this.formData.standbynamenode = querydata.standbynamenode
                this.formData.datanode = querydata.datanode
                this.formData.journalnode = querydata.journalnode
                this.formData.is_create_bk_monitor = querydata.is_create_bk_monitor.toString()
                if (querydata.zookeeperport) {
                    this.formData.zookeeperport = querydata.zookeeperport
                }
                
                this.formData.zookeepernode = querydata.zookeepernode
                this.formData.repl_number = querydata.replication_number
                this.formData.ssh_port = querydata.ssh_port
                if (querydata.resourcemanager.length !== 0 || querydata.nodemanager.length !== 0) {
                    this.formData.resourcemanagernode = querydata.resourcemanager
                    this.formData.nodemanagernode = querydata.nodemanager
                    this.isDeployYarn = true
                }
            }
        },
        methods: {
            colseYarnInfo () {
                this.isDeployYarn = false
                this.formData.resourcemanagernode = ''
                this.formData.nodemanagernode = ''
            },
            closeDialog () {
                this.$router.push(
                    {
                        path: 'hadooprecord'
                    }
                )
            },
            async getInfoData () {
                try {
                    const res = await this.$store.dispatch('hadoop/getAppInfoData', {}, { fromCache: true })
                    this.appinfo = res.data.info
                } catch (e) {
                    console.error(e)
                }
            },
            async submitData () {
                try {
                    const res = await this.$store.dispatch('hadoop/createHadoopCluster', this.formData)
                    if (res.code === 0) {
                        this.isChecking = false
                        const config = { theme: 'success' }
                        config.message = '提交成功, 跳转到HDFS执行记录中查看部署详情！'
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
                } catch (e) {
                    this.isChecking = false
                    console.log(e)
                }
            },
            beforeSubmit () {
                this.$bkInfo({
                    title: '请确认是否提交任务',
                    subTitle: '待部署集群名称：' + this.formData.cluster_name,
                    confirmFn: () => {
                        this.submitData()
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
