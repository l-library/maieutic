import asyncio
from fastapi import FastAPI
from app.agent.agent import agent

app = FastAPI()
_agent = agent()


@app.get("/")
def check_health():
    return {"status": "ok", "message": "Maieutic 服务已就绪"}


@app.get("/chat/")
def chat():
    return {
        "return": asyncio.run(
            _agent.core_loop(user_message="测试：请尝试通过网络搜索2026世界杯")
        )
    }
