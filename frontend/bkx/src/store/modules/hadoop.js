/**
 * @file app store
 * @author
 */

import http from '@/api'
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

        getAppInfoData (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/apps/`
            return http.get(Url, params, config)
        },

        getHadoopData (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/clusters/`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },
        createHadoopCluster (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/clusters/create_cluster/`
            return http.post(Url, params, config)
        },
        inputHadoopCluster (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/clusters/input_cluster/`
            return http.post(Url, params, config)
        },

        addDataNode (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/clusters/add_node/`
            return http.post(Url, params, config)
        },

        addDir (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/clusters/add_dir/`
            return http.post(Url, params, config)
        },

        removeDataNode (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/clusters/remove_node/`
            return http.post(Url, params, config)
        },

        deleteHadoopData (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/clusters/destroy_cluster/`
            return http.post(Url, params, config)
        },

        getHadoopDetail (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/detail/`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },
        getHadooptaskDetail (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record/get_task/`
            return http.post(Url, params, config)
        },

        getHadooptaskRecord (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },
        opTask (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record/op_task/`
            return http.post(Url, params, config)
        },
        getMachineCount (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/detail/get_machine_statistics/`
            return http.post(Url, params, config)
        },
        getMachineCountTop5 (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/detail/get_machine_statistics_top_five/`
            return http.post(Url, params, config)
        },
        createHadoopMonitor (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/clusters/create_monitor/`
            return http.post(Url, params, config)
        },
        getMonitorData (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}hadoop/v1/clusters/get_hadoop_monitor_data/`
            return http.post(Url, params, config)
        }
    }
}
