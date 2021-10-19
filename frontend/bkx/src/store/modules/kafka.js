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

        addBroker (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/clusters/add_broker/`
            return http.post(Url, params, config)
        },
        deleteKafkaData (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/clusters/destroy_cluster/`
            return http.post(Url, params, config)
        },

        // 获取Kafka Topic
        listTopics (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/topics/`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },

        // 获取Kafka集群列表
        getKafkaData (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/clusters/`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },

        // 获取broker列表
        getKafkaBroker (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/brokers/`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },

        // 创建Kafka集群
        createKafkaCluster (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/clusters/create_cluster/`
            return http.post(Url, params, config)
        },
        inputKafkaCluster (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/clusters/input_cluster/`
            return http.post(Url, params, config)
        },

        // 创建Kafka Topic
        createTopic (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/topics/create_topic/`
            return http.post(Url, params, config)
        },

        // 查询Kafka Topic
        checkTopic (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/topics/check_topic/`
            return http.post(Url, params, config)
        },

        getAppList (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/apps/`
            return http.get(Url, params, config)
        },
        getKafkaTaskRecord (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record`
            const kwargs = { 'params': params }
            return http.get(Url, kwargs, config)
        },
        getKafkaTaskRecordDetail (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record/get_task/`
            return http.post(Url, params, config)
        },
        opTask (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}v1/record/op_task/`
            return http.post(Url, params, config)
        },
        getMachineCount (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/brokers/get_machine_statistics/`
            return http.post(Url, params, config)
        },
        getMachineCountTop5 (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/brokers/get_machine_statistics_top_five/`
            return http.post(Url, params, config)
        },
        getMonitorData (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/brokers/get_kafka_monitor_data/`
            return http.post(Url, params, config)
        },
        createKafkaMonitor (context, params, config = {}) {
            const Url = `${AJAX_URL_PREFIX}kafka/v1/brokers/create_monitor/`
            return http.post(Url, params, config)
        }
    }
}
