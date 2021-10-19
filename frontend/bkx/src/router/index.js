/**
 * @file router 配置
 * @author
 */

import Vue from 'vue'
import VueRouter from 'vue-router'

import store from '@/store'
import http from '@/api'
import preload from '@/common/preload'

const MainEntry = () => import(/* webpackChunkName: 'entry' */'@/views')
// import MainEntry from '@/views'

const Main = () => import(/* webpackChunkName: 'mainpage' */'@/views/common/main')

const NotFound = () => import(/* webpackChunkName: 'none' */'@/views/404')
// import NotFound from '@/views/404'

const EsNew = () => import(/* webpackChunkName: 'new' */'@/views/es/new')
const EsList = () => import(/* webpackChunkName: 'list' */'@/views/es/list')
const EsNodeList = () => import(/* webpackChunkName: 'nodelist' */'@/views/es/nodelist')
// const EsRule = () => import(/* webpackChunkName: 'nodelist' */'@/views/es/rulelist')
const EsRecord = () => import(/* webpackChunkName: 'nodelist' */'@/views/es/record')
const EsInput = () => import(/* webpackChunkName: 'none' */'@/views/es/input')

// hadoop
const HadoopList = () => import(/* webpackChunkName: 'none' */'@/views/hadoop/list')
const HadoopNew = () => import(/* webpackChunkName: 'none' */'@/views/hadoop/new')
const HadoopInput = () => import(/* webpackChunkName: 'none' */'@/views/hadoop/input')
const HadoopRecord = () => import(/* webpackChunkName: 'none' */'@/views/hadoop/record')
// const HadoopRule = () => import(/* webpackChunkName: 'none' */'@/views/hadoop/rulelist')
const HadoopDetail = () => import(/* webpackChunkName: 'none' */'@/views/hadoop/detail')
const HadoopMonitor = () => import(/* webpackChunkName: 'none' */'@/views/hadoop/monitor')
// redis
const RedisNew = () => import(/* webpackChunkName: 'none' */'@/views/redis/redisnew')
const RedisDel = () => import(/* webpackChunkName: 'none' */'@/views/redis/redisdel')
const RedisBackup = () => import(/* webpackChunkName: 'none' */'@/views/redis/redisbackup')
const RedisClean = () => import(/* webpackChunkName: 'none' */'@/views/redis/redisclean')
const RedisSwitch = () => import(/* webpackChunkName: 'none' */'@/views/redis/redisswitch')
const RedisRebuild = () => import(/* webpackChunkName: 'none' */'@/views/redis/redisrebuild')
const RedisKeys = () => import(/* webpackChunkName: 'none' */'@/views/redis/rediskeys')
const RedisHotKeys = () => import(/* webpackChunkName: 'none' */'@/views/redis/redishotkeys')
const RedisBigKeys = () => import(/* webpackChunkName: 'none' */'@/views/redis/redisbigkeys')
const RedisClusterNew = () => import(/* webpackChunkName: 'none' */'@/views/redis/redisclusternew')
const RedisClusterAdd = () => import(/* webpackChunkName: 'none' */'@/views/redis/redisclusteradd')
const RedisClusterReduce = () => import(/* webpackChunkName: 'none' */'@/views/redis/redisclusterreduce')

// mysql
const MySQLList = () => import('@/views/mysql/list')
const MySQLFlows = () => import('@/views/mysql/flows')

// kafka
const KafkaNew = () => import(/* webpackChunkName: 'new' */'@/views/kafka/new')
const KafkaInput = () => import(/* webpackChunkName: 'nodelist' */'@/views/kafka/input')
const KafkaList = () => import(/* webpackChunkName: 'list' */'@/views/kafka/list')
const KafkaRecord = () => import(/* webpackChunkName: 'record' */'@/views/kafka/record')
const KafkaBroker = () => import(/* webpackChunkName: 'nodelist' */'@/views/kafka/brokerlist')
const KafkaMonitor = () => import(/* webpackChunkName: 'nodelist' */'@/views/kafka/monitor')
// common
const TaskRecord = () => import(/* webpackChunkName: 'taskrecord' */'@/views/common/taskrecord')

