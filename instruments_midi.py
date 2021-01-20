from mido import MidiFile, tick2second
import numpy as np
import click

ind = 0


def write_instrument(track):
    name = track.name.replace(" ", "_")

    messages = [msg for msg in track]
    instrument = list(filter(lambda msg: 'program_change' in msg.type, messages))
    control = list(filter(lambda msg: 'control_change' in msg.type, messages))
    # print(control)
    if len(instrument) > 0:
        instrument_midi = instrument[0].program
        channel_midi = instrument[0].channel
        # input()
    elif len(control) > 1:
        instrument_midi = 127
        channel_midi  = control[0].channel
    messages = list(filter(lambda msg: 'note' in msg.type, messages))
    time = np.array([msg.time for msg in messages])

    if (len(instrument) > 0 or len(control) > 1) and len(time) > 0 and max(time) < 65535:
        total = len(time)
        print("Total = {}".format(total))
        with open(name.replace("/", "-") + '.inst', 'wb') as f:
            f.write(np.uint8(channel_midi))
            f.write(np.uint8(instrument_midi))
            for msg in messages:
                msg_type = np.uint8(0 if 'off' in msg.type else 1)
                msg_note = np.uint8(msg.note)
                msg_velocity = np.uint8(msg.velocity)
                msg_time = np.uint16(msg.time)
                f.write(msg_type)
                f.write(msg_note)
                f.write(msg_velocity)
                f.write(msg_time)
                print(msg)
        # with open("inst_" + name + '.txt', 'rb') as f:
        #     read = f.read(1)
        #     read = int.from_bytes(read, byteorder='little', signed=False)
        #     print(read)
        #     read = f.read(2)
        #     read = int.from_bytes(read, byteorder='little', signed=False)
        #     msg_type = int.from_bytes(f.read(1), byteorder='little', signed=False)
        #     msg_note = int.from_bytes(f.read(1), byteorder='little', signed=False)
        #     msg_velocity = int.from_bytes(f.read(1), byteorder='little', signed=False)
        #     msg_time = int.from_bytes(f.read(2), byteorder='little', signed=False)
        #     print(msg_type, msg_note, msg_velocity, msg_time)           

    # print(messages)



@click.command()
@click.argument('file')
def main(file):
    events = set()
    mid = MidiFile(file)
    # print(tick2second(1, mid.ticks_per_beat, 500000) * 1000)
    # raise
    # type 0 (single track): all messages are saved in one track
    # type 1 (synchronous): all tracks start at the same time
    # type 2 (asynchronous): each track is independent of the others
    if mid.type == 1:
        for track in mid.tracks:
            events_by_track = np.array([msg.time for msg in track])
            events_by_track = np.cumsum(events_by_track)
            events = events | set(events_by_track)
            write_instrument(track)
    raise
    events = list(events)
    events.sort()
    print(events)
    events = np.array(events)

    print(len(events))
    time = events.copy()
    time[1:] -= time[:-1].copy()
    print(tick2second(events, mid.ticks_per_beat, 500000) * 1000)
    print(events)
    print(time[:10])
    raise



    print(mid.__dict__)
    print(mid.length)
    print(mid.ticks_per_beat)
    for i, track in enumerate(mid.tracks[1:]):


        print(track.__dict__)
        print('Track {}: {}'.format(i, track.name))
        first = True
        text = []
        time = []
        velocity = []

        text.append('byte ' + track.name.replace(" ", "_") + '_array[] = {')
        time.append('byte ' + track.name.replace(" ", "_") + '_time_array[] = {')
        velocity.append('byte ' + track.name.replace(" ", "_") + '_velocity_array[] = {')

        tim = 0
        for msg in track:
            if msg.type == 'note_on':
                note = msg.note
                tim += int(msg.time)
                print(tick2second(msg.time, mid.ticks_per_beat, 500000) * 1000)
                vel = msg.velocity

                text.append("{}{}".format(
                    '' if first else ', ', note))
                time.append("{}{}".format(
                    '' if first else ', ', tim))
                velocity.append("{}{}".format(
                    '' if first else ', ', vel))
                first = False
                tim = 0
                if len(text) % 14 == 0:
                    text.append(",\n{}".format(note))
                if len(time) % 14 == 0:
                    time.append(",\n{}".format(tim))
                if len(velocity) % 14 == 0:
                    velocity.append(",\n{}".format(vel))
                # if 'instrument_name' in str(msg.type):
                #     print(msg.type)
                #     print(msg)
                #     break
            if msg.type == 'note_off':
                tim += int(msg.time)
            print(msg)

        text.append("};\n")
        time.append("};\n")
        velocity.append("};\n")
        with open("inst_" + track.name + '.txt', 'w') as f:
            f.writelines(text)
        with open("inst_" + track.name + '_time.txt', 'w') as f:
            f.writelines(time)
        with open("inst_" + track.name + '_velocity.txt', 'w') as f:
            f.writelines(velocity)
        a = input()
        if a == 'e':
            raise


if __name__ == '__main__':
    main()
    # Test
