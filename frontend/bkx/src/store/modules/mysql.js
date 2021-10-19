/**
 * @file app store
 * @author
 */

import http from '@/api'
// import queryString from 'query-string'

export default {
    namespaced: true,
    state: {},
    mutations: {},
    actions: {
        // // 如果需要 mock，那么只需要在 url 后加上 AJAX_MOCK_PARAM 的参数，
        // // 参数值为 mock/ajax 下的路径和文件名，然后加上 invoke 参数，参数值为 AJAX_MOCK_PARAM 参数指向的文件里的方法名
        // // 例如本例子里，ajax 地址为 table_data，mock 地址为 table_data?AJAX_MOCK_PARAM=index&invoke=getTableData
        //
        // /**
        //  * enterExample1 请求，get 请求
        //  *
        //  * @param {Object} context store 上下文对象 { commit, state, dispatch }
        //  * @param {Object} params 请求参数
        //  *
        //  * @return {Promise} promise 对象
        //  */
        //
        // getTableData (context, params, config = {}) {
        //     // mock 的地址，示例先使用 mock 地址
        //     const mockUrl = `${AJAX_URL_PREFIX}table?${AJAX_MOCK_PARAM}=index&invoke=getTableData&${queryString.stringify(params)}`
        //     return http.get(mockUrl, params, config)
        // },
        createMySQLCluster (context, params, config = {}) {
            // const mockUrl = `${AJAX_URL_PREFIX}v1/mysql/cluster?${MYSQL_AJAX_MOCK_PARAM}=index&invoke=createMySQLCluster&${queryString.stringify(params)}`
            // eslint-disable-next-line no-undef
            const mockUrl = `${AJAX_URL_PREFIX}mysql/cluster/new/`
            return http.post(mockUrl, params, config)
        },
        addMySQLSlave (context, params, config = {}) {
            // eslint-disable-next-line no-undef
            const mockUrl = `${AJAX_URL_PREFIX}mysql/cluster/add_slave/`
            return http.post(mockUrl, params, config)
        },
        replaceMha (context, params, config = {}) {
            // eslint-disable-next-line no-undef
            const mockUrl = `${AJAX_URL_PREFIX}mysql/cluster/replace_mha/`
            return http.post(mockUrl, params, config)
        },
        listMySQLClusters (context, params, config = {}) {
            // eslint-disable-next-line no-undef
            const mockUrl = `${AJAX_URL_PREFIX}mysql/cluster/list/`
            return http.get(mockUrl, params, config)
        },
        listMySQLFlows (context, params, config = {}) {
            // eslint-disable-next-line no-undef
            const mockUrl = `${AJAX_URL_PREFIX}mysql/flows/`
            return http.get(mockUrl, params, config)
        },
        destroyMySQLCluster (context, params, config = {}) {
            // eslint-disable-next-line no-undef
            const mockUrl = `${AJAX_URL_PREFIX}mysql/cluster/destroy/`
            return http.post(mockUrl, params, config)
        },
        clearMySQLClusterDead (context, params, config = {}) {
            // eslint-disable-next-line no-undef
            const mockUrl = `${AJAX_URL_PREFIX}mysql/cluster/clear_dead/`
            return http.post(mockUrl, params, config)
        }
    }
}
