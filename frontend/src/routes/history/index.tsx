import {useEffect, useState} from "react";
import type {components} from "@/api/types.ts";
import {useConversationRefresh} from "@/context/conversationRefresh.ts";
import {conversationAPI} from "@/api/conversation.ts";
import  History from "@/components/UI/History.tsx";
import {Link} from "react-router-dom";
import { IoIosArrowBack } from "react-icons/io";

type ConversationElement = components["schemas"]["ConversationElement"]
const HistoryConversations = () => {
    const [error, setError] = useState<string | null>(null);
    const {refreshKey} = useConversationRefresh();
    const [conversations, setConversations] = useState<ConversationElement[]>([]);
    useEffect(() => {
        let cancelled = false;
        conversationAPI.get_list().then(({data, error}) => {
            if (cancelled)
                return;
            if (error) setError(JSON.stringify(error));
            else setConversations((data ?? []) as ConversationElement[]);
        });
        return () => {
            cancelled = true;
        };
    }, [refreshKey]);
    if (error) return <div className={"text-red-500"}>{error}</div>
    return (
        <div className="flex h-dvh bg-background min-h-0 overflow-hidden">
            <Link to='/' className="flex absolute cursor-pointer left-2 top-2 size-10 z-10 bg-secondary/50 shadow-4xl hover:bg-hover border border-primary rounded-full">
                <IoIosArrowBack className="mx-auto my-auto size-fit"/>
            </Link>
            <History conversations={conversations} in_single_page={true}/>
        </div>
    )
};

export default HistoryConversations;