/**
 * @file app store
 * @author
 */

import http from '@/api'
// import queryString from 'query-string'
// import queryString from 'query-string'

export default {
    namespaced: true,
    state: {
    },
    mutations: {
    },
    actions: {
        // 如果需要 mock，那么只需要在 url 后加上 AJAX_MOCK_PARAM 的参数，
        // 参数值为 mock/ajax 下的路径和文件名，然后加上 invoke 参数，参数值为 AJAX_MOCK_PARAM 参数指向的文件里的方法名
        // 例如本例子里，ajax 地址为 table_data，mock 地址为 table_data?AJAX_MOCK_PARAM=index&invoke=getTableData

        /**
         * enterExample1 请求，get 请求
         *
         * @param {Object} context store 上下文对象 { commit, state, dispatch }
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */

        getEsData (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}es/v1/clusters/`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },

        createEsCluster (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}es/v1/clusters/create_cluster/`
            return http.post(Url, params, config)
        },

        inputEsCluster (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}es/v1/clusters/input_cluster/`
            return http.post(Url, params, config)
        },

        deleteEsData (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}es/v1/clusters/destroy_cluster/`
            return http.post(Url, params, config)
        },

        getEsClusterName (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}es/v1/cluster-name/`
            return http.get(Url, params, config)
        },

        addNode (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}es/v1/clusters/add_node/`
            return http.post(Url, params, config)
        },

        getEsNodeInfo (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}es/v1/nodes/`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },

        getEsRule (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}es/v1/rules/`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },

        getAppList (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/apps/`
            return http.get(Url, params, config)
        },

        reduceNode (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}es/v1/clusters/reduce_node/`
            return http.post(Url, params, config)
        },
        getEsTaskRecord (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },
        getEsTaskRecordDetail (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record/get_task/`
            return http.post(Url, params, config)
        },
        opTask (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record/op_task/`
            return http.post(Url, params, config)
        },
        getMachineCount (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}es/v1/nodes/get_machine_statistics/`
            return http.post(Url, params, config)
        },
        getMachineCountTop5 (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}es/v1/nodes/get_machine_statistics_top_five/`
            return http.post(Url, params, config)
        }

    }
}
