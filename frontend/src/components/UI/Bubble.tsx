import {useState} from "react";
import { PiCaretDown,PiCaretUp } from "react-icons/pi";

export const Bubble = ({role, content, append_inf}: { role: string, content: string, append_inf?: string }) => {
    const [isOpen, setOpen] = useState(false);

    const changeOpen = () => {
        setOpen(!isOpen);
    }
    let bubble_style = "rounded-2xl shadow shadow-border hover:brightness-90 p-3 ";
    let append_bubble_style;
    switch (role) {
        case "user":
            append_bubble_style = "ml-auto bg-bubble-u w-bubble-min";
            break;
        case "tool_calls": // 工具调用
            append_bubble_style = "mx-auto bg-bubble-t w-bubble-min text-secondary"
            break;
        case "tool": // 工具调用结果
            append_bubble_style = "mx-auto bg-bubble-t w-bubble-min";
            break;
        case "assistant":
            append_bubble_style = "mx-auto bg-background w-300";
            break;
        default:
            append_bubble_style = "self-center bg-warning"
            break;
    }

    if (role == "tool_calls") {
        return (
            <div className={bubble_style + append_bubble_style}>
                <div className='text-text-secondary text-xl rounded p-1 flex w-full font-bold'
                     onClick={changeOpen}>
                    <div className='self-center text-primary'>
                        TOOL
                    </div>
                    <div className="ml-auto p-2 rounded-xl">
                        {content}
                    </div>
                    <div className="pl-2 mr-auto self-center p-2 rounded-3xl hover:bg-hover">
                        {isOpen?<PiCaretUp/>:<PiCaretDown/>}
                    </div>
                </div>
                <div className='text-text' style={{display: isOpen ? 'block' : 'none'}}>
                    {append_inf}
                </div>
            </div>)
    }

    return (
        <div className={bubble_style + append_bubble_style}>
            {content}
        </div>
    )
}

// type ConversationElement = components["schemas"]["ChatCompletionAssistantMessageParam"]
