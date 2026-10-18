import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import {RouterProvider} from 'react-router-dom';
import {ConversationRefreshProvider} from "@/context/conversations.tsx";
import router from './router.tsx'
import './token.css'

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ConversationRefreshProvider>
            <RouterProvider router={router}/>
        </ConversationRefreshProvider>
    </StrictMode>,
)
