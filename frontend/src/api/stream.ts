import {type Chunk, readSSE} from "@/api/sse.ts";
import {conversationAPI} from "@/api/conversation.ts";
import type {InputMessage} from "@/api/conversation.ts";

export async function* stream(
    conversation_id: number,
    message: InputMessage,
    signal?: AbortSignal
): AsyncGenerator<Chunk> {
    const {data, error} = await conversationAPI.llm_chat(conversation_id, message, signal);
    if (error || !data) throw new Error(`chat failed: ${JSON.stringify(error)}`);
    yield* readSSE(data);
}