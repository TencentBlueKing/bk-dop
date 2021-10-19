<template>
    <div>
        <bk-container col="12" :gutter="2" :margin="2">
            <bk-row>
                <bk-col>
                    <bk-button theme="primary" @click="newMySQLClusterVisible">新建集群</bk-button>
                </bk-col>
                <!--                <bk-col>-->
                <!--                    <bk-button theme="primary" @click="destroyMySQLCluster">销毁集群</bk-button>-->
                <!--                </bk-col>-->
            </bk-row>
            <bk-row>
                <bk-col span="12">
                    <bk-table :data="mysqlClusters">
                        <bk-table-column type="selection" width="40"></bk-table-column>
                        <bk-table-column type="index" width="80" label="序列"></bk-table-column>
                        <bk-table-column label="集群名" prop="cluster_name"></bk-table-column>
                        <bk-table-column label="mha manager" prop="mha_ip"></bk-table-column>
                        <bk-table-column label="master ip" prop="master"></bk-table-column>
                        <bk-table-column label="slave ips">
                            <template slot-scope="slaveScope">
                                <bk-table :data="dictSlaves(slaveScope.row.slaves)" :show-header="false"
                                    :row-border="false">
                                    <bk-table-column prop="slave"></bk-table-column>
                                    <template slot="empty">
                                        <div class="">
                                            nothing
                                        </div>
                                    </template>
                                </bk-table>
                            </template>
                        </bk-table-column>
                        <bk-table-column label="dead ips">
                            <template slot-scope="deadScope">
                                <bk-table :data="dictSlaves(deadScope.row.deads)" :show-header="false"
                                    :row-border="false">
                                    <bk-table-column prop="slave"></bk-table-column>
                                    <template slot="empty">
                                        <div class="">
                                            nothing
                                        </div>
                                    </template>
                                </bk-table>
                            </template>
                        </bk-table-column>
                        <bk-table-column width="400" label="操作">
                            <template slot-scope="scope">
                                <bk-button theme="default" size="small" @click="addMySQLSlaveVisible(scope.row)">添加
                                    slave
                                </bk-button>
                                <bk-button theme="default" size="small" @click="replaceMhaVisible(scope.row)">替换 mha
                                </bk-button>
                                <bk-button theme="default" size="small" @click="clearDeads(scope.row)">清理 deads
                                </bk-button>
                                <bk-button theme="danger" size="small" @click="destroyMySQLCluster(scope.row)">销毁集群
                                </bk-button>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </bk-col>
            </bk-row>
        </bk-container>
        <bk-dialog
            v-model="newMySQLClusterDialogVisible"
            theme="primary"
            :mask-close="false"
            title="新建集群"
            width="60%"
            @confirm="submitNewMySQLCluster"
        >
            <bk-container gutter="10" col="10">
                <bk-form :model="newMySQLClusterForm" form-type="vertical">
                    <bk-form-item>
                        <bk-row>
                            <bk-col span="2">
                                <label>集群名称</label>
                            </bk-col>
                            <bk-col span="6">
                                <bk-input v-model="newMySQLClusterForm.cluster_name"
                                    placeholder="test-cluster"></bk-input>
                            </bk-col>
                        </bk-row>
                    </bk-form-item>
                    <bk-form-item>
                        <bk-row>
                            <bk-col span="2">
                                <label>Master IP</label>
                            </bk-col>
                            <bk-col span="6">
                                <bk-input v-model="newMySQLClusterForm.master_ip" placeholder="1.1.1.1"></bk-input>
                            </bk-col>
                        </bk-row>
                    </bk-form-item>
                    <bk-form-item>
                        <bk-row>
                            <bk-col span="2">
                                <label>Slave IPS</label>
                            </bk-col>
                            <bk-col span="6">
                                <bk-input v-model="newMySQLClusterForm.slave_ips"
                                    placeholder="2.2.2.2, 3.3.3.3"></bk-input>
                            </bk-col>
                        </bk-row>
                    </bk-form-item>
                    <bk-form-item>
                        <bk-row>
                            <bk-col span="2">
                                <label>MHA Manager</label>
                            </bk-col>
                            <bk-col span="6">
                                <bk-input v-model="newMySQLClusterForm.mha_ip" placeholder="4.4.4.4"></bk-input>
                            </bk-col>
                        </bk-row>
                    </bk-form-item>
                    <bk-form-item>
                        <bk-row>
                            <bk-col span="2">
                                <label>数据目录</label>
                            </bk-col>
                            <bk-col span="4">
                                <bk-input v-model="newMySQLClusterForm.data_base_dir" placeholder="Data dir"></bk-input>
                            </bk-col>
                            <bk-col span="4">
                                数据位于: {{ newMySQLClusterForm.data_base_dir }}/mysqldata
                            </bk-col>
                        </bk-row>
                    </bk-form-item>
                    <bk-form-item>
                        <bk-row>
                            <bk-col span="2">
                                <label>日志目录</label>
                            </bk-col>
                            <bk-col span="4">
                                <bk-input v-model="newMySQLClusterForm.log_base_dir" placeholder="Log dir"></bk-input>
                            </bk-col>
                            <bk-col span="4">
                                日志位于: {{ newMySQLClusterForm.log_base_dir }}/mysqllog
                            </bk-col>
                        </bk-row>
                    </bk-form-item>
                    <bk-form-item>
                        <bk-row>
                            <bk-col span="2">
                                <label>root 密码</label>
                            </bk-col>
                            <bk-col span="4">
                                <bk-input v-model="newMySQLClusterForm.root_psw" placeholder="root password"></bk-input>
                            </bk-col>
                        </bk-row>
                    </bk-form-item>
                    <bk-form-item>
                        <bk-row>
                            <bk-col span="2">
                                <label>buff pool size</label>
                            </bk-col>
                            <bk-col span="4">
                                <bk-input v-model="newMySQLClusterForm.buffer_pool_size" placeholder="10"></bk-input>
                            </bk-col>
                            <bk-col>
                                MB
                            </bk-col>
                        </bk-row>
                    </bk-form-item>
                </bk-form>
            </bk-container>
        </bk-dialog>
        <bk-dialog
            v-model="addMySQLSlaveDialogVisible"
            :title="addMySQLSlaveForm.cluster_name + ' 添加 Slave'"
            :mask-close="false"
            @confirm="submitAddMySQLSlave"
            theme="primary"
            width="60%"
        >
            <bk-container gutter="10" col="10">
                <bk-form :model="addMySQLSlaveForm" form-type="vertical">
                    <bk-form-item>
                        <bk-row>
                            <bk-col span="2">
                                <label>New Slave</label>
                            </bk-col>
                            <bk-col span="6">
                                <bk-input v-model="addMySQLSlaveForm.new_slave" placeholder="1.1.1.1"></bk-input>
                            </bk-col>
                        </bk-row>
                    </bk-form-item>
                </bk-form>
            </bk-container>
        </bk-dialog>
        <bk-dialog
            v-model="replaceMhaDialogVisible"
            title="替换 mha"
            :mask-close="false"
            @confirm="submitReplaceMha"
            width="60%"
            theme="primary"
        >
            <bk-container gutter="10" col="10">
                <bk-form :model="replaceMhaForm" form-type="vertical">
                    <bk-form-item>
                        <bk-row>
                            <bk-col span="2">
                                <label>New mha</label>
                            </bk-col>
                            <bk-col span="6">
                                <bk-input v-model="replaceMhaForm.new_mha_ip" placeholder="1.1.1.1"></bk-input>
                            </bk-col>
                        </bk-row>
                    </bk-form-item>
                </bk-form>
            </bk-container>
        </bk-dialog>
    </div>
