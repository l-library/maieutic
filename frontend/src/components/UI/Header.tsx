import * as PI from "react-icons/pi"
import * as HI from "react-icons/hi2"
import {useConversationIdContext} from "@/context/currentConversation.ts";
import type {components} from "@/api/types"

type ConversationElement = components["schemas"]["ConversationElement"]

export const Header =
    ({bar_open, on_click, conversation_list}: {
        bar_open: boolean,
        on_click: () => void,
        conversation_list: ConversationElement[]
    }) => {
        // 对话名称的刷新
        const {id} = useConversationIdContext();
        const conv_name = conversation_list.find(c => c.id === id)?.title || `${id}`

        return (
            // none 固定宽高
            <div className="flex-none bg-white flex w-full h-15 border-b border-b-border items-center p-2">
                <button
                    className="flex items-center justify-center size-10 text-xl hover:bg-hover cursor-pointer"
                    onClick={on_click}
                >
                    {bar_open ? <PI.PiSidebar/> : <HI.HiBars3/>}
                </button>
                <div className="flex items-center text-xl p-2">
                    {conv_name}
                </div>
            </div>
        )
    }