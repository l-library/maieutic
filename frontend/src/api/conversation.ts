import {client} from "./request.ts";
import type {components} from "./types.ts"

type Message = components['schemas']['Message']

export const conversationAPI = {
    llm_alive: () => client.GET("/api/v1/"),

    get_conversation: ( conversation_id: number )=>
                       client.GET("/api/v1/conversation/{conversation_id}",{params:{path:{conversation_id}}}),

    llm_chat: (conversation_id:number, message:Message)=>
        client.POST("/api/v1/conversation/chat/{conversation_id}",{body:message,params:{path:{conversation_id}}}),

    create_conversation: ()=>
        client.GET("/api/v1/conversation/create")
}
