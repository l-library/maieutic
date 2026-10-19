import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import {RouterProvider} from 'react-router-dom';
import {ConversationRefreshProvider} from "@/context/conversations.tsx";
import {ErrorBoundary, getErrorMessage} from "react-error-boundary";
import router from './router.tsx'
import './token.css'

createRoot(document.getElementById('root')!).render(
    <ErrorBoundary fallbackRender={({error, resetErrorBoundary}) => (
        <div role="alert">
            <p>Something went wrong:</p>
            <pre>{getErrorMessage(error)}</pre>
            <button onClick={resetErrorBoundary}>Try again</button>
        </div>
    )}
    >
        <StrictMode>
            <ConversationRefreshProvider>
                <RouterProvider router={router}/>
            </ConversationRefreshProvider>
        </StrictMode>
    </ErrorBoundary>
)
