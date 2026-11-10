import {type ReactNode, useEffect, useState} from "react";
import {currentConversation} from "@/context/currentConversation.ts";
import {conversationAPI} from "@/api/conversation.ts";
import PageLoading from "@/components/PageLoading.tsx";

// 用于包裹子组件
export const CurrentConversationProvider = ({children}: { children: ReactNode }) => {
    // 默认为 1，所以必须保证后端至少有ID为1的对话
    const [id, changeId] = useState(1);
    useEffect(() => {
        let cancelled = false;
        conversationAPI.get_list().then(({data}) => {
            if (cancelled || !data?.length) return;
            const newest = data.reduce((a, b) => (b.change_time > a.change_time ? b : a));
            changeId(newest.id);
        })
    }, []);

    // 如果id不确定，就只显示加载页面
    if (id === null) return <PageLoading/>

    return (
        <currentConversation.Provider
            // 向所有后代提供Context值，提供两个值对应 RefreshContextValue
            value={{id, changeId: (new_id) => changeId(() => new_id)}}>
            {children}
        </currentConversation.Provider>
    );
};