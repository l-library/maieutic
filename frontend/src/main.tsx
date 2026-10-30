import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import {RouterProvider} from 'react-router-dom';
import {ConversationRefreshProvider} from "@/context/Conversations.tsx";
import {ErrorBoundary, getErrorMessage} from "react-error-boundary";
import router from './router.tsx'
import './token.css'
import {CurrentConversationProvider} from "@/context/CurrentConversationProvider.tsx";

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
                <CurrentConversationProvider>
                    <RouterProvider router={router}/>
                </CurrentConversationProvider>
            </ConversationRefreshProvider>
        </StrictMode>
    </ErrorBoundary>
)
