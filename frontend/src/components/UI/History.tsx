import {useState, useEffect} from "react";
import {conversationAPI} from "@/api/conversation.ts";
import type {components} from "@/api/types"
import {useConversationRefresh} from "@/context/conversationRefresh";
import { Link } from "react-router-dom";
import * as dayjs from "dayjs";

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
    if (error) return <div className={"text-red-500"}>{error}</div>
    const padding_distance = '3';
    return (
        <ul className='flex flex-col h-full w-full overflow-x-auto'>
            {conversations.map((m) =>
                <li key={m.id}>
                    <Link to='#' className={'flex gap-2 py-2 rounded items-center hover:bg-hover border border-border text-text-secondary p-'+padding_distance}>
                        {String(m.title)}
                        <div className='text-time ml-auto'>
                            {dayjs.unix(m.change_time).format("YYYY-M-D H:m:s")}
                        </div>
                    </Link>
                </li>
            )}
        </ul>
    );
}

export default History