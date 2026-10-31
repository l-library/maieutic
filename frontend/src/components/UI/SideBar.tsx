import * as PI from "react-icons/pi"
import {Link} from "react-router-dom";
import History from "@/components/UI/History.tsx";
import {useConversationRefresh} from "@/context/conversationRefresh";
import type {components} from "@/api/types.ts";
import {conversationAPI} from "@/api/conversation.ts";
import {useConversationIdContext} from "@/context/currentConversation.ts";
import {useState} from "react";

type ConversationElement = components["schemas"]["ConversationElement"]

const SideBar = ({open, conversation_list}: { open: boolean, conversation_list: ConversationElement[] }) => {
    const {refresh} = useConversationRefresh();
    const {changeId} = useConversationIdContext();
    const [error, setError] = useState<string | null>(null);

    const create_conversation = async () => {
        const {data, error} = await conversationAPI.create_conversation();
        if (error) setError(JSON.stringify(error));
        else changeId((data ?? 1) as number);
    }

    if (error) return <div className="text-red-600">{error}</div>;

    return (
        <div className={'flex-none overflow-hidden border-r border-r-border transition-all duration-300 ' +
            (open ? 'w-sidebar' : 'w-0')}>
            {/* 侧边栏本体：高度整个屏幕 */}
            <nav className={'h-full w-sidebar p-1.5 bg-sidebar flex flex-col'}>
                <img src="/maieutic.png" alt="maieutic"/>
                <ul className="flex flex-col gap-2 flex-1 min-h-0">
                    <li>
                        <div className="menu-item hover:cursor-pointer" onClick={() => {
                            refresh();
                            create_conversation();
                        }}>
                            <PI.PiPlusCircle/>
                            新对话
                        </div>
                    </li>
                    <li>
                        <Link to='#' className={"menu-item"}>
                            <PI.PiChat/>
                            全部对话
                        </Link>
                    </li>
                    <hr className={"text-border"}/>
                    <li className="flex-1 min-h-0 overflow-hidden"><History conversations={conversation_list}/></li>
                </ul>
            </nav>
        </div>
    )
}

export default SideBar