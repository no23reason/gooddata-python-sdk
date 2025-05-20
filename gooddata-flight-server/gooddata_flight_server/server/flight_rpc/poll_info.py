#  (C) 2025 GoodData Corporation
from dataclasses import dataclass
from typing import Optional

import pyarrow.flight
from google.protobuf import timestamp_pb2

import gooddata_flight_server.proto.flight_rpc_ext_pb2 as proto


@dataclass
class PollInfo:
    info: Optional[pyarrow.flight.FlightInfo] = None
    """
    The currently available results.

    If "flight_descriptor" is not specified, the query is complete
    and "info" specifies all results. Otherwise, "info" contains
    partial query results.

    Note that each PollInfo response contains a complete
    FlightInfo (not just the delta between the previous and current
    FlightInfo).

    Subsequent PollInfo responses may only append new endpoints to
    info.

    Clients can begin fetching results via DoGet(Ticket) with the
    ticket in the info before the query is
    completed. FlightInfo.ordered is also valid.
    """

    flight_descriptor: Optional[pyarrow.flight.FlightDescriptor] = None
    """
    The descriptor the client should use on the next try.
    If unset, the query is complete.
    """
    progress: Optional[float] = None
    """
    Query progress. If known, must be in [0.0, 1.0] but need not be
    monotonic or nondecreasing. If unknown, do not set.
    """

    expiration_time: Optional[int] = None
    """
    Expiration time for this request. After this passes, the server
    might not accept the retry descriptor anymore (and the query may
    be cancelled). This may be updated on a call to PollFlightInfo.
    """

    def serialize(self) -> bytes:
        pb = proto.PollInfo()

        if self.info is not None:
            i = proto.FlightInfo()
            i.ParseFromString(self.info.serialize())
            pb.info.CopyFrom(i)

        if self.flight_descriptor is not None:
            fd = proto.FlightDescriptor()
            fd.ParseFromString(self.flight_descriptor.serialize())
            pb.flight_descriptor.CopyFrom(fd)

        if self.progress is not None:
            pb.progress = self.progress

        if self.expiration_time is not None:
            t = timestamp_pb2.Timestamp()
            t.seconds = self.expiration_time
            pb.expiration_time.CopyFrom(t)

        return pb.SerializeToString()

    @staticmethod
    def deserialize(data: bytes) -> "PollInfo":
        pb = proto.PollInfo()
        pb.ParseFromString(data)
        return PollInfo(
            info=pyarrow.flight.FlightInfo.deserialize(pb.info.SerializeToString()) if pb.HasField("info") else None,
            flight_descriptor=pyarrow.flight.FlightDescriptor.deserialize(pb.flight_descriptor.SerializeToString())
            if pb.HasField("flight_descriptor")
            else None,
            progress=pb.progress if pb.HasField("progress") else None,
            expiration_time=pb.expiration_time.seconds if pb.HasField("expiration_time") else None,
        )
