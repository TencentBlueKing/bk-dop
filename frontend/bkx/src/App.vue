<template>
    <div id="app" :class="systemCls">
        <bk-navigation
            :header-title="nav.id"
            :side-title="nav.title"
            :navigation-type="curNav.nav"
            :need-menu="curNav.needMenu"
            :default-open="true"
            @toggle="handleToggle">
            <template slot="header">
                <div class="monitor-navigation-header">
                    <ol class="header-nav" v-if="curNav.nav === 'top-bottom'">
                        <li class="header-nav-item" v-for="(item,index) in header.list" :key="item.id"
                            :class="{ 'item-active': index === header.active }">
                            <bk-popover theme="light navigation-message" :arrow="false" offset="-50, 10"
                                placement="bottom-start">
                                {{ item.name }}
                                <template slot="content">
                                    <ul class="monitor-navigation-nav">
                                        <li class="nav-item" v-for="headerNavItem in curHeaderNav.navList"
                                            :key="headerNavItem.id">
                                            {{ headerNavItem.name }}
                                        </li>
                                    </ul>
                                </template>
                            </bk-popover>
                        </li>
                    </ol>
                    <div v-else class="header-title">
                        <!-- <span class="header-title-icon">
                            <svg class="icon" style="width: 30em; height: 30em;vertical-align: middle;fill: currentColor;overflow: hidden;" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4756"><path d="M416 480h320v64H416l96 96-48 48-176-176 176-176 48 48-96 96z" p-id="4757"></path></svg>
                        </span> -->
                        <span class="ml5">{{ nav.id }}</span>
                    </div>
                    <!-- <bk-select class="header-select" :class="{ 'is-left': curNav.nav === 'left-right' }"
                        v-model="header.bizId" :clearable="false" searchable :disabled="true">
                        <bk-option v-for="option in header.selectList"
                            :key="option.id"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select> -->
                    
                    <!-- <bk-popover theme="light navigation-message" :arrow="false" offset="-150, 5">
                        <div class="header-mind" :class="{ 'is-left': curNav.nav === 'left-right' }">
                            <svg
                                style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;"
                                viewBox="0 0 64 64" version="1.1" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M32,56c-1.3,0-2.6-0.6-3.4-1.6h-4.5c0.5,1.5,1.4,2.7,2.6,3.7c3.1,2.5,7.5,2.5,10.6,0c1.2-1,2.1-2.3,2.6-3.7h-4.5C34.6,55.4,33.3,56,32,56z"></path>
                                <path
                                    d="M53.8,49.1L50,41.5V28c0-8.4-5.8-15.7-14-17.6V8c0-2.2-1.8-4-4-4s-4,1.8-4,4v2.4c-8.2,1.9-14,9.2-14,17.6v13.5l-3.8,7.6c-0.3,0.6-0.3,1.3,0.1,1.9c0.4,0.6,1,1,1.7,1h40c0.7,0,1.3-0.4,1.7-1C54,50.4,54.1,49.7,53.8,49.1z"></path>
                            </svg>
                            <span class="header-mind-mark" :class="{ 'is-left': curNav.nav === 'left-right' }"></span>
                        </div>
                        <template slot="content">
                            <div class="monitor-navigation-message">
                                <h5 class="message-title">消息中心</h5>
                                <ul class="message-list">
                                    <li class="message-list-item" v-for="(item,index) in message.list" :key="index">
                                        <span class="item-message">{{ item.message }}</span>
                                        <span class="item-date">{{ item.date }}</span>
                                    </li>
                                </ul>
                                <div class="message-footer">进入消息中心</div>
                            </div>
                        </template>
                    </bk-popover> -->
                    <!-- <div class="header-help" :class="{ 'is-left': curNav.nav === 'left-right' }">
                        <svg class="bk-icon"
                            style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;"
                            viewBox="0 0 64 64" version="1.1" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M32,4C16.5,4,4,16.5,4,32c0,3.6,0.7,7.1,2,10.4V56c0,1.1,0.9,2,2,2h13.6C36,63.7,52.3,56.8,58,42.4S56.8,11.7,42.4,6C39.1,4.7,35.6,4,32,4z M31.3,45.1c-1.7,0-3-1.3-3-3s1.3-3,3-3c1.7,0,3,1.3,3,3S33,45.1,31.3,45.1z M36.7,31.7c-2.3,1.3-3,2.2-3,3.9v0.9H29v-1c-0.2-2.8,0.7-4.4,3.2-5.8c2.3-1.4,3-2.2,3-3.8s-1.3-2.8-3.3-2.8c-1.8-0.1-3.3,1.2-3.5,3c0,0.1,0,0.1,0,0.2h-4.8c0.1-4.4,3.1-7.4,8.5-7.4c5,0,8.3,2.8,8.3,6.9C40.5,28.4,39.2,30.3,36.7,31.7z"></path>
                        </svg>
                    </div> -->
                    <bk-popover style="margin-left: auto " theme="light navigation-message" :arrow="false" offset="-20, 10"
                        placement="bottom-start">
                        <div class="header-user" :class="{ 'is-left': curNav.nav === 'left-right' }">
                            {{ user.username }}
                            <!-- <i class="bk-icon icon-down-shape"></i> -->
                        </div>
                        <!-- <template slot="content">
                            <ul class="monitor-navigation-admin">
                                <li class="nav-item" v-for="userItem in admin.list" :key="userItem">
                                    {{ userItem }}
                                </li>
                            </ul>
                        </template> -->
                    </bk-popover>
                </div>
            </template>
            <template slot="menu">
                <bk-navigation-menu
                    ref="menu"
                    @select="handleSelect"
                    :default-active="nav.id"
                    :before-nav-change="beforeNavChange"
                    :toggle-active="nav.toggle">
                    <bk-navigation-menu-item
                        v-for="item in nav.list"
                        :key="item.name"
                        :has-child="item.children && !!item.children.length"
                        :group="item.group"
                        :icon="item.icon"
                        :disabled="item.disabled"
                        :url="item.url"
                        :id="item.name">
                        <span>{{item.name}}</span>
                        <div slot="child">
                            <bk-navigation-menu-item
                                :key="child.name"
                                v-for="child in item.children"
                                :has-child="child.children && !!child.children.length"
                                :id="child.name"
                                :disabled="child.disabled"
                                :icon="child.icon"
                                :url="child.url"
                                :title="child.title"
                                :default-active="child.active">
                                <span>{{child.name}}</span>
                            </bk-navigation-menu-item>
                        </div>
                    </bk-navigation-menu-item>
                </bk-navigation-menu>
            </template>
            <div class="monitor-navigation-content p20">
                <main class="main-content" v-bkloading="{ isLoading: mainContentLoading, opacity: 0 }">
                    <router-view :key="routerKey" v-show="!mainContentLoading" />
                </main>
            </div>
            <template slot="footer">
                <div class="monitor-navigation-footer">
                        
                </div>
            </template>
        </bk-navigation>
        <app-auth ref="bkAuth"></app-auth>
    </div>
