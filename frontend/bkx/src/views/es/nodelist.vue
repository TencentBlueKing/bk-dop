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
                            <p>master节点数量: {{ cluster_detail.master_cnt }} </p>
                            <p>data节点数量: {{ cluster_detail.data_cnt }} </p>
                            <p>cold节点数量: {{ cluster_detail.cold_cnt }}</p>
                            <p>协调节点数量: {{ cluster_detail.client_cnt }}</p>
                            <p>http端口: {{ cluster_detail.http_port }}</p>
                        </bk-col>
                    </bk-row>
                    <div slot="footer" class="foot-main">
                        <span><i class="bk-icon icon-edit"></i> 信息修改</span>
                        <span><i class="bk-icon icon-monitors"></i> 集群监控</span>
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
            <bk-row v-show="tab === 'node'">
                <bk-alert class="mb10" type="info" title="目前通过平台录入的集群暂不开放集群管理操作" closable></bk-alert>
                <div class="mb10">
                    <bk-button size="large" :title="'集群扩容'" :disabled="isOpen" :hover-theme="'primary'" @click="addNoteSettings.isShow = true" class="mr10">集群扩容</bk-button>
                    <bk-button size="large" :title="'集群缩容'" :disabled="isOpen" :hover-theme="'primary'" @click="removeNoteSettings.isShow = true" class="mr10">集群缩容</bk-button>
                </div>
                <bk-table :data="tableData" v-bkloading="{ isLoading: textLoading, title: '数据加载中', zIndex: 10 }">
                    <bk-table-column label="业务ID" prop="app_id"></bk-table-column>
                    <bk-table-column label="集群名" prop="cluster_name"></bk-table-column>
                    <bk-table-column label="节点名称" prop="node_name"></bk-table-column>
                    <bk-table-column label="ip" prop="ip"></bk-table-column>
                    <bk-table-column label="节点角色" prop="role"></bk-table-column>
                    <bk-table-column label="版本" prop="version"></bk-table-column>
                    <bk-table-column label="设备类型" prop="device_class"></bk-table-column>
                    <bk-table-column label="硬件信息" prop="hard_memo"></bk-table-column>
                </bk-table>
            </bk-row>
        </bk-container>
        <bk-sideslider
            :is-show.sync="addNoteSettings.isShow"
            :width="800"
            :before-close="beforeClose">
            <div slot="header">{{cluster_detail.cluster_name}}{{ addNoteSettings.title }}</div>
            
            <div class="p20" slot="content">
                <div>
                    <bk-alert style="margin-top: 10px;" type="info" title="1> ES节点添加可支持不同角色的节点添加，目前支持主节，数据节点，冷节点和协调节点的添加" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="2> 待添加的节点都需要绑定你选择的业务上，否则后台检测任务失败" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="3> 部署的机器IP需要先安装gse_agent,具有业务job执行权限" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="4> 待添加的节点必须是新节点，且不存在ES进程，节点的环境目录/data/esenv必须为空，否则部署会失败" closable></bk-alert>
                </div>
                <bk-divider type="dashed" style="margin-top: 50px;">填写待扩容信息</bk-divider>
                <div style="width: 600px; height: 500px ; margin-top: 50px;">
                    <bk-form :label-width="170" :model="addNodeformData" :rules="addNoderules" ref="addNodeForm">
                        <bk-form-item label="待扩容节点的数据角色" :required="true" :property="'role'" :error-display-type="'normal'">
                            <bk-select v-model="addNodeformData.role" searchable>
                                <bk-option v-for="option in addNodeList"
                                    :key="option.id"
                                    :id="option.id"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
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
            :is-show.sync="removeNoteSettings.isShow"
            :width="800"
            :before-close="beforeClose">
            <div slot="header">{{cluster_detail.cluster_name}}{{ removeNoteSettings.title }}</div>
            
            <div class="p20" slot="content">
                <div>
                    <bk-alert style="margin-top: 10px;" type="info" title="1> ES集群缩容目前针对集群节点回收" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="2> 部署的机器IP需要先安装gse_agent,具有业务job执行权限" closable></bk-alert>
                    <bk-alert style="margin-top: 10px;" type="info" title="3> 在保证最小集群规格情况下，请按需选择待缩容的节点" closable></bk-alert>
                </div>
                <bk-divider type="dashed" style="margin-top: 50px;">填写待缩容信息</bk-divider>
                <div style="width: 600px; height: 500px ; margin-top: 50px;">
                    <bk-form :label-width="140" :model="removeNodeformData" :rules="removeNoderules" ref="removeNodeForm">
                        <bk-form-item label="待缩容的节点IP" :required="true" :property="'role'" :error-display-type="'normal'">
                            <bk-select v-model="removeNodeformData.ips" searchable multiple show-select-all display-tag>
                                <bk-option v-for="option in tableData"
                                    :key="option.ip"
                                    :id="option.ip"
                                    :name="option.ip + '  节点角色:[' + option.role + ']'">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                        <bk-form-item>
                            <bk-button ext-cls="mr5" theme="primary" title="提交" @click.stop.prevent="checkData('removeNode')" :loading="isRmChecking">提交</bk-button>
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
        components: {},
        data () {
            return {
                isOpen: false,
                isAddChecking: false,
                isRmChecking: false,
                cluster_detail: {},
                tableData: [],
                textLoading: true,
                tab: 'node',
                panels: [
                    { name: 'broker', label: '节点信息' }
                ],
                addNoteSettings: {
                    isShow: false,
                    title: '集群扩容'
                },
                removeNoteSettings: {
                    isShow: false,
                    title: '集群缩容'
                },
                
                addNodeformData: {
                    cluster_name: '',
                    role: '',
                    ips: ''
                },
                removeNodeformData: {
                    cluster_name: '',
                    ips: ''
                },
                addNodeList: [
                    {
                        id: 'master',
                        name: '主节点(master node)'
                    },
                    {
                        id: 'data',
                        name: '数据节点(data node)'
                    },
                    {
                        id: 'cold',
                        name: '冷节点(cold node)'
                    },
                    {
                        id: 'client',
                        name: '协调节点(client node)'
                    }
                ],
                addNoderules: {
                    role: [
                        {
                            required: true,
                            message: '选择对应的扩容节点角色',
                            trigger: 'blur'
                        }
                    ],
                    ips: [
                        {
                            required: true,
                            message: '填写ip列表',
                            trigger: 'blur'
                        }
                    ]
                },
                removeNoderules: {
                    ips: [
                        {
                            required: true,
                            message: '填写ip列表',
                            trigger: 'blur'
                        }
                    ]
                }
                
            }
        },
        beforeRouteLeave (to, from, next) {
            localStorage.removeItem('condition')
            next()
        },
        mounted () {
            const condition = localStorage.getItem('condition')
            if (condition != null) {
                this.cluster_detail = JSON.parse(condition)
                this.addNodeformData.cluster_name = this.cluster_detail.cluster_name
                this.removeNodeformData.cluster_name = this.cluster_detail.cluster_name
            } else {
                const querydata = this.$route.query.row
                if (querydata.task_type === 10) {
                    // 表示任务记录重试扩容页面跳转过来，需要请求一次集群数据补全页面
                    this.addNoteSettings.isShow = true
                    this.addNodeformData.cluster_name = querydata.cluster_name
                    this.addNodeformData.role = querydata.role
                    if (querydata.role === 'master') {
                        this.addNodeformData.ips = querydata.master_list
                    }
                    if (querydata.role === 'data') {
                        this.addNodeformData.ips = querydata.data_list
                    }
                    if (querydata.role === 'cold') {
                        this.addNodeformData.ips = querydata.cold_list
                    }
                    if (querydata.role === 'client') {
                        this.addNodeformData.ips = querydata.client_list
                    }
                    this.cluster_detail.cluster_name = querydata.cluster_name
                    this.getEsInfo(this.cluster_detail.cluster_name)
                } else if (querydata.task_type === 11) {
                    // 表示任务记录重试扩容页面跳转过来，需要请求一次集群数据补全页面
                    this.removeNoteSettings.isShow = true
                    this.removeNodeformData.cluster_name = querydata.cluster_name
                    this.removeNodeformData.ips = querydata.target_ips
                    this.cluster_detail.cluster_name = querydata.cluster_name
                    this.getEsInfo(this.cluster_detail.cluster_name)
                } else {
                    // 表示集群管理页面跳转过来，不需要请求
                    this.cluster_detail = querydata
                    this.addNodeformData.cluster_name = this.cluster_detail.cluster_name
                    this.removeNodeformData.cluster_name = this.cluster_detail.cluster_name
                }
            }
            
            if (this.cluster_detail.add_type === '平台录入') {
                this.isOpen = true
            }
            this.getEsNodeInfo()
            localStorage.setItem('condition', JSON.stringify(this.cluster_detail))
        },
        methods: {
            closeDialog () {
                this.$router.push(
                    {
                        name: 'esrecord'
                    }
                )
            },
            beforeClose () {
                this.$bkInfo({
                    title: '请确认是否取消离开',
                    subTitle: '离开则丢失目前已填写好的信息',
                    confirmFn: () => {
                        this.addNodeformData.role = ''
                        this.addNodeformData.ips = ''
                        this.removeNodeformData.ips = ''
                        this.addNoteSettings.isShow = false
                        this.removeNoteSettings.isShow = false
                        return true
                    }
                })
            },
            beforeSubmit (val) {
                this.$bkInfo({
                    title: '请确认是否提交任务',
                    subTitle: '待操作集群名称：' + this.cluster_detail.cluster_name,
                    confirmFn: () => {
                        if (val === 'addNode') {
                            this.submitAddNodeData()
                        } else if (val === 'removeNode') {
                            this.submitRmNodeData()
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
                if (val === 'addNode') {
                    this.$refs.addNodeForm.validate().then(validator => {
                        this.isAddChecking = true
                        this.beforeSubmit(val)
                    }, validator => {
                        this.isAddChecking = false
                    })
                } else if (val === 'removeNode') {
                    this.$refs.removeNodeForm.validate().then(validator => {
                        this.isRmChecking = true
                        this.beforeSubmit(val)
                    }, validator => {
                        this.isRmChecking = false
                    })
                }
            },
            async getEsInfo (clusterName) {
                try {
                    const param = { 'cluster_name': clusterName }
                    const res = await this.$store.dispatch('es/getEsData', param)
                    if (res.data.length !== 0) {
                        this.cluster_detail = res.data[0]
                    
                        localStorage.setItem('condition', JSON.stringify(this.cluster_detail))
                    }
                } catch (e) {
                    console.error(e)
                }
            },
            async getEsNodeInfo () {
                try {
                    const param = { 'cluster_name': this.cluster_detail.cluster_name }
                    const res = await this.$store.dispatch('es/getEsNodeInfo', param)
                    this.tableData = res.data
                    this.textLoading = false
                } catch (e) {
                    this.textLoading = false
                    console.error(e)
                }
            },
            
            async submitRmNodeData () {
                try {
                    const res = await this.$store.dispatch('es/reduceNode', this.removeNodeformData)
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
            async submitAddNodeData () {
                try {
                    const res = await this.$store.dispatch('es/addNode', this.addNodeformData)
                    if (res.code === 0) {
                        this.isAddChecking = false
                        const config = { theme: 'success' }
                        config.message = '提交成功, 跳转到ES执行记录中查看部署详情！'
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