Vue.use(VueRouter)

const routes = [
    {
        path: window.PROJECT_CONFIG.SITE_URL,
        component: MainEntry,
        children: [
            {
                path: 'common/main',
                alias: '',
                name: 'mainpage',
                component: Main,
                meta: {
                    matchRoute: '首页'
                }
            },
            {
                path: 'es',
                name: 'es',
                component: MainEntry,
                children: [
                    {
                        path: 'info',
                        name: 'esinfo',
                        component: EsList,
                        meta: {
                            matchRoute: 'ES集群管理'
                        }
                    },
                    {
                        path: 'input',
                        name: 'esinput',
                        component: EsInput,
                        meta: {
                            matchRoute: 'ES集群纳管'
                        }
                    },
                    {
                        path: 'nodeinfo',
                        name: 'esnodeinfo',
                        component: EsNodeList,
                        meta: {
                            matchRoute: 'ES集群信息'
                        }
                    },
                    {
                        path: 'new',
                        name: 'esnew',
                        component: EsNew,
                        meta: {
                            matchRoute: 'ES集群部署'
                        }
                    },
                    {
                        path: 'record',
                        name: 'esrecord',
                        component: EsRecord,
                        meta: {
                            matchRoute: 'ES执行记录'
                        }
                    }
                ]
            },
            {
                path: 'mysql',
                name: 'mysql',
                component: MainEntry,
                redirect: 'mysql/mysqllist',
                children: [
                    {
                        path: 'mysqllist',
                        name: 'mysqllist',
                        component: MySQLList
                    },
                    {
                        path: 'mysqlflows',
                        name: 'mysqlflows',
                        component: MySQLFlows
                    }
                ]
            },
            {
                path: 'hadoop',
                name: 'hadoop',
                component: MainEntry,
                // redirect: 'hadoop/info',
                children: [
                    {
                        path: 'hadoopinfo',
                        name: 'hadoopinfo',
                        component: HadoopList,
                        meta: {
                            matchRoute: 'Hadoop集群管理'
                        }
                    },
                    {
                        path: 'hadoopnew',
                        name: 'hadoopnew',
                        component: HadoopNew,
                        meta: {
                            matchRoute: 'Hadoop集群部署'
                        }
                    },
                    {
                        path: 'hadoopinput',
                        name: 'hadoopinput',
                        component: HadoopInput,
                        meta: {
                            matchRoute: 'Hadoop集群纳管'
                        }
                    },
                    {
                        path: 'hadooprecord',
                        name: 'hadooprecord',
                        component: HadoopRecord,
                        meta: {
                            matchRoute: 'Hadoop执行记录'
                        }
                    },
                    // {
                    //     path: 'hadooprule',
                    //     name: 'hadooprule',
                    //     component: HadoopRule,
                    //     meta: {
                    //         matchRoute: 'HDFS权限管理'
                    //     }
                        
                    // },
                    {
                        path: 'hadoopdetail',
                        name: 'hadoopdetail',
                        component: HadoopDetail,
                        meta: {
                            matchRoute: 'Hadoop节点信息'
                        }
                    },
                    {
                        path: 'monitor',
                        name: 'hadoopmonitor',
                        component: HadoopMonitor,
                        meta: {
                            matchRoute: 'Hadoop仪表盘'
                        }
                    }
                ]
            },
            {
                path: 'redis',
                name: 'redis',
                component: MainEntry,
                // redirect: 'hadoop/info',
                children: [
                    {
                        path: 'new',
                        name: '/redis/new',
                        component: RedisNew
                    },
                    {
                        path: 'del',
                        name: '/redis/del',
                        component: RedisDel
                    },
                    {
                        path: 'cluster/new',
                        name: '/redis/cluster/new',
                        component: RedisClusterNew
                    },
                    {
                        path: 'cluster/add',
                        name: '/redis/cluster/add',
                        component: RedisClusterAdd
                    },
                    {
                        path: 'cluster/reduce',
                        name: '/redis/cluster/reduce',
                        component: RedisClusterReduce
                    },
                    {
                        path: 'backup',
                        name: '/redis/backup',
                        component: RedisBackup
                    },
                    {
                        path: 'clean',
                        name: '/redis/clean',
                        component: RedisClean
                    },
                    {
                        path: 'switch',
                        name: '/redis/switch',
                        component: RedisSwitch
                    },
                    {
                        path: 'rebuild',
                        name: '/redis/rebuild',
                        component: RedisRebuild
                    },
                    {
                        path: 'keys',
                        name: '/redis/keys',
                        component: RedisKeys
                    },
                    {
                        path: 'hotkeys',
                        name: '/redis/hotkeys',
                        component: RedisHotKeys
                    },
                    {
                        path: 'bigkeys',
                        name: '/redis/bigkeys',
                        component: RedisBigKeys
                    }
                ]
            },
            {
                path: 'kafka',
                name: 'kafka',
                component: MainEntry,
                redirect: 'kafka/info',
                children: [
                    {
                        path: 'info',
                        name: 'kafkainfo',
                        component: KafkaList,
                        meta: {
                            matchRoute: 'Kafka集群管理'
                        }
                    },
                    {
                        path: 'broker',
                        name: 'kafkabroker',
                        component: KafkaBroker,
                        meta: {
                            matchRoute: 'Kafka集群信息'
                        }
                    },
                    {
                        path: 'input',
                        name: 'kafkainput',
                        component: KafkaInput,
                        meta: {
                            matchRoute: 'Kafka集群纳管'
                        }
                    },
                    {
                        path: 'new',
                        name: 'kafkanew',
                        component: KafkaNew,
                        meta: {
                            matchRoute: 'Kafka集群部署'
                        }
                    },
                    {
                        path: 'record',
                        name: 'kafkarecord',
                        component: KafkaRecord,
                        meta: {
                            matchRoute: 'Kafka执行记录'
                        }
                    },
                    {
                        path: 'monitor',
                        name: 'kafkamonitor',
                        component: KafkaMonitor,
                        meta: {
                            matchRoute: 'Kafka仪表盘'
                        }
                    }

                ]
            },
            {
                path: 'common',
                name: 'common',
                component: MainEntry,
                children: [
                    {
                        path: 'taskrecord',
                        name: 'taskrecord',
                        component: TaskRecord,
                        meta: {
                            matchRoute: '执行记录'
                        }
                    }
                ]
            }
        ]
    },
    // 404
    {
        path: '*',
        name: '404',
        component: NotFound
    }
]

const router = new VueRouter({
    mode: 'history',
    routes: routes
})

const cancelRequest = async () => {
    const allRequest = http.queue.get()
    const requestQueue = allRequest.filter(request => request.cancelWhenRouteChange)
    await http.cancel(requestQueue.map(request => request.requestId))
}

let preloading = true
let canceling = true
let pageMethodExecuting = true

router.beforeEach(async (to, from, next) => {
    canceling = true
    await cancelRequest()
    canceling = false
    next()
})

router.afterEach(async (to, from) => {
    store.commit('setMainContentLoading', true)

    preloading = true
    await preload()
    preloading = false

    const pageDataMethods = []
    const routerList = to.matched
    routerList.forEach(r => {
        Object.values(r.instances).forEach(vm => {
            if (typeof vm.fetchPageData === 'function') {
                pageDataMethods.push(vm.fetchPageData())
            }
            if (vm.$options.preload === 'function') {
                pageDataMethods.push(vm.$options.preload.call(vm))
            }
        })
    })

    pageMethodExecuting = true
    await Promise.all(pageDataMethods)
    pageMethodExecuting = false

    if (!preloading && !canceling && !pageMethodExecuting) {
        store.commit('setMainContentLoading', false)
    }
})

export default router
