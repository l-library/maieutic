import {createBrowserRouter} from 'react-router-dom'
import {lazy, Suspense} from "react";
import PageLoading from "./components/PageLoading.tsx";

// 用suspense包裹，加载时显示为加载中
const withSuspense = (Component: React.ComponentType) => (
    <Suspense fallback={<PageLoading/>}>
        <Component/>
    </Suspense>
);

// 路由懒加载
const home = lazy(() => import('./routes/home'))
const history = lazy(() => import('./routes/history'))

// 创建路由
const router = createBrowserRouter([
    {
        path: '/',
        element: withSuspense(home)
    },
    {
        path: '/history',
        element: withSuspense(history)
    }
])

export default router;
