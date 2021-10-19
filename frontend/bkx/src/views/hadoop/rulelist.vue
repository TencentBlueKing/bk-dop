<template>
    <div class="exception-wrap">
        <bk-exception class="exception-wrap-item" type="403">
            <span>无业务权限</span>
            <div class="text-subtitle">你没有相应业务的访问权限，请前往申请相关业务权限</div>
            <div class="text-wrap">
                <span class="text-btn">去申请</span>
            </div>
        </bk-exception>
    </div>
</template>
<script>
    import { bkException } from '@tencent/bk-magic-vue'

    export default {
        components: {
            bkException
        }
    }
</script>
<style>
.exception-wrap .exception-wrap-item {
    border: 1px solid #DCDEE5;
    margin: 10px;
    height: 420px;
    padding-top: 22px;
}
.exception-wrap .exception-wrap-item .text-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    color: #3A84FF;
    font-size: 14px;
    margin-top: 12px;
}
.exception-wrap .exception-wrap-item .text-subtitle {
    color: #979BA5;
    font-size: 14px;
    text-align: center;
    margin-top: 14px;
}
.text-wrap .text-btn {
    margin: 0 5px;
}
.text-wrap .text-btn:hover {
    cursor: pointer;
}
</style>
