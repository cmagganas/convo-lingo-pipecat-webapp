from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from pipecat_ai_small_webrtc_prebuilt.frontend import SmallWebRTCPrebuiltUI


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # SmallWebRTCPrebuiltUI is an ASGI app; mount without calling it
    app.mount("/", SmallWebRTCPrebuiltUI, name="webrtc-ui")
    return app


app = create_app()


