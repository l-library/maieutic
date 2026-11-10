import type {components} from "@/api/types"
import dayjs from "dayjs";
import {useConversationIdContext} from "@/context/currentConversation.ts";

type ConversationElement = components["schemas"]["ConversationElement"]

const Day = {
    today: "今天",
    yesterday: "昨天",
    this_month: "本月",
    this_year: "今年",
    earlier: "更早",
} as const;

type Day = (typeof Day)[keyof typeof Day];

const History = ({conversations}: { conversations: ConversationElement[] }) => {
    const {id, changeId} = useConversationIdContext();
    const padding_distance = '3';

    const groupTime = (time: number): Day => {
        // 如果是在24小时以内
        const current_time = dayjs(new Date());
        const conv_time = dayjs.unix(time);
        if (current_time.isSame(conv_time, "day"))
            return Day.today;
        else if (current_time.isSame(conv_time.subtract(1, "day"), "day"))
            return Day.yesterday;
        else if (current_time.isSame(conv_time, "month"))
            return Day.this_month;
        else if (current_time.isSame(conv_time, "year"))
            return Day.this_year;
        return Day.earlier;
    }

    const getFormatedTime = (time: number) => {
        const group = groupTime(time);
        switch (group) {
            case Day.today:
                return dayjs.unix(time).format("HH:mm");
            case Day.yesterday:
                return "昨天";
            case Day.this_month:
            case Day.this_year:
                return dayjs.unix(time).format("MM-DD");
            case Day.earlier:
                return dayjs.unix(time).format("YYYY-MM");
        }
    }
    return (
        <ul className='flex flex-col h-full w-full overflow-x-auto'>
            {// 按更改时间排序，用 toSorted 避免修改原 props
                conversations.toSorted((a, b) => b.change_time - a.change_time).map((m, i, arr) => {
                    const day = groupTime(m.change_time);
                    // 只要昨天和今天的类型不一样，就需要新的分隔符（或者是在列表的开始）
                    const isNewGroup = i === 0 || groupTime(arr[i - 1].change_time) !== day;
                    return (
                        <li key={m.id}>
                            {isNewGroup && <div className="flex p-1.5 text-text bg-border border-slate-400 border rounded-xl">{day}</div>}
                            <div
                                className={(m.id === id ? "bg-highlight " : "") +
                                    'flex gap-2 py-2 rounded items-center hover:bg-hover cursor-pointer border border-border text-text-secondary p-' + padding_distance}
                                onClick={() => changeId(m.id)}>
                                {String(m.title)}
                                <div className='text-time ml-auto'>{getFormatedTime(m.change_time)}</div>
                            </div>
                        </li>
                    )
                })}
        </ul>
    )
}

export default History