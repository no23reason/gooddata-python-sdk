# (C) 2025 GoodData Corporation
import pyarrow
import pyarrow.flight
import pytest
from gooddata_flight_server.server.flight_rpc.poll_info import PollInfo


@pytest.mark.parametrize(
    "poll_info",
    [
        PollInfo(),
        PollInfo(flight_descriptor=pyarrow.flight.FlightDescriptor.for_path("a/b/c")),
        PollInfo(
            info=pyarrow.flight.FlightInfo(
                pyarrow.schema([pyarrow.field("foo", pyarrow.string())]),
                pyarrow.flight.FlightDescriptor.for_path("a/b/c"),
                [],
            )
        ),
        PollInfo(progress=0.42, expiration_time=1234),
    ],
)
def test_serde(poll_info: PollInfo) -> None:
    serialized = poll_info.serialize()
    deserialized = poll_info.deserialize(serialized)
    assert poll_info == deserialized
