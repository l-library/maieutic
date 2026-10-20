export const Bubble = ({role, content}: { role: string, content: string }) => {
    let bubble_style = "rounded-2xl shadow shadow-border hover:brightness-90 p-3 ";
    let append_bubble_style = "";
    switch (role) {
        case "user":
            append_bubble_style = "ml-auto bg-bubble-u w-bubble-min";
            break;
        case "tool":
            // TODO: 优化 tool 展示
            append_bubble_style = "mx-auto bg-primary w-bubble-min";
            break;
        case "assistant":
            append_bubble_style = "mx-auto bg-background w-300";
            break;
        default:
            append_bubble_style = "self-center bg-warning"
            break;
    }

    return (
        <div className={bubble_style + append_bubble_style}>
            {content}
        </div>
    )
}

// type ConversationElement = components["schemas"]["ChatCompletionAssistantMessageParam"]