</template>

<script>
    export default {
        name: 'list',
        data () {
            return {
                mysqlClusters: [],
                newMySQLClusterDialogVisible: false,
                addMySQLSlaveDialogVisible: false,
                replaceMhaDialogVisible: false,
                newMySQLClusterForm: {
                    cluster_name: '',
                    master_ip: '',
                    slave_ips: '',
                    mha_ip: '',
                    data_base_dir: '',
                    log_base_dir: '',
                    root_psw: '',
                    buffer_pool_size: ''
                },
                addMySQLSlaveForm: {
                    cluster_name: '',
                    new_slave: ''
                },
                replaceMhaForm: {
                    cluster_name: '',
                    new_mha_ip: ''
                }
            }
        },
        created () {
            this.listMySQLClusters()
        },
        methods: {
            async listMySQLClusters () {
                try {
                    const res = await this.$store.dispatch('mysql/listMySQLClusters')
                    console.log(res)
                    this.mysqlClusters = res['data']
                } catch (e) {
                    console.log(e)
                }
            },
            addMySQLSlaveVisible (obj) {
                console.log(obj)
                this.addMySQLSlaveForm = {
                    cluster_name: obj.cluster_name,
                    new_slave: ''
                }
                this.addMySQLSlaveDialogVisible = true
            },
            newMySQLClusterVisible () {
                this.newMySQLClusterForm = {
                    cluster_name: '',
                    master_ip: '',
                    slave_ips: '',
                    mha_ip: '',
                    data_base_dir: '',
                    log_base_dir: '',
                    root_psw: '',
                    buffer_pool_size: ''
                }
                this.newMySQLClusterDialogVisible = true
            },
            replaceMhaVisible (obj) {
                console.log(obj)
                this.replaceMhaForm = {
                    cluster_name: obj.cluster_name,
                    new_mha_ip: ''
                }
                this.replaceMhaDialogVisible = true
            },
            async submitNewMySQLCluster () {
                try {
                    const res = await this.$store.dispatch('mysql/createMySQLCluster', this.newMySQLClusterForm)
                    console.log('submit success: ', res)
                } catch (e) {
                    console.error('submit err: ', e)
                }
            },
            async submitAddMySQLSlave () {
                try {
                    const res = await this.$store.dispatch('mysql/addMySQLSlave', this.addMySQLSlaveForm)
                    console.log(res)
                } catch (e) {
                    console.log(e)
                }
            },
            async submitReplaceMha () {
                try {
                    console.log(this.replaceMhaForm)
                    const res = await this.$store.dispatch('mysql/replaceMha', this.replaceMhaForm)
                    console.log(res)
                } catch (e) {
                    console.log(e)
                }
            },
            destroyMySQLCluster (obj) {
                this.$bkInfo({
                    type: 'warning',
                    title: '销毁集群 ' + obj.cluster_name + ' 将不可恢复',
                    confirmFn: async () => {
                        try {
                            const res = await this.$store.dispatch('mysql/destroyMySQLCluster', {
                                cluster_name: obj.cluster_name
                            })
                            console.log(res)
                        } catch (e) {
                            console.error(e)
                        }
                    }
                })
            },
            async clearDeads (obj) {
                try {
                    console.log(obj)
                    const res = await this.$store.dispatch('mysql/clearMySQLClusterDead', {
                        cluster_name: obj.cluster_name
                    })
                    console.log(res)
                } catch (e) {
                    console.error(e)
                }
            },
            dictSlaves (slaveList) {
                if (slaveList.length === 0) {
                    return [{ 'slave': '-' }]
                }

                const d = []
                slaveList.forEach(ele => {
                    d.push({
                        'slave': ele
                    })
                })
                return d
            }
        }
    }
</script>

<style>

</style>
