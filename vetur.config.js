/*
 * @Author       : Outsider
 * @Date         : 2023-11-28 15:18:14
 * @LastEditors  : Outsider
 * @LastEditTime : 2023-11-28 15:30:28
 * @Description  : In User Settings Edit
 * @FilePath     : \thesis\vetur.config.js
 */
// vetur.config.js
/** @type {import('vls').VeturConfig} */
module.exports = {
    // **optional** default: `{}`
    // override vscode settings
    // Notice: It only affects the settings used by Vetur.
    // settings: {
    //   "vetur.useWorkspaceDependencies": true,
    //   "vetur.experimental.templateInterpolationService": true
    // },
    // **optional** default: `[{ root: './' }]`
    // support monorepos
    projects: [
      './frontend', // Shorthand for specifying only the project root location
      {
        // **required**
        // Where is your project?
        // It is relative to `vetur.config.js`.
        root: './frontend',
        // **optional** default: `'package.json'`
        // Where is `package.json` in the project?
        // We use it to determine the version of vue.
        // It is relative to root property.
        package: './frontend/package.json',
        // **optional**
        // Where is TypeScript config file in the project?
        // It is relative to root property.
        tsconfig: './frontend/tsconfig.json',
        // **optional** default: `'./.vscode/vetur/snippets'`
        // Where is vetur custom snippets folders?
        snippetFolder: './frontend/.vscode/vetur/snippets',
        // **optional** default: `[]`
        // Register globally Vue component glob.
        // If you set it, you can get completion by that components.
        // It is relative to root property.
        // Notice: It won't actually do it. You need to use `require.context` or `Vue.component`
        globalComponents: [
          './frontend/src/components/**/*.vue'
        ]
      }
    ]
  }