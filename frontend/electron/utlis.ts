import path from 'path'
import { app } from "electron"


export const isDev = process.env.NODE_ENV === 'development';
console.log(isDev)
export const getPreloadPath = () => {
    return path.join(
        app.getAppPath(),
        isDev ? '.' : "..",
        "./dist-electron/preload.cjs" 

    )
}
