from __future__ import annotations

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.network.fastapi_websocket import FastAPIWebsocketParams
from pipecat.transports.services.daily import DailyParams


transport_params = {
    "daily": lambda: DailyParams(
        audio_in_enabled=True, audio_out_enabled=True, vad_analyzer=SileroVADAnalyzer()
    ),
    "twilio": lambda: FastAPIWebsocketParams(
        audio_in_enabled=True, audio_out_enabled=True, vad_analyzer=SileroVADAnalyzer()
    ),
    "webrtc": lambda: TransportParams(
        audio_in_enabled=True, audio_out_enabled=True, vad_analyzer=SileroVADAnalyzer()
    ),
}


