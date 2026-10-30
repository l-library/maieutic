import {type ReactNode, useState} from "react";
import {currentConversation} from "@/context/currentConversation.ts";

// 用于包裹子组件
export const CurrentConversationProvider = ({children}: { children: ReactNode }) => {
    // 默认为 1，所以必须保证后端至少有ID为1的对话
    // TODO: 后端种子对话
    const [id, changeId] = useState(1);
    return (
        <currentConversation.Provider
            // 向所有后代提供Context值，提供两个值对应 RefreshContextValue
            value={{id, changeId: (new_id) => changeId(() => new_id)}}>
            {children}
        </currentConversation.Provider>
    );
};