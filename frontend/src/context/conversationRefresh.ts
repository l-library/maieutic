import {createContext, useContext} from "react";

type RefreshContextValue = {
   refreshKey: number,
   refresh: () => void // 刷新函数，消费者和生产者各取所需
};
// 用数字的变化表示上下文变化
const ConversationRefreshContext = createContext<RefreshContextValue | null>(null);

const useConversationRefresh = () => {
   const ctx = useContext(ConversationRefreshContext);
   if (!ctx) throw new Error("useConversationRefresh 必须在 ConversationRefreshProvider 内使用");
   return ctx;
};

export {ConversationRefreshContext, useConversationRefresh};