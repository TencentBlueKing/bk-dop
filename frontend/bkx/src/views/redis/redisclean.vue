<template>
    <div style="width: 600px;">
        <bk-form :label-width="200" :model="formData" :rules="rules" ref="formData">
            <bk-form-item label="清档类型" :required="true" :property="'version'">
                <bk-select v-model="formData.version" searchable>
                    <bk-option v-for="option in versionList"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item label="实例列表" :required="true" :property="'master_list'" :error-display-type="'normal'">
                <bk-input type="textarea" v-model="formData.master_list" placeholder=""></bk-input>
            </bk-form-item>
            <bk-form-item label="DB编号" :property="'password'" :error-display-type="'normal'">
                <bk-input v-model="formData.cluster_name" placeholder="" value="0"></bk-input>
                <p class="mt5 mb0 f12" slot="tip"></p>
            </bk-form-item>
            <bk-form-item label="强制执行" :required="true" :property="'yun'">
                <bk-select v-model="formData.yun" searchable>
                    <bk-option v-for="option in yunList"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item label="是否重启进程" :required="true" :property="'zone'">
                <bk-select v-model="formData.zone" searchable>
                    <bk-option v-for="option in zoneList"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item>
                <bk-button ext-cls="mr5" theme="primary" title="提交" @click="submitnewclusterForm" :loading="submitLoading">提交</bk-button>
                <bk-button ext-cls="mr5" theme="default" title="取消">取消</bk-button>
            </bk-form-item>
        </bk-form>
    </div>
</template>
<script>
    import { bkForm, bkFormItem, bkButton, bkInput } from '@tencent/bk-magic-vue'

    export default {
        components: {
            bkForm,
            bkFormItem,
            bkButton,
            bkInput
        },
        data () {
            return {
                formData: {
                    cluster_name: '',
                    version: '',
                    master_list: '',
                    data_list: '',
                    cold_list: '',
                    client_list: '',
                    http_port: '6300',
                    description: '',
                    yun: '',
                    zone: '',
                    app: 'lol',
                    appid: 999
                },
                submitLoading: false,
                versionList: [
                    {
                        id: '1',
                        name: '只清理单个db'
                    },
                    {
                        id: '2',
                        name: '清理所有数据'
                    }
                ],
                yunList: [
                    {
                        id: '1',
                        name: 'YES'
                    },
                    {
                        id: '2',
                        name: 'NO'
                    }
                ],
                zoneList: [
                    {
                        id: '1',
                        name: 'NO'
                    },
                    {
                        id: '2',
                        name: 'YES'
                    }
                ],
                rules: {
                    zone: [{ required: true, message: '请选择地区', trigger: 'change' }],
                    cluster_name: [
                        {
                            required: true,
                            pattern: /^[a-z0-9]+[a-z0-9-]+[a-z0-9]+$/,
                            message: '请输入集群名称(只能包含小写字母，数字，-)',
                            trigger: 'change'
                        },
                        { min: 2, max: 32, message: '长度在 2 到 32 个字符', trigger: 'change' },
                        {
                            validator: this.checkClusterName,
                            message: function (val) {
                                return `集群${val}存在，请重新输入`
                            },
                            trigger: 'change'
                        }
                    ],
                    yun: [
                        {
                            required: true,
                            message: '请选择云供应商',
                            trigger: 'change'
                        }
                    ],
                    version: [
                        {
                            required: true,
                            message: '请选择版本',
                            trigger: 'change'
                        }
                    ],
                    master_list: [
                        {
                            required: true,
                            message: '请输入作为master的IP列表',
                            trigger: 'change'
                        }
                    ],
                    data_list: [
                        {
                            required: true,
                            message: '请输入作为数据节点的IP列表',
                            trigger: 'blur'
                        }
                    ]
                }
            }
        },
        methods: {
            closeDialog () {
                window.location = '/es/record/'
            },
            submitnewclusterForm () {
                this.$refs.formData.validate((valid) => {
                    if (valid) {
                        this.submitLoading = true
                        try {
                            const res = this.$store.dispatch('es/createEsCluster', this.formData)
                            if (res) {
                                this.$bkMessage({
                                    message: '提交成功, 请到ES执行记录中查看部署详情！',
                                    theme: 'success'
                                })
                            }
                        } catch (err) {
                            this.$bkMessage({
                                message: err.message ? err.message : err,
                                theme: 'error'
                            })
                        } finally {
                            this.submitLoading = false
                            this.closeDialog()
                        }
                    }
                })
            },
            async checkClusterName (val) {
                let result = true
                const res = await this.$store.dispatch('es/getEsClusterName')
                this.esClusterName = res.data
                console.log(this.esClusterName)
                for (const a in this.esClusterName) {
                    console.log(this.esClusterName[a]['cluster_name'])
                    if (val === this.esClusterName[a]['cluster_name']) {
                        result = false
                        break
                    }
                }
                return result
            },
            clearError1 () {
                this.$refs.validateForm1.clearError()
            }
        }
    }
</script>
