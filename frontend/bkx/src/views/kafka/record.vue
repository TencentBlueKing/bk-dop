<template>
    <div class="example1-wrapper">

        <bk-dialog v-model="revoketask.primary.visible"
            theme="primary"
            :mask-close="true"
            :header-position="revoketask.primary.headerPosition"
            @confirm="optask(revoketask.id, 'revoke')"
            title="撤销任务">
            <p><small>流程ID : {{ revoketask.id }}</small></p>
            <p><small>撤销任务后任务不再被调用，是否确认?</small></p>
        </bk-dialog>

        <bk-dialog v-model="pausetask.primary.visible"
            theme="primary"
            :mask-close="true"
            :header-position="pausetask.primary.headerPosition"
            @confirm="optask(pausetask.id, 'pause')"
            title="暂停任务">
            <p><small>流程ID : {{ pausetask.id }}</small></p>
            <p><small>暂停任务后任务流程则中断，是否确认?</small></p>
        </bk-dialog>

        <bk-dialog v-model="resumetask.primary.visible"
            theme="primary"
            :mask-close="true"
            :header-position="resumetask.primary.headerPosition"
            @confirm="optask(resumetask.id, 'resume')"
            title="重新执行任务">
            <p><small>流程ID : {{ resumetask.id }}</small></p>
            <p><small>即将重新执行已暂停任务，是否确认?</small></p>
        </bk-dialog>

        <bk-dialog v-model="retrytask.primary.visible"
            theme="primary"
            width="600"
            :mask-close="true"
            :header-position="retrytask.primary.headerPosition"
            @confirm="optask(retrytask.id, 'retry')"
            title="重试失败任务">
            <p><small>流程ID : {{ retrytask.id }}</small></p>
            <p><small>即将直接重试已失败任务，是否确认?</small></p>
            <bk-link
                underline
                theme="primary"
                @click="getherf(retrytask.task_info)">
                如果需要修改任务参数重试发布任务，则请点击这里
            </bk-link>
        </bk-dialog>
        <bk-container :col="12">
            <bk-row>
                <div class="fr clearfix mb15">
                    <bk-form form-type="inline">
                        <bk-form-item label="集群名称">
                            <bk-input placeholder="搜索任务对应集群名称" v-model="formData.cluster_name"></bk-input>
                        </bk-form-item>
                        <bk-form-item label="创建日期">
                            <bk-date-picker placeholder="搜索任务的创建日期" v-model="timeRange" :type="'datetimerange'"></bk-date-picker>
                        </bk-form-item>
                        <bk-form-item>
                            <bk-button @click="search()" theme="primary" title="提交">搜索</bk-button>
                        </bk-form-item>
                    </bk-form>
                </div>
            </bk-row>
            <bk-row>
                <div>
                    <bk-alert type="info" title="展示的执行记录状态是属于当前状态，不作动态刷新" closable></bk-alert>
                </div>
            </bk-row>
            <bk-row>
                <bk-table style="margin-top: 15px;"
                    :data="tableData"
                    :size="size"
                    :pagination="pagination"
                    @highlight-current-row="true"
                    @row-mouse-enter="handleRowMouseEnter"
                    @row-mouse-leave="handleRowMouseLeave"
                    @page-change="handlePageChange"
                    @page-limit-change="handlePageLimitChange"
                    v-bkloading="{ isLoading: textLoading, title: '数据加载中', zIndex: 10 }">
                    <bk-table-column label="流程ID" prop="pipeline_id"></bk-table-column>
                    <bk-table-column label="集群名" prop="cluster_name"></bk-table-column>
                    <bk-table-column label="组件名称" prop="db_type"></bk-table-column>
                    <bk-table-column label="任务模式" prop="task_mode"
                        :filters="typeFilters"
                        :filter-method="typeFiltersMethod"
                        :filter-multiple="false">
                    </bk-table-column>
                    <bk-table-column label="任务类型" prop="task_type"></bk-table-column>
                    <bk-table-column label="操作人" prop="op_user"></bk-table-column>
                    <bk-table-column label="执行状态" prop="task_status"
                        :filters="statusFilters"
                        :filter-method="statusFilterMethod"
                        :filter-multiple="true">
                        <template slot-scope="props">
                            <bk-tag v-show=" props.row.task_status === '执行完成' " theme="success">{{ props.row.task_status }} </bk-tag>
                            <bk-tag v-show=" props.row.task_status === '正在执行' " theme="info">{{ props.row.task_status }} </bk-tag>
                            <bk-tag v-show=" props.row.task_status === '执行失败' " theme="danger">{{ props.row.task_status }} </bk-tag>
                            <bk-tag v-show=" props.row.task_status === '任务暂停' " theme="warning">{{ props.row.task_status }} </bk-tag>
                            <bk-tag v-show=" props.row.task_status === '任务撤销' ">{{ props.row.task_status }} </bk-tag>
                        </template>
                    </bk-table-column>
                    <bk-table-column label="创建时间" prop="create_time"></bk-table-column>
                    <bk-table-column label="结束时间" prop="stop_time"></bk-table-column>
                    <bk-table-column label="任务操作" width="200">
                        <template slot-scope="props">
                            <bk-button theme="primary" text @click="pause(props.row)">暂停</bk-button>
                            <bk-button theme="primary" text @click="revoke(props.row)">撤销</bk-button>
                            <bk-button theme="primary" text @click="resume(props.row)">执行</bk-button>
                            <bk-button theme="primary" text @click="retry(props.row)">重试</bk-button>
                            <bk-button theme="primary" text @click="openSideslider(props.row)">详情</bk-button>
                        </template>
                    </bk-table-column>
                </bk-table>
            </bk-row>
        </bk-container>
        <bk-sideslider :is-show.sync="customSettings.isShow" :quick-close="true" :width="customSettings.width" @hidden="closeSideslider">
            <div slot="header">{{ customSettings.title }}</div>
            <div class="p30" slot="content">
                <bk-container :col="12">
                    <bk-row>
                        <bk-card :title="selectTask.task_type">
                            <p>任务ID: {{selectTask.pipeline_id}}</p>
                            <p>任务状态: {{selectTask.task_status}}</p>
                            <p>创建时间: {{selectTask.create_time}}</p>
                        </bk-card>
                    </bk-row>
                    <bk-row style="margin-top: 20px;">
                        <bk-alert type="info" title="步骤状态默认每5秒刷新一次，日志查询需要跳转到JOB平台查询" closable></bk-alert>
                    </bk-row>
                    <bk-row style="margin-top: 20px">
                        <bk-table
                            :data="TaskDtateDetails"
                            :outer-border="false"
                            :header-border="false"
                            v-bkloading="{ isLoading: textTaskLoading, title: '数据加载中', zIndex: 10 }">>
                            <bk-table-column type="index" label="流程步骤" width="100"></bk-table-column>
                            <bk-table-column label="步骤名称" prop="node_name"></bk-table-column>
                            <bk-table-column label="步骤状态" prop="node_status">
                                <template slot-scope="props">
                                    <bk-tag :theme="props.row.theme">{{ props.row.node_status }} </bk-tag>
                                </template>
                            </bk-table-column>
                            <bk-table-column label="已执行耗时(s)" prop="exec_time"></bk-table-column>
                            <bk-table-column label="日志查询">
                                <template slot-scope="props">
                                    <bk-button theme="primary" size="small" @click="check(props.row.log_url)">查看</bk-button>
                                </template>
                            </bk-table-column>
                        </bk-table>
                    </bk-row>

                </bk-container>
            </div>
        </bk-sideslider>
    </div>
