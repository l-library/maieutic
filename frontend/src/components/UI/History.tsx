import type {components} from "@/api/types"
import * as dayjs from "dayjs";
import {useConversationIdContext} from "@/context/currentConversation.ts";

type ConversationElement = components["schemas"]["ConversationElement"]

const History = ({conversations}: { conversations: ConversationElement[] }) => {
    const {id, changeId} = useConversationIdContext();
    const padding_distance = '3';
    return (
        <ul className='flex flex-col h-full w-full overflow-x-auto'>
            {conversations.map((m) =>
                <li key={m.id}>
                    <div
                        className={(m.id === id ? "bg-highlight " : "") +
                            'flex gap-2 py-2 rounded items-center hover:bg-hover cursor-pointer border border-border text-text-secondary p-' + padding_distance}
                        onClick={() => {
                            changeId(m.id)
                        }}>
                        {String(m.title)}
                        <div className='text-time ml-auto'>
                            {dayjs.unix(m.change_time).format("YYYY-M-D H:m:s")}
                        </div>
                    </div>
                </li>
            )}
        </ul>
    )
        ;
}

export default History