</template>
<script>
    import { mapGetters } from 'vuex'
    
    import { bus } from '@/common/bus'

    export default {
        name: 'app',
        data () {
            return {
                routerKey: +new Date(),
                systemCls: 'mac',
                isDropdownShow: false,
                nav: {
                    list: [
                        {
                            name: '首页',
                            icon: 'icon-dashboard-shape',
                            url: 'mainpage'
                        },
                        {
                            name: 'ES',
                            icon: 'icon-data2-shape',
                            // group: true,
                            children: [
                                {
                                    name: 'ES集群管理',
                                    url: 'esinfo'
                                },
                                {
                                    name: 'ES集群纳管',
                                    url: 'esinput'
                                },
                                {
                                    name: 'ES集群部署',
                                    url: 'esnew'
                                },
            
                                // {
                                //     name: 'ES权限管理',
                                //     url: 'esrule'
                                // },
                                {
                                    name: 'ES执行记录',
                                    url: 'esrecord'
                                }
                            ]

                        },
                        {
                            name: 'Hadoop',
                            icon: 'icon-sitemap-shape',
                            children: [
                                {
                                    name: 'Hadoop集群管理',
                                    url: 'hadoopinfo'
                                },
                                {
                                    name: 'Hadoop集群纳管',
                                    url: 'hadoopinput'
                                },
                                {
                                    name: 'Hadoop集群部署',
                                    url: 'hadoopnew'
                                },

                                {
                                    name: 'Hadoop执行记录',
                                    url: 'hadooprecord'
                                }
                            ]
                        },
                        {
                            name: 'Kafka',
                            icon: 'icon-pipeline-shape',
                            children: [
                                {
                                    name: 'Kafka集群管理',
                                    url: 'kafkainfo'
                                },
                                {
                                    name: 'Kafka集群纳管',
                                    url: 'kafkainput'
                                },
                                {
                                    name: 'Kafka集群部署',
                                    url: 'kafkanew'
                                },
                                {
                                    name: 'Kafka执行记录',
                                    url: 'kafkarecord'
                                }
                            ]
                        }
                        // {
                        //     name: '管理',
                        //     icon: 'icon-cog-shape',
                        //     children: [
                        //         {
                        //             name: '执行记录',
                        //             url: 'taskrecord'
                        //         }
                        //     ]
                        // }
                    ],
                    toggle: false,
                    submenuActive: false,
                    title: 'Data Ops Platform'
                },
                header: {
                    list: [],
                    selectList: [],
                    active: 2,
                    bizId: 1
                },
                message: {
                    list: []
                },
                admin: {
                    list: [
                        '项目管理',
                        '权限中心',
                        '退出'
                    ]
                }
            }
        },
        computed: {
            ...mapGetters(['mainContentLoading', 'user']),
            curNav () {
                return {
                    nav: 'left-right',
                    needMenu: true,
                    name: '左右结构导航'
                }
            },
            curHeaderNav () {
                return this.header.list[this.header.active] || {}
            },
            curYear () {
                return (new Date()).getFullYear()
            }
        },
        watch: {
            '$route' () {
                this.nav.id = this.$route.meta ? this.$route.meta.matchRoute : this.$route.name
            }
        },
        created () {
            const platform = window.navigator.platform.toLowerCase()
            if (platform.indexOf('win') === 0) {
                this.systemCls = 'win'
            }
        },
        mounted () {
            const self = this
            bus.$on('show-login-modal', data => {
                self.$refs.bkAuth.showLoginModal(data)
            })
            bus.$on('close-login-modal', () => {
                self.$refs.bkAuth.hideLoginModal()
                setTimeout(() => {
                    window.location.reload()
                }, 0)
            })
        },
        methods: {
            /**
             * router 跳转
             *
             * @param {string} idx 页面指示
             */
            goPage (idx) {
                if (idx) {
                    this.$router.push({
                        name: idx
                    })
                }
            },
            dropdownShow () {
                this.isDropdownShow = true
            },
            dropdownHide () {
                this.isDropdownShow = false
            },
            triggerHandler (val) {
                this.$refs.dropdown.hide()
                if (val === 1) {
                    alert('跳转到 PC 端')
                } else {
                    alert('跳转到移动端')
                }
            },
            handleSelect (id, item) {
                this.nav.url = item.url
                this.nav.id = id
                if (item.url) {
                    this.goPage(item.url)
                }
            },
            handleToggle (v) {
                this.nav.toggle = v
            },
            beforeNavChange (newId, oldId) {
                // console.info(newId, oldId)
                return true
            }
        }
    }
