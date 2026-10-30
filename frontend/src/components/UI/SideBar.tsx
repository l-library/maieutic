import * as PI from "react-icons/pi"
import {Link} from "react-router-dom";
import History from "@/components/UI/History.tsx";
import {useConversationRefresh} from "@/context/conversationRefresh";
import type {components} from "@/api/types.ts";

type ConversationElement = components["schemas"]["ConversationElement"]

const SideBar = ({open, conversation_list}: { open: boolean, conversation_list: ConversationElement[] }) => {
    const {refresh} = useConversationRefresh();

    return (
        <div className={'flex-none overflow-hidden transition-all duration-300 ' +
            (open ? 'w-sidebar' : 'w-0')}>
            {/* 侧边栏本体：高度整个屏幕 */}
            <nav className={'h-full w-sidebar p-1.5 bg-sidebar flex flex-col'}>
                <img src="/maieutic.png" alt="maieutic"/>
                <ul className="flex flex-col gap-2 flex-1 min-h-0">
                    <li onClick={refresh}>
                        <Link to='#' className="menu-item">
                            <PI.PiPlusCircle/>
                            新对话
                        </Link>
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