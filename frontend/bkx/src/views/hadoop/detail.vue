<template>
    <div class="wrapper">
        <bk-container :col="2">
            <bk-row>
                <bk-card title="集群信息" :is-collapse="true" :show-foot="true" :position="'right'">
                    <bk-row>
                        <bk-col :span="1">
                            <p>集群名称: {{ cluster_detail.cluster_name }}</p>
                            <p>集群版本: {{ cluster_detail.cluster_version }}</p>
                            <p>集群状态: {{ cluster_detail.cluster_status }}</p>
                            <p>添加模式: {{ cluster_detail.add_type }}</p>
                            <p>启动用户: {{ cluster_detail.cluster_user }} </p>
                        </bk-col>
                        <bk-col :span="1">
                            <p>安装目录: {{ cluster_detail.base_dir }} </p>
                            <p>数据目录: {{ cluster_detail.hdfs_data_dir }}</p>
                            <p>副本设置: {{ cluster_detail.hdfs_repl_num }}</p>
                            <p>远程端口: {{ cluster_detail.ssh_port }}</p>
                            <p>hdfs白名单路径: {{ cluster_detail.hdfs_includes }}</p>
                            <p>hdfs黑名单路径: {{ cluster_detail.hdfs_excludes }}</p>
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
                <bk-tab :active.sync="active" type="unborder-card" :before-toggle="getHadoopDetail">
                    <bk-tab-panel
                        v-for="(panel, index) in panels"
                        v-bind="panel"
                        :key="index">
                    </bk-tab-panel>
                </bk-tab>
            </bk-row>
            
            <bk-row>
                <bk-alert class="mb10" type="info" title="目前通过平台录入的集群暂不开放集群管理操作" closable></bk-alert>
                <div class="mb10">
                    <bk-button size="large" :title="'集群扩容'" :disabled="isOpen" :hover-theme="'primary'" @click="addSettings.isShow = true" class="mr10">集群扩容</bk-button>
                    <bk-button size="large" :title="'集群缩容'" :disabled="isOpen" :hover-theme="'primary'" @click="removeSettings.isShow = true" class="mr10">集群缩容</bk-button>
                </div>
                <bk-table :data="data" v-bkloading="{ isLoading: textLoading, title: '数据加载中', zIndex: 10 }">
                    <bk-table-column label="进程名称" prop="process_name" sortable></bk-table-column>
                    <bk-table-column label="进程ip" prop="process_ip"></bk-table-column>
                    <bk-table-column label="进程域名" prop="process_hostname"></bk-table-column>
                    <bk-table-column label="进程版本" prop="package_version"></bk-table-column>
                    <bk-table-column label="进程状态" prop="process_status"></bk-table-column>
                    <bk-table-column label="创建时间" prop="create_time"></bk-table-column>
                </bk-table>
            
            </bk-row>
        </bk-container>
        <bk-sideslider
            :is-show.sync="addSettings.isShow"
            :width="800"
            :before-close="beforeClose">
            <div slot="header">{{cluster_detail.cluster_name}}{{ addSettings.title }}：{{ panelNameNow }}</div>
            
            <div class="p20" slot="content">
                <div>
                    <bk-alert style="margin-top: 10px;" type="info" title="1> HDFS集群目前提供两种扩容方式：DN节点扩容、多目录(磁盘)扩容" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="2> 选择DN节点扩容时，待添加IP节点必须不存在有DN进程，否则扩容时检测到异常。机器可支持进程混部" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="3> 选择多目录(磁盘)扩容时，待添加目录路径在所有DN节点机器上都必须存在" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="4> 扩容后不做rebanlance操作，如需要数据平衡则人为评估后手动操作" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="5> 待添加的节点都需要绑定你选择的业务上，否则后台检测任务失败" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="6> 部署的机器IP需要先安装gse_agent,具有业务job执行权限" closable></bk-alert>
                </div>
                <bk-divider type="dashed" style="margin-top: 50px;">填写待扩容信息</bk-divider>
                <div style="width: 600px; height: 500px ; margin-top: 50px;">
                    <bk-form :label-width="120" :model="addformData" :rules="addrules" ref="addForm">
                        <bk-form-item label="扩容模式" :required="true" :property="'op_type'" :error-display-type="'normal'">
                            <div class="bk-button-group">
                                <bk-button @click="addformData.op_type = 'add_datanode'" :class="addformData.op_type === 'add_datanode' ? 'is-selected' : ''">DN节点扩容</bk-button>
                                <bk-button @click="addformData.op_type = 'add_dir'" :class="addformData.op_type === 'add_dir' ? 'is-selected' : ''">DN目录扩容</bk-button>
                                            
                            </div>
                        </bk-form-item>

                        <bk-form-item label="扩容目录路径" :required="true" :property="'data_dir'" :error-display-type="'normal'" v-if="addformData.op_type === 'add_dir'">
                            <bk-input type="textarea" v-model="addformData.data_dir" placeholder="合法已存在目录，多个用英文逗号隔开"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="扩容IP列表" :required="true" :property="'ips'" :error-display-type="'normal'" v-if="addformData.op_type === 'add_datanode'">
                            <bk-input type="textarea" v-model="addformData.ips" placeholder="待扩容的ip列表，多个用英文逗号隔开"></bk-input>
                        </bk-form-item>
                        <bk-form-item>
                            <bk-form-item>
                                <bk-button ext-cls="mr5" theme="primary" title="提交" @click.stop.prevent="checkData('add')" :loading="isAddChecking">提交</bk-button>
                                <bk-button ext-cls="mr5" theme="default" title="取消" @click="beforeClose">取消</bk-button>
                            </bk-form-item>
                        </bk-form-item>
                    </bk-form>

                </div>
            </div>
            
        </bk-sideslider>
        <bk-sideslider
            :is-show.sync="removeSettings.isShow"
            :width="800"
            :before-close="beforeClose">
            <div slot="header">{{cluster_detail.cluster_name}}{{ removeSettings.title }}：{{ panelNameNow }}</div>
            
            <div class="p20" slot="content">
                <div>
                    <bk-alert style="margin-top: 10px;" type="info" title="1> HDFS集群目前提供一种扩容方式：DN集群缩容，一次会回收多个DN节点，前提条件缩容后剩余的DN节点数量不能少于集群设置的副本数" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="2> 缩容后不做rebanlance操作，如需要数据平衡则人为评估后手动操作" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="3> 部署的机器IP需要先安装gse_agent,具有业务job执行权限" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="4> 在保证最小集群规格情况下，请按需选择待缩容的节点" closable></bk-alert>
                </div>
                <bk-divider type="dashed" style="margin-top: 50px;">填写待缩容信息</bk-divider>
                <div style="width: 600px; height: 500px ; margin-top: 50px;">
                    <bk-form :label-width="140" :model="removeformData" :rules="removerules" ref="removeForm">
                        <bk-form-item label="待缩容的节点IP" :required="true" :property="'process_id_list'" :error-display-type="'normal'">
                            <bk-select v-model="removeformData.process_id_list" searchable multiple display-tag>
                                <bk-option v-for="option in data" v-show="option.process_name === 'DataNode'"
                                    :key="option.process_id"
                                    :id="option.process_id"
                                    :name="option.process_ip + '  节点角色:[' + option.process_name + ']' + ' 节点状态:[' + option.process_status + ']' ">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                        <bk-form-item>
                            <bk-button ext-cls="mr5" theme="primary" title="提交" @click.stop.prevent="checkData('remove')" :loading="isRmChecking">提交</bk-button>
                            <bk-button ext-cls="mr5" theme="default" title="取消" @click="beforeClose">取消</bk-button>
                        </bk-form-item>
                    </bk-form>

                </div>
            </div>
            
        </bk-sideslider>
    </div>
