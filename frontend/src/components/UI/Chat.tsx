import {conversationAPI} from "@/api/conversation.ts";
import {Fragment, useEffect, useState} from "react";
import {Bubble} from "@/components/UI/Bubble.tsx";

type ToolCall = {
    id: string;
    type: string;
    function: { name: string; arguments: string };
};
type Message = { role: string, content: string, tool_calls?: ToolCall[], tool_call_id?: string } // tool_calls 可能存在
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
    }, [conversation_id]);
    const tool_id_res = new Map<String, String>();
    for (let m of messages) {
        if (m.tool_call_id) // 如果是某次 tool call 的结果
            tool_id_res.set(m.tool_call_id, m.content);
    }
    if (error) return <div className="text-red-600">{error}</div>;
    return (
        <ol className='flex flex-col h-full w-full overflow-y-auto list-none pl-0 m-0 px-4 py-3 gap-3'>
            {
                messages.map((m, i) => {
                        if (m.tool_call_id) // 工具调用结果不再单独占用一个气泡
                            return (<div key={i}></div>);
                        return (
                            <Fragment key={i}>
                                <li className='min-w-0'>
                                    {<Bubble role={m.role} content={m.content}/>}
                                </li>
                                {
                                    m.tool_calls?.map((tc) => (
                                            <li key={tc.id} className="min-w-0">
                                                <Bubble role="tool_calls"
                                                        content={tc.function.name}
                                                        append_inf={`arguments:\n${tc.function.arguments}\nresult:\n${tool_id_res.get(tc.id)}`}
                                                />
                                            </li>
                                        )
                                    )}
                            </Fragment>
                        )
                    }
                )
            }
        </ol>
    )
}
