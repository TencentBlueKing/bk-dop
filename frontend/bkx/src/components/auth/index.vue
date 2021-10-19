<template>
    <div class="bk-login-dialog" v-if="isShow">
        <div class="bk-login-wrapper ">
            <iframe :src="iframeSrc" scrolling="no" border="0" :width="iframeWidth" :height="iframeHeight"></iframe>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'app-auth',
        data () {
            return {
                iframeSrc: '',
                iframeWidth: 500,
                iframeHeight: 500,
                isShow: false
            }
        },
        methods: {
            hideLoginModal () {
                this.isShow = false
            },
            showLoginModal (data) {
                let url = data.login_url
                if (!url) {
                    const callbackUrl = `${location.origin}/static/login_success.html?is_ajax=1`
                    url = `${window.PROJECT_CONFIG.BKPAAS_URL}login/plain/?c_url=${callbackUrl}`
                }
                this.iframeSrc = url
                const iframeWidth = data.width
                if (iframeWidth) {
                    this.iframeWidth = iframeWidth
                }
                const iframeHeight = data.height
                if (iframeHeight) {
                    this.iframeHeight = iframeHeight
                }
                setTimeout(() => {
                    this.isShow = true
                }, 1000)
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
