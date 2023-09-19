"""
A controller manages distributed workers.
It sends worker addresses to clients.
"""
import argparse
import asyncio
import dataclasses
from enum import Enum, auto
import json
import logging, logging.handlers
import time
from typing import List, Union
import threading

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import numpy as np
import requests
import uvicorn

from fastchat.constants import (
    CONTROLLER_HEART_BEAT_EXPIRATION,
    WORKER_API_TIMEOUT,
    ErrorCode,
    SERVER_ERROR_MSG,
)
from fastchat.utils import build_logger



class DispatchMethod(Enum):
    LOTTERY = auto()
    SHORTEST_QUEUE = auto()

    @classmethod
    def from_str(cls, name):
        if name == "lottery":
            return cls.LOTTERY
        elif name == "shortest_queue":
            return cls.SHORTEST_QUEUE
        else:
            raise ValueError(f"Invalid dispatch method")


@dataclasses.dataclass
class WorkerInfo:
    model_names: List[str]
    speed: int
    queue_length: int
    check_heart_beat: bool
    last_heart_beat: str


def heart_beat_controller(controller):
    while True:
        time.sleep(CONTROLLER_HEART_BEAT_EXPIRATION)
        controller.remove_stable_workers_by_expiration()


class Controller:
    def __init__(self, dispatch_method: str):
        # Dict[str -> WorkerInfo]
        self.worker_info = {}
        self.dispatch_method = DispatchMethod.from_str(dispatch_method)

        self.heart_beat_thread = threading.Thread(
            target=heart_beat_controller, args=(self,)
        )
        self.heart_beat_thread.start()

    def register_worker(
        self, worker_name: str, check_heart_beat: bool, worker_status: dict
    ):
        if worker_name not in self.worker_info:
            logger.info(f"Register a new worker: {worker_name}")
        else:
            logger.info(f"Register an existing worker: {worker_name}")

        if not worker_status:
            worker_status = self.get_worker_status(worker_name)
        if not worker_status:
            return False

        self.worker_info[worker_name] = WorkerInfo(
            worker_status["model_names"],
            worker_status["speed"],
            worker_status["queue_length"],
            check_heart_beat,
            time.time(),
        )

        logger.info(f"Register done: {worker_name}, {worker_status}")
        return True

    def get_worker_status(self, worker_name: str):
        try:
            r = requests.post(worker_name + "/worker_get_status", timeout=5)
        except requests.exceptions.RequestException as e:
            logger.error(f"Get status fails: {worker_name}, {e}")
            return None

        if r.status_code != 200:
            logger.error(f"Get status fails: {worker_name}, {r}")
            return None

        return r.json()

    def remove_worker(self, worker_name: str):
        del self.worker_info[worker_name]

    def refresh_all_workers(self):
        old_info = dict(self.worker_info)
        self.worker_info = {}

        for w_name, w_info in old_info.items():
            if not self.register_worker(w_name, w_info.check_heart_beat, None):
                logger.info(f"Remove stale worker: {w_name}")

    def list_models(self):
        model_names = set()

        for w_name, w_info in self.worker_info.items():
            model_names.update(w_info.model_names)

        return list(model_names)

    def get_worker_address(self, model_name: str):
        if self.dispatch_method == DispatchMethod.LOTTERY:
            worker_names = []
            worker_speeds = []
            for w_name, w_info in self.worker_info.items():
                if model_name in w_info.model_names:
                    worker_names.append(w_name)
                    worker_speeds.append(w_info.speed)
            worker_speeds = np.array(worker_speeds, dtype=np.float32)
            norm = np.sum(worker_speeds)
            if norm < 1e-4:
                return ""
            worker_speeds = worker_speeds / norm
            if True:  # Directly return address
                pt = np.random.choice(np.arange(len(worker_names)), p=worker_speeds)
                worker_name = worker_names[pt]
                return worker_name

            # Check status before returning
            while True:
                pt = np.random.choice(np.arange(len(worker_names)), p=worker_speeds)
                worker_name = worker_names[pt]

                if self.get_worker_status(worker_name):
                    break
                else:
                    self.remove_worker(worker_name)
                    worker_speeds[pt] = 0
                    norm = np.sum(worker_speeds)
                    if norm < 1e-4:
                        return ""
                    worker_speeds = worker_speeds / norm
                    continue
            return worker_name
        elif self.dispatch_method == DispatchMethod.SHORTEST_QUEUE:
            worker_names = []
            worker_qlen = []
            for w_name, w_info in self.worker_info.items():
                if model_name in w_info.model_names:
                    worker_names.append(w_name)
                    worker_qlen.append(w_info.queue_length / w_info.speed)
            if len(worker_names) == 0:
                return ""
            min_index = np.argmin(worker_qlen)
            w_name = worker_names[min_index]
            self.worker_info[w_name].queue_length += 1
            logger.info(
                f"count: {len(worker_names)}, max_queue_lens: {max(worker_qlen)}, ret: {w_name}"
            )
            return w_name
        else:
            raise ValueError(f"Invalid dispatch method: {self.dispatch_method}")

    def receive_heart_beat(self, worker_name: str, queue_length: int):
        if worker_name not in self.worker_info:
            logger.info(f"Receive unknown heart beat. {worker_name}")
            return False

        self.worker_info[worker_name].queue_length = queue_length
        self.worker_info[worker_name].last_heart_beat = time.time()
        logger.info(f"Receive heart beat. {worker_name}")
        return True

    def remove_stable_workers_by_expiration(self):
        expire = time.time() - CONTROLLER_HEART_BEAT_EXPIRATION
        to_delete = []
        for worker_name, w_info in self.worker_info.items():
            if w_info.check_heart_beat and w_info.last_heart_beat < expire:
                to_delete.append(worker_name)

        for worker_name in to_delete:
            self.remove_worker(worker_name)

    def handle_no_worker(self, params):
        logger.info(f"no worker: {params['model']}")
        ret = {
            "text": SERVER_ERROR_MSG,
            "error_code": ErrorCode.CONTROLLER_NO_WORKER,
        }
        return json.dumps(ret).encode() + b"\0"

    def handle_worker_timeout(self, worker_address):
        logger.info(f"worker timeout: {worker_address}")
        ret = {
            "text": SERVER_ERROR_MSG,
            "error_code": ErrorCode.CONTROLLER_WORKER_TIMEOUT,
        }
        return json.dumps(ret).encode() + b"\0"

    # Let the controller act as a worker to achieve hierarchical
    # management. This can be used to connect isolated sub networks.
    def worker_api_get_status(self):
        model_names = set()
        speed = 0
        queue_length = 0

        for w_name, w_info in self.worker_info.items():
            worker_status = self.get_worker_status(w_name)
            if worker_status is not None:
                model_names.update(worker_status["model_names"])
                speed += worker_status["speed"]
                queue_length += worker_status["queue_length"]

        return {
            "model_names": list(model_names),
            "speed": speed,
            "queue_length": queue_length,
        }

    def worker_api_generate_stream(self, params):
        worker_addr = self.get_worker_address(params["model"])
        if not worker_addr:
            yield self.handle_no_worker(params)

        try:
            response = requests.post(
                worker_addr + "/worker_generate_stream",
                json=params,
                stream=True,
                timeout=WORKER_API_TIMEOUT,
            )
            for chunk in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
                if chunk:
                    yield chunk + b"\0"
        except requests.exceptions.RequestException as e:
            yield self.handle_worker_timeout(worker_addr)

    def worker_api_generate(self, params):
        worker_addr = self.get_worker_address(params["model"])
        if not worker_addr:
            return self.handle_no_worker(params)

        try:
            response = requests.post(
                worker_addr + "/worker_generate",
                json=params,
                timeout=WORKER_API_TIMEOUT,
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return self.handle_worker_timeout(worker_addr)


app = FastAPI()


@app.post("/register_worker")
async def register_worker(request: Request):
    # logger.info("Request >> /register_worker")
    data = await request.json()
    controller.register_worker(
        data["worker_name"], data["check_heart_beat"], data.get("worker_status", None)
    )
    # logger.info("Response << /register_worker")
    return {"status": "ok"}


@app.post("/refresh_all_workers")
async def refresh_all_workers():
    return {"message": "This is a deprecated API. Do not call it."}
    models = controller.refresh_all_workers()
    return {"status": "ok"}


@app.post("/list_models")
async def list_models():
    # logger.info("Request >> /list_models")
    models = controller.list_models()
    # logger.info("Response << /list_models")
    return {"models": models}


@app.post("/get_worker_address")
async def get_worker_address(request: Request):
    # logger.info("Request >> /get_worker_address")
    data = await request.json()
    addr = controller.get_worker_address(data["model"])
    # logger.info("Response << /get_worker_address")
    return {"address": addr}


@app.post("/receive_heart_beat")
async def receive_heart_beat(request: Request):
    # logger.info("Request >> /receive_heart_beat")
    data = await request.json()
    exist = controller.receive_heart_beat(data["worker_name"], data["queue_length"])
    # logger.info("Response << /receive_heart_beat")
    return {"exist": exist}


@app.post("/worker_generate_stream")
async def worker_api_generate_stream(request: Request):
    # logger.info("Request >> /worker_generate_stream")
    params = await request.json()
    generator = controller.worker_api_generate_stream(params)
    # logger.info("Response << /worker_generate_stream")
    return StreamingResponse(generator)


@app.post("/worker_generate")
async def worker_api_generate(request: Request):
    return {"message": "This is a deprecated API. Do not call it."}
    logger.info("Request >> /worker_generate")
    params = await request.json()
    result = controller.worker_api_generate(params)
    logger.info("Response << /worker_generate")
    return result


@app.post("/worker_get_status")
async def worker_api_get_status(request: Request):
    # logger.info("Request >> /worker_get_status")
    # logger.info("Response << /worker_get_status")
    return controller.worker_api_get_status()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--logger_dir", type=str, default="logs")
    parser.add_argument(
        "--dispatch-method",
        type=str,
        choices=["lottery", "shortest_queue"],
        default="shortest_queue",
    )
    args = parser.parse_args()
    import os
    if not args.logger_dir:
        args.logger_dir = os.path.join("logs/controller", time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))

    os.makedirs(args.logger_dir, exist_ok=True)
    logger = build_logger("model_controller", os.path.join(args.logger_dir ,f"model_controller.log"))
    logger.info(f"args: {args}")

    controller = Controller(args.dispatch_method)
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")