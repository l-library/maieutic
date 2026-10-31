import {conversationAPI} from "@/api/conversation.ts";
import {Fragment, useEffect, useState} from "react";
import {Bubble} from "@/components/UI/Bubble.tsx";
import {stream} from "@/api/stream"
import type {Chunk} from "@/api/sse.ts";
import {ChatBox} from "@/components/UI/ChatBox.tsx";
import {useConversationRefresh} from "@/context/conversationRefresh.ts";

type ToolCall = {
    id: string;
    type: string;
    function: { name: string; arguments: string };
};
type Message = { role: string, content: string, tool_calls?: ToolCall[], tool_call_id?: string } // tool_calls 可能存在
export const Chat = ({conversation_id}: { conversation_id: number }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [streaming, set_streaming] = useState<Message | null>(null); // 正在拼的气泡
    const [pending, set_pending] = useState(false);
    const {refresh} = useConversationRefresh();

    // 获取 chunk 的 roll
    const role_of = (t: Chunk["type"]) =>
        t === "tool_calls" ? "tool_calls" : t === "tool" ? "tool" : t === "reasoning" ? "reasoning" : "assistant";

    // 获取对话
    const load = async () => {
        const {data, error} = await conversationAPI.get_conversation(conversation_id);
        if (error) setError(JSON.stringify(error));
        else setMessages((data ?? []) as Message[]);
    };

    // 输入：用户输入
    // 将用户输入发送到后端，并触发流式输出
    const chat = async (text: string) => {
        set_pending(true);
        setError(null);
        setMessages((prev) => [...prev, {role: "user", content: text}]); // 先把用户消息贴到 messages 里
        let acc: Message | null = null; // 累加器，累计流式到达的消息
        try {
            for await (const c of stream(conversation_id, {message: text})) {
                if (c.type === "title") {
                    refresh();
                    continue;
                }
                const role = role_of(c.type);
                // tool 的 content 可能是数组/对象（Web_Extract 返回 list）
                const content = typeof c.content === "string" ? c.content : JSON.stringify(c.content);
                if (acc && acc.role === role) {
                    acc.content += content;               // 同类型：累加到当前气泡
                } else {
                    if (acc) {                            // 类型切换：把上一段定格进历史
                        const done = acc;
                        setMessages((prev) => [...prev, done]);
                    }
                    acc = {role, content};                 // 开新气泡
                }
                set_streaming({...acc});             // 每次覆盖，触发重渲染
            }
        } catch (e) {
            setError(String(e));
        } finally {
            const done = acc;
            if (done) setMessages((prev) => [...prev, done]);
            set_streaming(null);
            set_pending(false);
            await load();                            // 用落库结果对齐（补齐 tool_call_id、去掉临时气泡）
        }
    };
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
    const tool_id_res = new Map<string, string>();
    for (let m of messages) {
        if (m.tool_call_id) // 如果是某次 tool call 的结果
            tool_id_res.set(m.tool_call_id, m.content);
    }
    if (error) return <div className="text-red-600">{error}</div>;
    return (
        <div className="flex flex-col h-full w-full">
            <ol className='flex flex-col flex-1 min-h-0 overflow-y-auto list-none pl-0 m-0 px-4 py-3 gap-3'>
                {messages.map((m, i) => {
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
                )}
                {streaming && (
                    <li className='min-w-0'>
                        <Bubble role={streaming.role} content={streaming.content}/>
                    </li>
                )/*若有流式，则给流式单独开一个气泡*/}
            </ol>
            <ChatBox send={chat} is_disabled={pending}/>
        </div>
    );
}
