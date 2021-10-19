<template>
    <div>
        <bk-form :model="formData">
            <bk-form-item>
                <bk-input v-model="formData.cluster_name" placeholder="Cluster Name"></bk-input>
            </bk-form-item>
            <bk-form-item>
                <bk-input v-model="formData.master_ip" placeholder="Master IP"></bk-input>
            </bk-form-item>
            <bk-form-item>
                <bk-input v-model="formData.slave_ips" placeholder="Slave IPS"></bk-input>
            </bk-form-item>
            <bk-form-item>
                <bk-input v-model="formData.mha_ip" placeholder="MHA Manager IP"></bk-input>
            </bk-form-item>
            <bk-form-item>
                <bk-input v-model="formData.data_base_dir" placeholder="Data dir"></bk-input>
            </bk-form-item>
            <bk-form-item>
                <bk-input v-model="formData.log_base_dir" placeholder="Log dir"></bk-input>
            </bk-form-item>
            <bk-form-item>
                <bk-input v-model="formData.root_psw" placeholder="root password"></bk-input>
            </bk-form-item>
            <bk-form-item>
                <bk-button type="primary" @click="submitData">提交</bk-button>
            </bk-form-item>
            <bk-tree :data="flowStruct" :node-key="name">
            </bk-tree>
        </bk-form>
    </div>
</template>

<script>
    import { bkForm, bkFormItem, bkButton, bkInput, bkTree } from '@tencent/bk-magic-vue'

    export default {
        comments: {
            bkForm,
            bkFormItem,
            bkButton,
            bkInput,
            bkTree
        },
        data () {
            return {
                formData: {
                    cluster_name: '',
                    master_ip: '',
                    slave_ips: '',
                    mha_ip: '',
                    data_base_dir: '',
                    log_base_dir: '',
                    root_psw: ''
                },
                flowStruct: [{
                    name: '一级 1',
                    children: [{
                        name: '二级 1-1',
                        children: [{
                            name: '三级 1-1-1'
                        }]
                    }]
                }, {
                    name: '一级 2',
                    children: [{
                        name: '二级 2-1',
                        children: [{
                            name: '三级 2-1-1'
                        }]
                    }, {
                        name: '二级 2-2',
                        children: [{
                            name: '三级 2-2-1'
                        }]
                    }]
                }, {
                    name: '一级 3',
                    children: [{
                        name: '二级 3-1',
                        children: [{
                            name: '三级 3-1-1'
                        }]
                    }, {
                        name: '二级 3-2',
                        children: [{
                            name: '三级 3-2-1'
                        }]
                    }]
                }]
            }
        },
        methods: {
            async submitData () {
                try {
                    const res = await this.$store.dispatch('mysql/createMySQLCluster', this.formData)
                    console.log(res)
                    this.flowStruct = res['data']
                } catch (e) {
                    console.error(e)
                }
            }
        }
    }
</script>

<style scoped>

</style>
