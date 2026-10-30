import SideBar from '@/components/UI/SideBar'
import {Chat} from "@/components/UI/Chat.tsx";
import {Header} from "@/components/UI/Header.tsx";
import {useEffect, useState} from "react";
import {useConversationIdContext} from "@/context/currentConversation.ts";
import {useConversationRefresh} from "@/context/conversationRefresh.ts";
import {conversationAPI} from "@/api/conversation.ts";
import type {components} from "@/api/types.ts";

type ConversationElement = components["schemas"]["ConversationElement"]

const Home = () => {
    const [bar_open, change_open] = useState<boolean>(true);
    // 在 Home 就获取到对话列表，
    const [conversations, setConversations] = useState<ConversationElement[]>([]);
    const [error, setError] = useState<string | null>(null);
    const {refreshKey} = useConversationRefresh();
    useEffect(() => {
        let cancelled = false;
        conversationAPI.get_list().then(({data, error}) => {
            if (cancelled) return; // 挂载后不再刷新
            if (error) setError(JSON.stringify(error));
            else setConversations((data ?? []) as ConversationElement[]);
        });
        return () => {
            cancelled = true;
        };
    }, [refreshKey]);
    const current_conversation_id = useConversationIdContext().id;
    if (error) return <div className={"text-red-500"}>{error}</div>

    return (
        // h-dvh 让元素占满整个视图
        <div className="flex h-dvh bg-background">
            <SideBar open={bar_open} conversation_list={conversations}/>
            <div className="flex flex-col flex-1 min-w-0">
                <Header bar_open={bar_open} on_click={() => (change_open(!bar_open))}
                        conversation_list={conversations}/>
                <main className="flex-1 min-h-0">
                    <Chat conversation_id={current_conversation_id}/>
                </main>
            </div>
        </div>
    )
}

export default Home