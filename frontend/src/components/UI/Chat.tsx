import {conversationAPI} from "@/api/conversation.ts";
import {useEffect, useState} from "react";
import {Bubble} from "@/components/UI/Bubble.tsx";

type Message = { role: string, content: string }
export const Chat = ({conversation_id}: { conversation_id: number }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [error, setError] = useState<string | null>(null);
    useEffect(() => {
        let cancelled = false;
        conversationAPI.get_conversation(conversation_id).then(({data, error}) => {
            if (cancelled) return;
            if (error) setError(JSON.stringify(error));
            else setMessages((data ?? []) as Message[]);
        });
        return () => {
            cancelled = true;
        };
    }, [conversation_id]); // 先用常数占位
    if (error) return <div className="text-red-600">{error}</div>;
    return (
        <ol className='flex flex-col h-full w-full overflow-y-auto list-none pl-0 m-0 px-4 py-3 gap-3'>
            {
                messages.map((m, i) =>
                    <li key={i} className='min-w-0'>
                        <Bubble role={m.role} content={m.content}/>
                    </li>
                )
            }
        </ol>
    )
}
