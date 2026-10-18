import {useState, useEffect} from "react";
import {conversationAPI} from "@/api/conversation.ts";
import type {components} from "@/api/types"
import {useConversationRefresh} from "@/context/conversationRefresh";
import { Link } from "react-router-dom";

type ConversationElement = components["schemas"]["ConversationElement"]

const History = () => {
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
    // TODO: 错误显示组件
    if (error) return <div className={"text-red-500"}>{error}</div>
    return (
        // TODO: Conversation 时间字段 自动命名
        <ul className='flex flex-col h-full w-full overflow-x-auto'>
            {conversations.map((m) =>
                <li key={m.id}>
                    <Link to='#' className='flex gap-2 py-2 rounded items-center hover:bg-hover border border-border p-3'>
                        {String(m.title)}
                    </Link>
                </li>
            )}
        </ul>
    );
}

export default History