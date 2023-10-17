import sys
import datetime

import EPICSEvent_pb2

ESCAPE_CHAR = b"\x1B"
ESCAPE_ESCAPE_CHAR = b"\x01"
NEWLINE_CHAR = b"\x0A"
NEWLINE_ESCAPE_CHAR = b"\x02"
CARRIAGERETURN_CHAR = b"\x0D"
CARRIAGERETURN_ESCAPE_CHAR = b"\x03"


def main():
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "Serialized Sample Data")
        sys.exit(-1)

    with open(sys.argv[1], "rb") as f:
        lines = f.readlines()

    info = EPICSEvent_pb2.PayloadInfo()
    sample = None
    inChunk = False

    for line in lines:
        if line.startswith(b"\n"):
            inChunk = False
            continue

        l = unescapeLine(line)

        if not inChunk:
            info.ParseFromString(l)
            print(info)
            inChunk = True
            sample = getMessageType(info.type)
            continue

        if sample is None:
            continue

        sample.ParseFromString(l)
        print(
            f"timestamp: {convertTimestamp(info.year, sample.secondsintoyear, sample.nano)}"
        )
        print(sample)


def unescapeLine(line):
    buf = bytes()
    escaped = False
    for b in line:
        byteb = bytes([b])

        if escaped:
            if byteb == ESCAPE_ESCAPE_CHAR:
                buf += ESCAPE_CHAR
            elif byteb == NEWLINE_ESCAPE_CHAR:
                buf += NEWLINE_CHAR
            elif byteb == CARRIAGERETURN_ESCAPE_CHAR:
                buf += CARRIAGERETURN_CHAR
            else:
                buf += byteb

            escaped = False
            continue

        if byteb == NEWLINE_CHAR:
            continue

        if byteb == ESCAPE_CHAR:
            escaped = True
            continue

        buf += byteb

    return buf


def getMessageType(info_type):
    payload_type = EPICSEvent_pb2.PayloadType
    if info_type == payload_type.SCALAR_STRING:
        return EPICSEvent_pb2.ScalarString()
    elif info_type == payload_type.SCALAR_SHORT:
        return EPICSEvent_pb2.ScalarShort()
    elif info_type == payload_type.SCALAR_FLOAT:
        return EPICSEvent_pb2.ScalarFloat()
    elif info_type == payload_type.SCALAR_ENUM:
        return EPICSEvent_pb2.ScalarEnum()
    elif info_type == payload_type.SCALAR_BYTE:
        return EPICSEvent_pb2.ScalarByte()
    elif info_type == payload_type.SCALAR_INT:
        return EPICSEvent_pb2.ScalarInt()
    elif info_type == payload_type.SCALAR_DOUBLE:
        return EPICSEvent_pb2.ScalarDouble()
    elif info_type == payload_type.WAVEFORM_STRING:
        return EPICSEvent_pb2.VectorString()
    elif info_type == payload_type.WAVEFORM_SHORT:
        return EPICSEvent_pb2.VectorShort()
    elif info_type == payload_type.WAVEFORM_FLOAT:
        return EPICSEvent_pb2.VectorFloat()
    elif info_type == payload_type.WAVEFORM_ENUM:
        return EPICSEvent_pb2.VectorEnum()
    elif info_type == payload_type.WAVEFORM_BYTE:
        return EPICSEvent_pb2.VectorChar()
    elif info_type == payload_type.WAVEFORM_INT:
        return EPICSEvent_pb2.VectorInt()
    elif info_type == payload_type.WAVEFORM_DOUBLE:
        return EPICSEvent_pb2.VectorDouble()
    elif info_type == payload_type.V4_GENERIC_BYTES:
        return EPICSEvent_pb2.V4GenericBytes()


def convertTimestamp(year, seconds, nano):
    yearts = datetime.datetime(year=year, month=1, day=1)
    secs = datetime.timedelta(seconds=seconds, microseconds=nano / 1000)
    ts = yearts + secs
    return ts


if __name__ == "__main__":
    main()