</template>

<script>

    export default {
       
        data () {
            return {
                timeRange: [],
                statusFilters: [
                    { text: '未执行', value: '未执行' },
                    { text: '正在执行', value: '正在执行' },
                    { text: '执行完成', value: '执行完成' },
                    { text: '执行失败', value: '执行失败' },
                    { text: '任务暂停', value: '任务暂停' },
                    { text: '任务撤销', value: '任务撤销' }
                ],
                typeFilters: [
                    { text: '异步触发', value: '异步触发' },
                    { text: '同步触发', value: '同步触发' }
                ],
                revoketask: {
                    primary: {
                        visible: false,
                        headerPosition: 'left'
                    },
                    id: ''
                },
                pausetask: {
                    primary: {
                        visible: false,
                        headerPosition: 'left'
                    },
                    id: ''
                },
                resumetask: {
                    primary: {
                        visible: false,
                        headerPosition: 'left'
                    },
                    id: ''
                },
                retrytask: {
                    primary: {
                        visible: false,
                        headerPosition: 'left'
                    },
                    id: '',
                    task_info: ''
                    
                },
                formData: {
                    db_type: 3,
                    cluster_name: '',
                    start_time: '',
                    stop_time: ''
                },
                textLoading: true,
                textTaskLoading: true,
                temptableData: [],
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                customSettings: {
                    isShow: false,
                    title: '任务详情',
                    width: 800
                },
                TaskDtateDetails: [],
                task_id: '',
                selectTask: {
                    task_type: '',
                    pipeline_id: '',
                    task_status: '',
                    create_time: '',
                    timer: ''
                }
            }
        },
        computed: {
            tableData: function () {
                const start = (this.pagination.current - 1) * this.pagination.limit
                const end = start + this.pagination.limit < this.pagination.count ? start + this.pagination.limit : this.pagination.count
                return this.temptableData.slice(start, end)
            }
        },
        watch: {
            
            'timeRange': function (val) {
                this.formData.start_time = val[0]
                this.formData.stop_time = val[1]
            }
        },
        created () {
            this.getTaskData(this.formData)
        },
        methods: {
            handleInfo (config) {
                config.offsetY = 80
                this.$bkMessage(config)
            },
            closeSideslider () {
                this.selectTask.task_type = ''
                this.selectTask.pipeline_id = ''
                this.selectTask.create_time = ''
                this.selectTask.task_status = ''
                this.TaskDtateDetails = []
                this.textTaskLoading = true
                clearInterval(this.selectTask.timer)
                this.getTaskData(this.formData)
            },
            openSideslider (row) {
                this.customSettings.isShow = true
                this.selectTask.task_type = row.cluster_name + ' ' + row.task_type + '任务'
                this.selectTask.pipeline_id = row.pipeline_id
                this.selectTask.create_time = row.create_time
                this.selectTask.task_status = row.task_status
                this.getEsTaskRecordDetail(row)
                // 定时器，每5秒刷新任务状态
                this.selectTask.timer = setInterval(() => {
                    this.getEsTaskRecordDetail(row)
                }, 5000)
            },
            async getTaskData (param) {
                try {
                    const res = await this.$store.dispatch('kafka/getKafkaTaskRecord', param, { fromCache: true })
                    this.temptableData = res.data
                    this.pagination.count = res.data.length
                    this.textLoading = false
                } catch (e) {
                    this.textLoading = false
                    console.error(e)
                }
            },
            async getEsTaskRecordDetail (row) {
                try {
                    this.textTaskLoading = true
                    const param = { 'pipeline_id': row.pipeline_id }
                    const res = await this.$store.dispatch('kafka/getKafkaTaskRecordDetail', param, { fromCache: true })
                    this.TaskDtateDetails = res.data
                    this.textTaskLoading = false
                } catch (e) {
                    this.textTaskLoading = false
                    console.error(e)
                }
            },
            handlePageLimitChange (limit) {
                this.pagination.limit = limit
            },
            handlePageChange (page) {
                this.pagination.current = page
            },
            statusFilterMethod (value, row, column) {
                const property = column.property
                return row[property] === value
            },
            typeFiltersMethod (value, row, column) {
                const property = column.property
                return row[property] === value
            },
            check (url) {
                window.open(url)
            },
            search () {
                this.textLoading = true
                this.getTaskData(this.formData)
            },
            revoke (row) {
                if (row.task_status !== '执行完成' && row.task_status !== '任务撤销') {
                    this.revoketask.primary.visible = true
                    this.revoketask.id = row.pipeline_id
                } else {
                    this.handleInfo({ theme: 'error', limit: 1, delay: 2000, message: '任务已完成/任务已撤销，无法撤销' })
                }
            },
            pause (row) {
                if (row.task_status === '正在执行') {
                    this.pausetask.primary.visible = true
                    this.pausetask.id = row.pipeline_id
                } else {
                    this.handleInfo({ theme: 'error', limit: 1, delay: 2000, message: '任务未正在执行，无法暂停' })
                }
            },
            resume (row) {
                if (row.task_status === '任务暂停') {
                    this.resumetask.primary.visible = true
                    this.resumetask.id = row.pipeline_id
                } else {
                    this.handleInfo({ theme: 'error', limit: 1, delay: 2000, message: '任务未执行暂停，无法重新执行' })
                }
            },
            retry (row) {
                if (row.task_status === '执行失败') {
                    this.retrytask.primary.visible = true
                    this.retrytask.id = row.pipeline_id
                    this.retrytask.task_info = row
                } else {
                    this.handleInfo({ theme: 'error', limit: 1, delay: 2000, message: '任未执行失败，无法重试任务' })
                }
            },
            getherf (row) {
                if (row.db_type === 'ES') {
                    if (row.task_type === '集群部署') {
                        this.$router.push(
                            {
                                name: 'esnew', query: { 'row': row.task_kwargs }
                            }
                        )
                    } else if (row.task_type === '集群扩容') {
                        this.$router.push(
                            {
                                name: 'esnodeinfo', query: { 'row': JSON.parse(row.task_kwargs) }
                            }
                        )
                    } else if (row.task_type === '集群缩容') {
                        this.$router.push(
                            {
                                name: 'esnodeinfo', query: { 'row': JSON.parse(row.task_kwargs) }
                            }
                        )
                    } else if (row.task_type === '集群录入检测') {
                        this.$router.push(
                            {
                                name: 'esinput', query: { 'row': row.task_kwargs }
                            }
                        )
                    } else {
                        this.handleInfo({ theme: 'error', limit: 1, delay: 2000, message: '跳转页面失败，请联系系统管理员' })
                    }
                } else if (row.db_type === 'Hadoop') {
                    if (row.task_type === '集群部署') {
                        this.$router.push(
                            {
                                name: 'hadoopnew', query: { 'row': row.task_kwargs }
                            }
                        )
                    } else if (row.task_type === '多磁盘扩容' || row.task_type === 'datanode节点扩容') {
                        this.$router.push(
                            {
                                name: 'hadoopdetail', query: { 'row': JSON.parse(row.task_kwargs) }
                            }
                        )
                    } else if (row.task_type === 'datanode节点缩容') {
                        this.$router.push(
                            {
                                name: 'hadoopdetail', query: { 'row': JSON.parse(row.task_kwargs) }
                            }
                        )
                    } else if (row.task_type === '集群录入检测') {
                        this.$router.push(
                            {
                                name: 'hadoopinput', query: { 'row': row.task_kwargs }
                            }
                        )
                    } else {
                        this.handleInfo({ theme: 'error', limit: 1, delay: 2000, message: '跳转页面失败，请联系系统管理员' })
                    }
                } else if (row.db_type === 'Kafka') {
                    if (row.task_type === '集群部署') {
                        this.$router.push(
                            {
                                name: 'kafkanew', query: { 'row': row.task_kwargs }
                            }
                        )
                    } else if (row.task_type === '集群扩容') {
                        this.$router.push(
                            {
                                name: 'kafkabroker', query: { 'row': JSON.parse(row.task_kwargs) }
                            }
                        )
                    } else if (row.task_type === '集群录入检测') {
                        this.$router.push(
                            {
                                name: 'kafkainput', query: { 'row': row.task_kwargs }
                            }
                        )
                    } else {
                        this.handleInfo({ theme: 'error', limit: 1, delay: 2000, message: '跳转页面失败，请联系系统管理员' })
                    }
                } else {
                    this.handleInfo({ theme: 'error', limit: 1, delay: 2000, message: '跳转页面失败，请联系系统管理员' })
                }
            },
            async optask (Id, opType) {
                try {
                    const res = await this.$store.dispatch('kafka/opTask', { 'id': Id, 'op_type': opType })
                    if (res.code === 0) {
                        this.handleInfo({ theme: 'success', limit: 1, delay: 3000, message: res.message })
                        this.getTaskData(this.formData)
                    } else {
                        this.handleInfo({ theme: 'error', limit: 1, delay: 3000, message: res.message })
                    }
                } catch (e) {
                    console.log(e)
                }
            }

        }
    }
    
</script>
<style lang="postcss">
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
