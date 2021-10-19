/**
 * @file ajax handler for dev
 * @author
 */

import path from 'path'
import fs from 'fs'
import url from 'url'
import queryString from 'querystring'
import chalk from 'chalk'
import devEnv from './dev.env'

const mockReqHandler = (req, mockParamValue) => {
    // mockFile replace 去掉 最后的 /，例如 /a/b/c/ => /a/b/c
    const mockFilePath = path.join(__dirname, '../mock/ajax', mockParamValue.replace(/\/+$/, '')) + '.js'
    if (!fs.existsSync(mockFilePath)) {
        return false
    }

    console.log(chalk.magenta('Mock File Query: ', mockParamValue))
    console.log(chalk.magenta('Mock File Path: ', mockFilePath))

    delete require.cache[require.resolve(mockFilePath)]
    return require(mockFilePath)
}

export default async function ajaxMiddleWare (req, res, next) {
    // eslint-disable-next-line node/no-deprecated-api
    let query = url.parse(req.url).query

    if (!query) {
        return next()
    }

    query = queryString.parse(query)

    const mockParamValue = query[JSON.parse(devEnv.AJAX_MOCK_PARAM)]
    // 不是 mock 请求
    if (!mockParamValue) {
        return next()
    } else {
        const postData = req.body || ''
        const mockDataHandler = mockReqHandler(req, mockParamValue)

        if (!mockDataHandler) {
            res.status(404).end()
            return
        }

        let data = await mockDataHandler.response(query, postData, req)

        if (data.statusCode) {
            res.status(data.statusCode).end(JSON.stringify(data))
            return
        }

        let contentType = req.headers['Content-Type']

        // 返回值未指定内容类型，默认按 JSON 格式处理返回
        if (!contentType) {
            contentType = 'application/json;charset=UTF-8'
            req.headers['Content-Type'] = contentType
            res.setHeader('Content-Type', contentType)
            data = JSON.stringify(data || {})
        }

        res.end(data)

        return next()
    }
}