</script>

<style lang="postcss">
@import './css/reset.css';
@import './css/app.css';

.main-content {
    min-height: 300px;
}
.split {
    margin-bottom: 15px;
}
.header-bussiness {
    margin-right: 50px;
}
.header-icon {
    margin-right: 8px;
    display: inline-block;
    color: #63656e;
    font-size: 16px;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    text-align: center;
    line-height: 32px;
}
.header-icon:hover {
    background: #f0f1f5;
    cursor: pointer;
}
.header-avatar {
    display: inline-block;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    font-size: 16px;
    color: #979ba5;
    line-height: 28px;
    text-align: center;
    margin-left: 8px;
    margin-right: 25px;
    background: #f0f1f5;
    border: 1px solid #eee;
    box-shadow: 0px 3px 6px 0px rgba(99, 101, 110, 0.06);
    cursor: pointer;
}
.monitor-navigation-header {
.bk-icon {
    vertical-align: middle;
}
}
/* 以下样式是为了适应例子父级的宽高而设置 */
.bk-navigation {
    outline: 1px solid #ebebeb;
.bk-navigation-wrapper {
    height: calc(100vh - 252px) !important;
}
}
/* 以上样式是为了适应例子父级的宽高而设置 */

@define-mixin defualt-icon-mixin $color: #768197 {
    color: $color;
    font-size: 16px;
    position: relative;
    height: 32px;
    width: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 8px;
}
@define-mixin is-left-mixin $needBgColor: true {
    color: #63656e;
&:hover {
     color: #3a84ff;
    @if $needBgColor {
        background: #f0f1f5;
    }
}
}
@define-mixin icon-hover-mixin {
    background: linear-gradient(
        270deg,
        rgba(37, 48, 71, 1) 0%,
        rgba(38, 50, 71, 1) 100%
    );
    border-radius: 100%;
    cursor: pointer;
    color: #d3d9e4;
}
@define-mixin popover-panel-mxin $width: 150px, $itemHoverColor: #3a84ff {
    width: $width;
    display: flex;
    flex-direction: column;
    background: #ffffff;
    border: 1px solid #e2e2e2;
    box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
    padding: 6px 0;
    margin: 0;
    color: #63656e;
    .nav-item {
        flex: 0 0 32px;
        display: flex;
        align-items: center;
        padding: 0 20px;
        list-style: none;
&:hover {
     color: $itemHoverColor;
     cursor: pointer;
     background-color: #f0f1f5;
 }
}
}
.monitor-navigation {
&-header {
     flex: 1;
     /* padding-left: 12px; */
     height: 100%;
     display: flex;
     align-items: center;
     font-size: 14px;
.header-nav {
    display: flex;
    padding: 0;
    margin: 0;
&-item {
     list-style: none;
     margin-right: 40px;
     color: #96a2b9;
&.item-active {
     color: #ffffff !important;
 }
&:hover {
     cursor: pointer;
     color: #d3d9e4;
 }
}
}
.header-title {
    color: #63656e;
    font-size: 16px;
    display: flex;
    align-items: center;
    margin-left: -6px;
&-icon {
     display: flex;
     align-items: center;
     width: 28px;
     height: 28px;
     font-size: 28px;
     color: #3a84ff;
     cursor: pointer;
 }
}
.header-select {
    width: 240px;
    margin-left: auto;
    margin-right: 34px;
    border: none;
    background: #252f43;
    color: #d3d9e4;
    box-shadow: none;
&.is-left {
     background: #f0f1f5;
     color: #63656e;
 }
}
.header-mind {
    @mixin defualt-icon-mixin;
&.is-left {
     @mixin is-left-mixin;
 }
&-mark {
     position: absolute;
     right: 8px;
     top: 8px;
     height: 7px;
     width: 7px;
     border: 1px solid #27334c;
     background-color: #ea3636;
     border-radius: 100%;
&.is-left {
     border-color: #f0f1f5;
 }
}
&:hover {
     @mixin icon-hover-mixin;
 }
}
.header-help {
    @mixin defualt-icon-mixin;
&.is-left {
     @mixin is-left-mixin;
 }
&:hover {
     @mixin icon-hover-mixin;
 }
}
.header-user {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #96a2b9;
.bk-icon {
    margin-left: 5px;
    font-size: 12px;
}
&.is-left {
     @mixin is-left-mixin false;
 }
&:hover {
     cursor: pointer;
     color: #d3d9e4;
 }
}
}
&-content {
     min-height: calc(100% - 84px);
     /* background: #ffffff; */
     /* box-shadow: 0px 2px 4px 0px rgba(25, 25, 41, 0.05); */
     /* border-radius: 2px; */
     /* border: 1px solid rgba(220, 222, 229, 1); */
 }
&-footer {
     height: 52px;
     width: 100%;
     margin: 32px 0 0;
     display: flex;
     align-items: center;
     justify-content: center;
     border-top: 1px solid #dcdee5;
     color: #63656e;
     font-size: 12px;
 }
&-message {
     display: flex;
     flex-direction: column;
     width: 360px;
     background-color: #ffffff;
     border: 1px solid #e2e2e2;
     border-radius: 2px;
     box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
     color: #979ba5;
     font-size: 12px;
.message-title {
    flex: 0 0 48px;
    display: flex;
    align-items: center;
    color: #313238;
    font-size: 14px;
    padding: 0 20px;
    margin: 0;
    border-bottom: 1px solid #f0f1f5;
}
.message-list {
    flex: 1;
    max-height: 450px;
    overflow: auto;
    margin: 0;
    display: flex;
    flex-direction: column;
    padding: 0;
&-item {
     display: flex;
     width: 100%;
     padding: 0 20px;
.item-message {
    padding: 13px 0;
    line-height: 16px;
    min-height: 42px;
    flex: 1;
    flex-wrap: wrap;
    color: #63656e;
}
.item-date {
    padding: 13px 0;
    margin-left: 16px;
    color: #979ba5;
}
&:hover {
     cursor: pointer;
     background: #f0f1f5;
 }
}
}
.message-footer {
    flex: 0 0 42px;
    border-top: 1px solid #f0f1f5;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #3a84ff;
}
}
&-nav {
     @mixin popover-panel-mxin;
 }
&-admin {
     @mixin popover-panel-mxin 170px #63656e;
 }
}
.tippy-popper {
.tippy-tooltip.navigation-message-theme {
    padding: 0;
    border-radius: 0;
    box-shadow: none;
}
}
</style>
