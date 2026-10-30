import {type ReactNode, useState} from "react";
import {ConversationRefreshContext} from "@/context/conversationRefresh.ts";

// 用于包裹子组件
export const ConversationRefreshProvider = ({children}: { children: ReactNode }) => {
    const [refreshKey, setRefreshKey] = useState(0);
    return (
        <ConversationRefreshContext.Provider
            // 向所有后代提供Context值，提供两个值对应 RefreshContextValue
            value={{refreshKey, refresh: () => setRefreshKey((k) => k + 1)}}>
            {children}
        </ConversationRefreshContext.Provider>
    );
};