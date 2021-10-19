/**
 * @file main entry
 * @author
 */

import './public-path'
import Vue from 'vue'

import App from '@/App'
import router from '@/router'
import store from '@/store'
// import { injectCSRFTokenToHeaders } from '@/api'
// import auth from '@/common/auth'
// import Img403 from '@/images/403.png'
import Exception from '@/components/exception'
import { bus } from '@/common/bus'
import AuthComponent from '@/components/auth'
import ElementUI from 'element-ui'
import '@/common/bkmagic'
import 'element-ui/lib/theme-chalk/index.css'
import '@tencent/bk-magic-vue/lib/utils/svg-icon'

Vue.use(ElementUI)
Vue.component('app-exception', Exception)
Vue.component('app-auth', AuthComponent)
Vue.config.devtools = true

global.bus = bus
global.mainComponent = new Vue({
    el: '#app',
    router,
    store,
    components: { App },
    template: '<App/>'
})
