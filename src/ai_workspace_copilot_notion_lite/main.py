from ai_workspace_copilot_notion_lite.routers.wm_router import wm_router
from ai_workspace_copilot_notion_lite.routers.workspace_router import workspace_router
from ai_workspace_copilot_notion_lite.routers.auth_router import auth_router
from fastapi import FastAPI
from fastapi.responses import JSONResponse



app = FastAPI(title="Ai Workspace Copilot")

app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(wm_router)

@app.get("/")
async def get_root():
    return JSONResponse(
        status_code=200,
        content={"detail" : "running"}
    )