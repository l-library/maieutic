import {useState} from "react";

export const ChatBox = ({send, is_disabled}: { send: (text:string) => void ,is_disabled:boolean}) => {
    const [input,set_input] = useState<string>("")

    return (
        <form className='flex gap-2 px-4 py-3'
                  onSubmit={(e) => {
                      e.preventDefault();
                      if (!input.trim() || is_disabled) return;
                      const text = input;
                      set_input("");
                      send(text);
                  }}>
                <input className='flex-1 min-w-0 rounded-2xl border-2 border-border px-3 py-2 bg-background'
                       value={input} onChange={(e) => set_input(e.target.value)}
                       placeholder="输入消息…" disabled={is_disabled}/>
                <button className='menu-item' type="submit" disabled={is_disabled}>发送</button>
            </form>
    )

}