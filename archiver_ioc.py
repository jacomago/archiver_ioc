import asyncio
from dataclasses import dataclass
import os
import time
from p4p.nt import NTScalar
from p4p.server import Server
from p4p.server.thread import SharedPV
from epicsarchiver import ArchiverAppliance
from epicsarchiver.mgmt.archiver_mgmt_info import ArchivingStatus


@dataclass
class WritingOptions:
    maximum: float
    init: float
    increment: float
    interval: float
    period: float = 0.0
    method: str = "MONITOR"


@dataclass
class ExamplePV:
    shared_pv: SharedPV
    options: WritingOptions


async def start_server_pv(pvs: dict[str, ExamplePV]):
    with Server(
        providers=[{pv_name: pv.shared_pv for pv_name, pv in pvs.items()}]
    ) as _server:
        print("Creating server with PVs:")
        for pv_name in pvs.keys():
            print(pv_name)
        print("Subscribing to archiver appliance")
        archive_pvs(pvs)
        print("Starting server")
        await write_to_pvs(pvs)


def archive_pvs(pvs):
    hostname = os.environ.get("ARCHIVER_HOST", "aa")
    port = os.environ.get("ARCHIVER_PORT", "8080")
    print(f"Archiving to {hostname}:{port}")
    aa = ArchiverAppliance(hostname, port)
    for pv_name in pvs.keys():
        aa.pause_pv(pv_name)
        archiver_status = aa.get_archiving_status(pv_name)
        if archiver_status == ArchivingStatus.Paused:
            aa.delete_pv(pv_name)
        aa.archive_pv(
            f"pva://{pv_name}",
            samplingperiod=pvs[pv_name].options.period,
            samplingmethod=pvs[pv_name].options.method,
        )


def pv_name(base_name: str, option: WritingOptions) -> str:
    return f"{base_name}:PERIOD-{int(1 / option.period)}Hz:METHOD-{option.method}:{int(option.interval)}Hz"


def create_pvs(base_name: str, options: list[WritingOptions]) -> dict[str, ExamplePV]:
    return {
        pv_name(base_name, option): ExamplePV(create_pv(), option) for option in options
    }


def create_pv() -> SharedPV:
    return SharedPV(
        nt=NTScalar("d"),  # scalar double
        initial=0.0,
    )


async def write_to_pvs(pvs: dict[str, ExamplePV]):
    writeables = [write_to_pv(pv_options) for pv_options in pvs.values()]
    await asyncio.gather(*writeables)


async def write_to_pv(pv: ExamplePV):
    value = pv.options.init
    while value < pv.options.maximum:
        value += pv.options.increment
        await asyncio.sleep(1.0 / pv.options.interval)
        pv.shared_pv.post(value, timestamp=time.time())


PV_PREFIX = "ARCH"
TIME_PERIOD_SECS = int(os.environ.get("TIME_PERIOD_SECS", 120))


async def runner():
    print("start")
    await start_server_pv(
        create_pvs(
            PV_PREFIX,
            [
                WritingOptions(
                    20 + TIME_PERIOD_SECS * 32, 20.0, 1.0, 32.0, 0.07, "MONITOR"
                ),
                WritingOptions(TIME_PERIOD_SECS * 32, 0.0, 1.0, 32.0, 0.03, "MONITOR"),
                WritingOptions(
                    40 + TIME_PERIOD_SECS * 32, 40.0, 1.0, 32.0, 0.07, "SCAN"
                ),
                WritingOptions(20 + TIME_PERIOD_SECS * 5, 20.0, 1.0, 5.0, 1, "MONITOR"),
                WritingOptions(TIME_PERIOD_SECS * 5, 0.0, 1.0, 5.0, 0.25, "MONITOR"),
                WritingOptions(40 + TIME_PERIOD_SECS * 5, 40.0, 1.0, 5.0, 1, "SCAN"),
            ],
        )
    )
    print("end")


asyncio.run(runner())