</template>

<script>
    export default {
        data () {
            return {
                // id: '',
                isOpen: false,
                isAddChecking: false,
                isRmChecking: false,
                cluster_detail: {},
                data: [],
                panels: [
                    { name: 'hdfs', label: 'HDFS节点信息' },
                    { name: 'yarn', label: 'YARN节点信息' }
                ],
                panelNameNow: '',
                active: 'mission',
                textLoading: true,
                addSettings: {
                    isShow: false,
                    title: '集群扩容'
                },
                removeSettings: {
                    isShow: false,
                    title: '集群缩容'
                },
                
                addformData: {
                    cluster_id: '',
                    op_type: 'add_datanode',
                    ips: '',
                    data_dir: '',
                    clean_data_force: ''
                },
                removeformData: {
                    cluster_id: '',
                    op_type: 'recycle_datanode',
                    process_id_list: []
                },
                addrules: {
                    op_type: [
                        {
                            required: true,
                            message: '选择对应的扩容模式',
                            trigger: 'blur'
                        }
                    ],
                    ips: [
                        {
                            required: true,
                            message: '填写待扩容的IP列表',
                            trigger: 'blur'
                        }
                    ],
                    data_dir: [
                        {
                            required: true,
                            message: '填写待扩容的绝对路径',
                            trigger: 'blur'
                        }
                    ]

                },
                removerules: {
                    process_id_list: [
                        {
                            required: true,
                            message: '选择对应下线IP',
                            trigger: 'blur'
                        }
                    ]
                }
                
            }
        },
        beforeRouteLeave (to, from, next) {
            if (to.name === 'hadoopmonitor') {
                next()
            } else {
                localStorage.removeItem('hadoop_condition')
                next()
            }
        },
        mounted () {
            const condition = localStorage.getItem('hadoop_condition')
            if (condition != null) {
                this.cluster_detail = JSON.parse(condition)
                this.addformData.cluster_id = this.cluster_detail.cluster_id
                this.removeformData.cluster_id = this.cluster_detail.cluster_id
            } else {
                const querydata = this.$route.query.row
                if (querydata.task_type === 4) {
                    // 表示任务记录重试DN扩容页面跳转过来，需要请求一次集群数据补全页面
                    this.addSettings.isShow = true
                    this.addformData.ips = querydata.scaled_up_ip_list
                    this.addformData.op_type = 'add_datanode'
                    this.addformData.cluster_id = querydata.cluster_id
                    this.removeformData.cluster_id = querydata.cluster_id
                    this.cluster_detail.cluster_id = querydata.cluster_id
                    this.getHadoopData(querydata.cluster_name)
                } else if (querydata.task_type === 8) {
                    // 表示任务记录重试目录扩容页面跳转过来，需要请求一次集群数据补全页面
                    this.addSettings.isShow = true
                    this.addformData.data_dir = querydata.scaled_up_dir_list
                    this.addformData.op_type = 'add_dir'
                    this.addformData.cluster_id = querydata.cluster_id
                    this.removeformData.cluster_id = querydata.cluster_id
                    this.cluster_detail.cluster_id = querydata.cluster_id
                    this.getHadoopData(querydata.cluster_name)
                } else if (querydata.task_type === 5) {
                    // 表示任务记录重试DN缩容页面跳转过来，需要请求一次集群数据补全页面
                    this.removeSettings.isShow = true
                    this.removeformData.process_id_list = querydata.process_id_list
                    this.addformData.cluster_id = querydata.cluster_id
                    this.removeformData.cluster_id = querydata.cluster_id
                    this.cluster_detail.cluster_id = querydata.cluster_id
                    this.getHadoopData(querydata.cluster_name)
                } else {
                    // 表示集群管理页面跳转过来，不需要请求
                    this.cluster_detail = this.$route.query.row
                    this.addformData.cluster_id = this.cluster_detail.cluster_id
                    this.removeformData.cluster_id = this.cluster_detail.cluster_id
                }
            }
            if (typeof (this.cluster_detail) === 'object' && this.cluster_detail.cluster_name !== '') {
                this.getHadoopDetail('hdfs')
                localStorage.setItem('hadoop_condition', JSON.stringify(this.cluster_detail))
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
        },
        methods: {
            closeDialog () {
                this.$router.push(
                    {
                        name: 'hadooprecord'
                    }
                )
            },
            monitor () {
                this.$router.push({
                    name: 'hadoopmonitor', query: { 'row': this.cluster_detail }
                })
            },
            beforeClose () {
                this.$bkInfo({
                    title: '请确认是否取消离开',
                    subTitle: '离开则丢失目前已填写好的信息',
                    confirmFn: () => {
                        this.addformData.op_type = 'add_datanode'
                        this.addformData.ips = ''
                        this.addformData.data_dir = ''
                        this.addSettings.isShow = false

                        this.removeformData.process_id_list = []
                        this.removeSettings.isShow = false
                        return true
                    }
                })
            },
            beforeSubmit (val) {
                this.$bkInfo({
                    title: '请确认是否提交任务',
                    subTitle: '待操作集群名称：' + this.cluster_detail.cluster_name,
                    confirmFn: () => {
                        if (val === 'add') {
                            this.submitAddData()
                        } else if (val === 'remove') {
                            this.submitRmData()
                        }
                        return true
                    },
                    cancelFn: () => {
                        this.isRmChecking = false
                        this.isAddChecking = false
                    }
                })
            },
            checkData (val) {
                if (val === 'add') {
                    this.$refs.addForm.validate().then(validator => {
                        this.isAddChecking = true
                        this.beforeSubmit(val)
                    }, validator => {
                        this.isAddChecking = false
                    })
                } else if (val === 'remove') {
                    this.$refs.removeForm.validate().then(validator => {
                        this.isRmChecking = true
                        this.beforeSubmit(val)
                    }, validator => {
                        this.isRmChecking = false
                    })
                }
            },
            async getHadoopData (clusterName) {
                console.log(clusterName)
                const param = { 'cluster_name': clusterName }
                try {
                    const res = await this.$store.dispatch('hadoop/getHadoopData', param)
                    if (res.data.length !== 0) {
                        this.cluster_detail = res.data[0]
                        localStorage.setItem('hadoop_condition', JSON.stringify(this.cluster_detail))
                    }
                } catch (e) {
                    console.error(e)
                }
            },
            async getHadoopDetail (panelName) {
                try {
                    this.textLoading = true
                    this.isOpen = true
                    this.panelNameNow = panelName
                    if (panelName === 'hdfs' && this.cluster_detail.add_type !== '平台录入') {
                        this.isOpen = false
                    }
                    const param = { 'cluster_id': this.cluster_detail.cluster_id, 'hadoop_group_name': panelName }
                    const res = await this.$store.dispatch('hadoop/getHadoopDetail', param)
                    this.data = res.data
                    this.textLoading = false
                } catch (e) {
                    this.textLoading = false
                    console.error(e)
                }
                return panelName
            },
            async submitRmData () {
                console.log(this.removeformData)
                try {
                    const res = await this.$store.dispatch('hadoop/removeDataNode', this.removeformData)
                    if (res.code === 0) {
                        this.isRmChecking = false
                        const config = { theme: 'success' }
                        config.message = '提交成功, 跳转到ES执行记录中查看部署详情！'
                        config.offsetY = 80
                        this.$bkMessage(config)
                        this.closeDialog()
                    } else {
                        this.isRmChecking = false
                        const config = { theme: 'error' }
                        config.message = res.message
                        config.offsetY = 80
                        this.$bkMessage(config)
                    }
                } catch (e) {
                    this.isRmChecking = false
                    console.log(e)
                }
            },
            async submitAddData () {
                try {
                    let url = ''
                    if (this.addformData.op_type === 'add_datanode') {
                        url = 'hadoop/addDataNode'
                    } else {
                        url = 'hadoop/addDir'
                    }
                    const res = await this.$store.dispatch(url, this.addformData)
                    if (res.code === 0) {
                        this.isAddChecking = false
                        const config = { theme: 'success' }
                        config.message = '提交成功, 跳转到HDFS执行记录中查看扩容详情！'
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
