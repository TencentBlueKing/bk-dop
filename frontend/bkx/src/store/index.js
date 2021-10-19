/**
 * @file main store
 * @author
 */

import Vue from 'vue'
import Vuex from 'vuex'

import example from './modules/example'
import common from './modules/common'
import es from './modules/es'
import mysql from './modules/mysql'
import hadoop from './modules/hadoop'
import kafka from './modules/kafka'
import http from '@/api'
import { unifyObjectStyle } from '@/common/util'

Vue.use(Vuex)

const store = new Vuex.Store({
    // 模块
    modules: {
        example,
        common,
        es,
        mysql,
        hadoop,
        kafka
    },
    // 公共 store
    state: {
        mainContentLoading: false,
        // 系统当前登录用户
        user: {}
    },
    // 公共 getters
    getters: {
        mainContentLoading: state => state.mainContentLoading,
        user: state => state.user
    },
    // 公共 mutations
    mutations: {
        /**
         * 设置内容区的 loading 是否显示
         *
         * @param {Object} state store state
         * @param {boolean} loading 是否显示 loading
         */
        setMainContentLoading (state, loading) {
            state.mainContentLoading = loading
        },

        /**
         * 更新当前用户 user
         *
         * @param {Object} state store state
         * @param {Object} user user 对象
         */
        updateUser (state, user) {
            state.user = Object.assign({}, user)
        }
    },
    actions: {
        /**
         * 获取用户信息
         *
         * @param {Object} context store 上下文对象 { commit, state, dispatch }
         *
         * @return {Promise} promise 对象
         */
        userInfo (context, config = {}) {
            // ajax 地址为 USER_INFO_URL，如果需要 mock，那么只需要在 url 后加上 AJAX_MOCK_PARAM 的参数，
            // 参数值为 mock/ajax 下的路径和文件名，然后加上 invoke 参数，参数值为 AJAX_MOCK_PARAM 参数指向的文件里的方法名
            // 例如本例子里，ajax 地址为 USER_INFO_URL，mock 地址为 USER_INFO_URL?AJAX_MOCK_PARAM=index&invoke=getUserInfo

            // 后端提供的地址
            // const url = USER_INFO_URL
            // mock 的地址，示例先使用 mock 地址, 修改mock/ajax/index文件
            return http.get(USER_INFO_URL).then(response => {
                const userData = response.data || {}
                context.commit('updateUser', userData)
                return userData
            })
        }
    }
})

/**
 * hack vuex dispatch, add third parameter `config` to the dispatch method
 *
 * @param {Object|string} _type vuex type
 * @param {Object} _payload vuex payload
 * @param {Object} config config 参数，主要指 http 的参数，详见 src/api/index initConfig
 *
 * @return {Promise} 执行请求的 promise
 */
store.dispatch = function (_type, _payload, config = {}) {
    const { type, payload } = unifyObjectStyle(_type, _payload)

    const action = { type, payload, config }
    const entry = store._actions[type]
    if (!entry) {
        if (NODE_ENV !== 'production') {
            console.error(`[vuex] unknown action type: ${type}`)
        }
        return
    }

    store._actionSubscribers.forEach(sub => {
        return sub(action, store.state)
    })

    return entry.length > 1
        ? Promise.all(entry.map(handler => handler(payload, config)))
        : entry[0](payload, config)
}

export default store
