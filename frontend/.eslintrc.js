/*
 * @Author       : Outsider
 * @Date         : 2023-11-28 15:02:56
 * @LastEditors  : Outsider
 * @LastEditTime : 2023-12-08 11:19:33
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\frontend\.eslintrc.js
 */
module.exports = {
    "env": {
        "browser": true,
        "es2021": true
    },
    "extends": [
        "standard-with-typescript",
        "plugin:vue/vue3-essential",
        'eslint:recommended',
        'plugin:@typescript-eslint/recommended'
    ],
    "overrides": [
        {
            "env": {
                "node": true
            },
            "files": [
                ".eslintrc.{js,cjs}"
            ],
            "parserOptions": {
                "sourceType": "script"
            }
        }
    ],
    parser: '@typescript-eslint/parser',
    "parserOptions": {
        "ecmaVersion": "latest",
        "sourceType": "module",
        "project": path.join(__dirname, "tsconfig.json")
    },
    "plugins": [
        "vue",
        '@typescript-eslint'
    ],
    "rules": {
    }
}
