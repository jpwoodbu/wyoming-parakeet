import argparse
import asyncio
import functools
import logging
import signal

import onnx_asr
from wyoming import server as wyoming_server

from wyoming_parakeet import handler


_LOGGER = logging.getLogger(__package__)


async def start(uri: str, quantization: str | None) -> None:
    # The handler seems to get re-created for every request, so we need to do
    # the expensive work of loading the model ahead and time and pass it in.
    _LOGGER.info("Loading model...")
    model = onnx_asr.load_model(
        f"{handler.REPO_ID}/{handler.MODEL_ID}", quantization=quantization
    )
    _LOGGER.info("Model loaded")

    model_lock = asyncio.Lock()
    server = wyoming_server.AsyncServer.from_uri(uri)
    _LOGGER.info(f"Starting server at {uri}")
    server_task = asyncio.create_task(
        server.run(
            functools.partial(handler.ParakeetEventHandler, model, model_lock)
        )
    )

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, server_task.cancel)
    loop.add_signal_handler(signal.SIGTERM, server_task.cancel)

    try:
        await server_task
    except asyncio.CancelledError:
        _LOGGER.info("Server stopped gracefully.")
    except Exception as e:
        _LOGGER.error(f"Server stopped due to an unexpected error: {e}")
        server_task.cancel()
        await asyncio.gather(server_task, return_exceptions=True)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s",
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--uri",
        default="tcp://0.0.0.0:10300",
        help="URI the Wyoming server should listen on",
    )
    parser.add_argument("-q", "--quantization", default=None, help="E.g. int8")
    args = parser.parse_args()

    try:
        asyncio.run(start(args.uri, args.quantization))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
