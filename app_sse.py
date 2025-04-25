import uuid
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from sse_starlette.sse import EventSourceResponse
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

# In-memory session store: session_id -> SseServerTransport
sessions = {}

async def handle_sse(request: Request):
    print(f"[SERVER] handle_sse called")
    session_id = str(uuid.uuid4())
    print(f"[SERVER] New /sse connection, assigned session_id: {session_id}")
    transport = SseServerTransport(f"/messages/?session_id={session_id}")
    sessions[session_id] = transport

    import asyncio
    async def event_generator():
        print(f"[SERVER] event_generator entered for session_id: {session_id}")
        print(f"[SERVER] Sending endpoint event for session_id: {session_id}")
        yield f"event: endpoint\ndata: /messages/?session_id={session_id}\n\n"
        print(f"[SERVER] Starting MCP server for session_id: {session_id}")
        async def run_mcp():
            try:
                async with transport.connect_sse(request.scope, request.receive, request._send) as streams:
                    await request.app.state.mcp._mcp_server.run(
                        streams[0], streams[1], request.app.state.mcp._mcp_server.create_initialization_options()
                    )
            except Exception as e:
                print(f"[SERVER][ERROR] Exception in MCP server run: {e}")
            print(f"[SERVER] MCP server finished for session_id: {session_id}")
        # Run MCP server in background
        asyncio.create_task(run_mcp())
        # Yield periodic pings so SSE client stays alive
        import datetime
        while True:
            await asyncio.sleep(1)
            now = datetime.datetime.utcnow().isoformat()
            yield f"event: ping\ndata: {now}\n\n"

    return EventSourceResponse(event_generator())

async def handle_post_message(request: Request):
    session_id = request.query_params.get("session_id")
    print(f"[SERVER] Received POST to /messages/ with session_id: {session_id}")
    if not session_id or session_id not in sessions:
        print(f"[SERVER][ERROR] Invalid or missing session_id: {session_id}")
        return JSONResponse({"error": "Invalid or missing session_id"}, status_code=400)
    try:
        payload = await request.json()
        print(f"[SERVER] Payload: {payload}")
        method = payload.get("method")
        tool = payload.get("tool")
        args = payload.get("args", {})
        result = None
        if method == "tool" and tool:
            # Call the tool on the FastMCP instance (vulnerable)
            tool_fn = getattr(request.app.state.mcp, tool, None)
            if tool_fn:
                result = tool_fn(**args)
            elif hasattr(request.app.state.mcp, '_tools') and tool in request.app.state.mcp._tools:
                result = request.app.state.mcp._tools[tool](**args)
            else:
                result = f"Tool {tool} not found"
        else:
            result = "Invalid method or tool"
        print(f"[SERVER] Tool result: {result}")
        return JSONResponse({"result": result})
    except Exception as e:
        print(f"[SERVER][ERROR] Exception in handle_post_message: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

        return JSONResponse({"error": "Invalid or missing session_id"}, status_code=400)
    transport = sessions[session_id]
    try:
        response = await transport.handle_post_message(request)
        print(f"[SERVER] POST handled for session_id: {session_id}")
        return response
    except Exception as e:
        print(f"[SERVER][ERROR] Exception in handle_post_message: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

# Factory for Starlette app
def create_sse_server(mcp: FastMCP):
    app = Starlette(routes=[
        Route("/sse/", handle_sse, methods=["GET"]),
        Route("/messages/", handle_post_message, methods=["POST"]),
    ])
    app.state.mcp = mcp
    return app
