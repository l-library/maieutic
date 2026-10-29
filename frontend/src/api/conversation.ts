import {client} from "./request.ts";
import type {components} from "./types.ts"

export type InputMessage = components['schemas']['Message']

export const conversationAPI = {
    llm_alive: () => client.GET("/api/v1/"),

    get_conversation: (conversation_id: number) =>
        client.GET("/api/v1/conversation/get/{conversation_id}", {params: {path: {conversation_id}}}),

    llm_chat: (conversation_id: number, message: InputMessage, signal?: AbortSignal) =>
        client.POST("/api/v1/conversation/chat/{conversation_id}", {
            parseAs: "stream",
            body: message,
            params: {path: {conversation_id}},
            signal
        }),

    create_conversation: () =>
        client.GET("/api/v1/conversation/create"),

    get_list: () =>
        client.GET("/api/v1/conversation/list")
}
