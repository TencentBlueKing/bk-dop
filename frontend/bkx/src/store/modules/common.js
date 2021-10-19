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
 
        getTaskStatistics (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record/get_task_sum_group_by_db/`
            return http.post(Url, params, config)
        },
        getTaskRecord (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },
        getTaskRecordDetail (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record/get_task/`
            return http.post(Url, params, config)
        },
        opTask (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record/op_task/`
            return http.post(Url, params, config)
        }
    }
}
