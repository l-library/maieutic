import {createContext, useContext} from "react";

type conversationIdRefresh = {
    id: number,
    changeId: (new_id: number) => void
};

export const currentConversation = createContext<conversationIdRefresh | null>(null);

export const useConversationIdContext = () => {
    const ctx = useContext(currentConversation);
    if (!ctx) throw new Error("currentConversation 必须在 CurrentConversationProvider 内使用");
    return ctx;
};