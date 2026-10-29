export type ToolCall = {
    id: string;
    type: string;
    function: { name: string; arguments: string };
};
export type Chunk = { type: "reasoning" | "assistant" | "tool"| "tool_calls"; content: string; tool_calls?:ToolCall };

// SSE 解析器
export async function* readSSE(body: ReadableStream<Uint8Array>): AsyncGenerator<Chunk> {
  const reader = body.getReader();
  const decoder = new TextDecoder();       // 处理多字节 UTF-8 被拆开的情况
  let buf = "";
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true }); // 解码

      let sep: number;
      while ((sep = buf.indexOf("\n\n")) !== -1) {   // 攒够一帧
        const frame = buf.slice(0, sep);
        buf = buf.slice(sep + 2);

        const data = frame
          .split("\n")
          .filter((l) => l.startsWith("data:"))       // `: ping` 注释行自然被滤掉
          .map((l) => l.slice(5).replace(/^ /, ""))   // 去掉 "data:" 和一个可选空格
          .join("\n");
        if (!data) continue;

        yield JSON.parse(data) as Chunk;
      }
    }
  } finally {
    reader.releaseLock();
  }
}