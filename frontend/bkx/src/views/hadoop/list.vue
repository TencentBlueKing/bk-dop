<template>
    <div class="wrapper">
        <div>
            <bk-form form-type="inline">
                <bk-form-item :required="true" :property="'app'" :error-display-type="'normal'">
                    <bk-select v-model="selectedAppList"
                        searchable
                        multiple
                        show-select-all
                        display-tag
                        style="width: 350px"
                        placeholder="筛选业务,可多选，过滤时根据集群名称搜索失效"
                        @change="changeHandle">
                        <bk-option v-for="option in appinfo"
                            :key="option.bk_biz_id"
                            :id="option.bk_biz_id"
                            :name="option.bk_biz_name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                
            </bk-form>
            <bk-form form-type="inline" class="fr clearfix mb15">
                <bk-form-item label="集群名称">
                    <bk-input placeholder="组件+集群名称全局唯一" v-model="formData.cluster_name"></bk-input>
                </bk-form-item>
                <bk-form-item>
                    <bk-button @click="search" theme="primary" title="提交">搜索</bk-button>
                </bk-form-item>
                <bk-form-item>
                    <bk-button @click="output" theme="primary" title="导出">导出本页数据</bk-button>
                </bk-form-item>
            </bk-form>
        </div>
        <bk-dialog v-model="deleteCluster.primary.visible"
            theme="warning"
            width="700"
            :mask-close="true"
            :header-position="deleteCluster.primary.headerPosition"
            @confirm="deleteHadoopData(deleteCluster.info)"
            title="集群信息删除任务">
            <p>业务名称 : {{ deleteCluster.info.app }}</p>
            <p>集群名称 : {{ deleteCluster.info.cluster_name }}</p>
            <p style="color: red">删除集群的相关信息(不回收进程)，该操作不可逆！是否确认?</p>
        </bk-dialog>
        
        <bk-table id="mytable" style="margin-top: 15px;"
            :data="tableData"
            :size="size"
            :pagination="pagination"
            @row-mouse-enter="handleRowMouseEnter"
            @row-mouse-leave="handleRowMouseLeave"
            @page-change="handlePageChange"
            @page-limit-change="handleLimitChange"
            v-bkloading="{ isLoading: textLoading, title: '数据加载中', zIndex: 10 }">
            <bk-table-column label="集群id" prop="cluster_id"></bk-table-column>
            <bk-table-column label="业务名称" prop="app"></bk-table-column>
            <bk-table-column label="集群名称" prop="cluster_name"></bk-table-column>
            <bk-table-column label="添加模式" prop="add_type"
                :filters="typeFilters"
                :filter-method="typeFiltersMethod"
                :filter-multiple="false"></bk-table-column>
            <bk-table-column label="集群状态" prop="cluster_status"></bk-table-column>
            <bk-table-column label="集群版本" prop="cluster_version"></bk-table-column>
            <bk-table-column label="创建人" prop="create_user"></bk-table-column>
            <bk-table-column label="创建时间" prop="create_time"></bk-table-column>
            <bk-table-column label="操作">
                <template slot-scope="props">
                    <bk-button theme="primary" text @click="getClusterDetail(props.row)">集群详情</bk-button>
                    <bk-button theme="primary" text @click="deleteDialog(props.row)">集群删除</bk-button>
                    <bk-button theme="primary" text @click="bklogUrl()">日志查看</bk-button>
                </template>
            </bk-table-column>
        </bk-table>
    </div>
</template>

<script>
    import FileSaver from 'file-saver'
    import XLSX from 'xlsx'
    export default {
        components: {
        },
        data () {
            return {
                typeFilters: [
                    { text: '平台新建', value: '平台新建' },
                    { text: '平台录入', value: '平台录入' }
                ],
                formData: {
                    cluster_name: ''
                },
                selectedAppList: [],
                temptableData: [],
                appinfo: [],
                size: 'large',
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                hdfsInfo: '',
                textLoading: true,
                deleteCluster: {
                    primary: {
                        visible: false,
                        headerPosition: 'left'
                    },
                    info: ''
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
        created () {
            this.getInfoData()
            this.getHadoopData(this.formData)
        },
        methods: {
            closeDialog () {
                this.$router.push(
                    {
                        path: 'hadooprecord'
                    }
                )
            },
            bklogUrl: function () {
                const url = window.PROJECT_CONFIG.BKPAAS_URL + '/o/bk_log_search/#/manage/collect'
                window.open(url)
            },
            handleInfo (config) {
                config.offsetY = 80
                this.$bkMessage(config)
            },
            typeFiltersMethod (value, row, column) {
                const property = column.property
                return row[property] === value
            },
            getClusterDetail (row) {
                this.$router.push(
                    {
                        path: 'hadoopdetail', query: { 'row': row }
                    }
                )
            },
            deleteDialog (row) {
                if (row.cluster_status !== '集群变更中' && row.cluster_status !== '集群回收中') {
                    this.deleteCluster.primary.visible = true
                    this.deleteCluster.info = row
                } else {
                    this.handleInfo({ theme: 'error', limit: 1, delay: 2000, message: '集群处于正常变更中状态，暂时不能删除' })
                }
            },
            async getInfoData () {
                try {
                    const res = await this.$store.dispatch('hadoop/getAppInfoData', {}, { fromCache: true })
                    this.appinfo = res.data.info
                } catch (e) {
                    console.error(e)
                }
            },
            async getHadoopData (param) {
                try {
                    const res = await this.$store.dispatch('hadoop/getHadoopData', param, { fromCache: true })
                    this.temptableData = res.data
                    this.pagination.count = res.data.length
                    this.textLoading = false
                } catch (e) {
                    this.textLoading = false
                    console.error(e)
                }
            },
            async deleteHadoopData (param) {
                try {
                    this.textLoading = true
                    const res = await this.$store.dispatch('hadoop/deleteHadoopData', param)
                    if (res.code === 0) {
                        this.handleInfo({ theme: 'success', limit: 1, delay: 2000, message: '集群信息删除完成' })
                        this.closeDialog()
                    } else {
                        this.textLoading = false
                        this.handleInfo({ theme: 'error', limit: 1, delay: 2000, message: '集群信息删除失败' })
                    }
                } catch (e) {
                    this.textLoading = false
                    this.handleInfo({ theme: 'error', limit: 1, delay: 2000, message: e })
                }
            },
            async changeHandle (value) {
                const appIdList = this.selectedAppList.join(',')
                this.formData.cluster_name = ''
                this.textLoading = true
                this.getHadoopData({ 'selectedAppList': appIdList })
            },
            handlePageChange (page) {
                this.pagination.current = page
            },
            handleLimitChange (limit) {
                this.pagination.limit = limit
                this.handlePageChange(1)
            },
            output () {
                /* generate workbook object from table */
                const wb = XLSX.utils.table_to_book(document.querySelector('#mytable')) // mytable为表格的id名
                /* get binary string as output */
                const wbout = XLSX.write(wb, { bookType: 'xlsx', bookSST: true, type: 'array' })
                try {
                    FileSaver.saveAs(new Blob([wbout], { type: 'application/octet-stream' }), 'sheet.xlsx')
                } catch (e) {
                    if (typeof console !== 'undefined') console.log(e, wbout)
                }
                return wbout
            },
            search () {
                this.textLoading = true
                this.getHadoopData(this.formData)
            }
            
        }
    }
</script>
