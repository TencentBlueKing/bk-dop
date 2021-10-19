<template>
    <bk-table :data="flows" @expand-change="onExpandChange" :expand-row-keys="expandedRows" row-key="id">
        <bk-table-column type="expand">
            <template slot-scope="props">
                <el-table :data="props.row.struct" row-key="id" :show-header="false">
                    <el-table-column label="name" prop="name"></el-table-column>
                    <el-table-column label="id" prop="uuid"></el-table-column>
                    <el-table-column label="status" prop="status"></el-table-column>
                </el-table>
            </template>
        </bk-table-column>
        <bk-table-column label="name" prop="name"></bk-table-column>
        <bk-table-column label="id" prop="uuid"></bk-table-column>
        <bk-table-column label="status" prop="status"></bk-table-column>
    </bk-table>
</template>

<script>

    export default {
        name: 'flows',
        data () {
            return {
                flows: [],
                expandedRows: [],
                timer: 0
            }
        },
        created () {
            this.listMySQLFlows()
        },
        mounted () {
            if (this.timer) {
                clearInterval(this.timer)
            } else {
                this.timer = setInterval(() => {
                    this.listMySQLFlows()
                }, 3000)
            }
        },
        destroyed () {
            clearInterval(this.timer)
        },
        methods: {
            async listMySQLFlows () {
                try {
                    const res = await this.$store.dispatch('mysql/listMySQLFlows')
                    console.log(res)
                    this.flows = res['data']
                } catch (e) {
                    console.error(e)
                }
            },
            onExpandChange (row, expandedRows) {
                console.log(row)
                console.log(expandedRows)
                this.expandedRows = []
                expandedRows.forEach((ele) => {
                    this.expandedRows.push(ele.id)
                })
            }
        }
    }
</script>

<style scoped>

</style>
