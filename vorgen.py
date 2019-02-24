import argparse
import math
import struct
import wave

SAMPLE_RATE = 44100

def get_vor_samples(bearing=0, duration=1, sample_rate=SAMPLE_RATE):
    SUBCARRIER_FREQ = 9960
    DEVIATION_FREQ = 480
    REF_MODULATION_FREQ = 30
    VARIABLE_FREQ = 30
    
    # For angular calculations, use radians; expect input in degrees
    bearing_rad = math.radians(bearing)
    ref_rad = 0
    samples = []
    for sample in range(0, duration*sample_rate):
        time = sample / sample_rate
        fm_turns = 30 * time
        # Whole turns don't matter
        fm_turns -= math.floor(fm_turns)
        fm_rad = fm_turns * 2 * math.pi
        fm_val = math.sin(fm_rad)

        ref_freq = SUBCARRIER_FREQ + DEVIATION_FREQ * fm_val
        ref_rad += ref_freq * 2 * math.pi / sample_rate
        ref_pos = math.sin(ref_rad)

        var_rad = fm_rad + bearing_rad
        var_pos = math.sin(var_rad)

        # scale output to [-1, 1]
        samples.append((var_pos + ref_pos)/2.0)

    return samples

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create VOR wave"
    )
    parser.add_argument(
        "output_filename",
        type=str,
        help="Name of output WAVE file.",
    )
    parser.add_argument(
        "-b", "--bearing",
        type=float,
        help="VOR bearing",
        default=0.0,
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        help="Duration in seconds of the output file",
        default=1,
    )
    args = parser.parse_args()

    wav = wave.open(args.output_filename, "wb")
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(SAMPLE_RATE)
    samples = get_vor_samples(
        bearing=args.bearing,
        duration=args.duration,
        sample_rate=SAMPLE_RATE,
    )

    # from https://www.programcreek.com/python/example/82393/wave.open
    tensor_enc = b""
    for sample in samples:
        tensor_enc += struct.pack("<h", int(32767.0 * sample))
    wav.writeframes(tensor_enc)
    wav.close()
