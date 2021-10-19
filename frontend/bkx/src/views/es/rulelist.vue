<template>
    <div class="example1-wrapper">
        <div class="fr clearfix mb15">
            <bk-form form-type="inline">
                <bk-form-item label="名称">
                    <bk-input placeholder="名称" v-model="formData.name"></bk-input>
                </bk-form-item>
                <bk-form-item label="日期">
                    <bk-date-picker placeholder="日期" :timer="false" v-model="formData.date"></bk-date-picker>
                </bk-form-item>
                <bk-form-item>
                    <bk-button theme="primary" title="提交">搜索</bk-button>
                </bk-form-item>
            </bk-form>
        </div>
        <bk-table style="margin-top: 15px;"
            :data="tableData"
            :size="size"
            :pagination="pagination"
            @row-mouse-enter="handleRowMouseEnter"
            @row-mouse-leave="handleRowMouseLeave"
            @page-change="handlePageChange">
            <bk-table-column type="selection" width="60" align="center"></bk-table-column>
            <bk-table-column type="index" label="序列" align="center" width="60"></bk-table-column>
            <bk-table-column label="业务" prop="app"></bk-table-column>
            <bk-table-column label="集群名" prop="cluster_name"></bk-table-column>
            <bk-table-column label="账号" prop="user_name"></bk-table-column>
            <bk-table-column label="操作" width="150">
                <template slot-scope="props">
                    <bk-button theme="primary" text @click="remove(props.row)">重置密码</bk-button>
                </template>
            </bk-table-column>
        </bk-table>
    </div>
</template>

<script>
    export default {
        components: {},
        data () {
            return {
                formData: {
                    cluster_name: '',
                    date: ''
                },
                tableData: [],
                pagination: {
                    page: 1,
                    count: 0,
                    limit: 10
                }
            }
        },
        created () {
            this.init()
        },
        methods: {
            init () {
                this.getEsRule()
            },
            async getEsRule () {
                try {
                    const res = await this.$store.dispatch(
                        'es/getEsRule',
                        this.pagination
                    )
                    this.tableData = res.data
                    this.pagination.count = res.data.length
                    console.log(this.pagination.count)
                } catch (e) {
                    console.error(e)
                }
            },
            toggleTableSize () {
                const size = ['small', 'medium', 'large']
                const index = (size.indexOf(this.size) + 1) % 3
                this.size = size[index]
            },
            handlePageChange (page) {
                this.pagination.page = page
                this.getEsData()
            },
            remove (row) {
                const config = { theme: 'error' }
                config.message = '功能开发中'
                config.offsetY = 80
                this.$bkMessage(config)
                // const index = this.tableData.indexOf(row)
                // if (index !== -1) {
                //     this.tableData.splice(index, 1)
                // }
            },
            reset (row) {
                row.status = '创建中'
            }
        }
    }
</script>
