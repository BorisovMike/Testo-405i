# Borsov M

# To discover Bluetooth devices
import asyncio
from bleak import BleakScanner
from bleak import BleakClient
import struct
import time
import os
# async def main():
#     devices = await BleakScanner.discover()
#     for d in devices:
#         print(d)

# asyncio.run(main())


address = "48:70:1E:3A:54:8C"
MODEL_NBR_UUID = "00002a00-0000-1000-8000-00805f9b34fb"
uuid_chr1 = '0000fff1-0000-1000-8000-00805f9b34fb'
uuid_chr4 = '0000fff2-0000-1000-8000-00805f9b34fb'
buffer = bytearray()
data = {'Timestamp':0,
        'Velocity':0,
        'Temperature':0}

def callback(sender: int, data: bytearray):
    global buffer
    # print(f"{sender}: {data.hex(' ')}")
    buffer.extend(data)
    if len(buffer) > 40:
        buffer_read()


def buffer_read():
    global buffer
    # print(f'Buffer length {len(buffer)}')
    while len(buffer) >= 32:
        if buffer[0:2] == b'\x10\x80':
            frame_len = buffer[2] + 8
            frame = buffer[:frame_len]
            # print(f"frame len {frame_len}  {frame.hex(' ')}")
            # print(f"frame len {frame_len}  {frame}")
            buffer[:frame_len] = b'' # shift buffer left 
            parse_frame(frame)
        else:
            buffer[:1] = b'' # shift buffer left
    return

def parse_frame(frame):
    global data
    parameter_len = frame[8]
    parameter = frame[12:12+parameter_len].decode(encoding='utf-8')
    if parameter == 'Velocity':
        data['Timestamp'] = time.time() # data packet starts from Velocity
        data['Velocity'] = False
    value = struct.unpack('<f', frame[12+parameter_len:12+parameter_len+4])[0]
    data[parameter] = '{:.2f}'.format(value)
    if data['Velocity'] is not False:
        print(data)
        # print('{Timestamp:},{Velocity:},{Temperature:}\n'.format(**data))
        log.write('{Timestamp:},{Velocity:},{Temperature:}\n'.format(**data))
        log.flush()

    # print(parameter.decode(encoding='utf-8'))
    # if parameter.decode(encoding='utf-8') == 'Velocity': #'Temperature': #
    #     rest = frame[12+parameter_len:]
    #     print(rest.hex(' '))
# FOR CRC https://pycrc.org/, https://pypi.org/project/crcmod/


async def Testo405i(address):
    async with BleakClient(address) as client:
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))

        # for a in client.services.characteristics:
        #     characteristic = client.services.characteristics[a]
        #     print(  
        #             hex(characteristic.handle),
        #             characteristic.uuid,
        #             characteristic.description,
        #         )

        await client.start_notify(uuid_chr4, callback)
        await client.write_gatt_char(uuid_chr1, b"\x56\x00\x03\x00\x00\x00\x0c\x69\x02\x3e\x81", response=True)
        await client.write_gatt_char(uuid_chr1, b"\x20\x01\x00\x00\x00\x00\x3a\xbb", response=True)
        await client.write_gatt_char(uuid_chr1, b"\x04\x02\x15\x00\x00\x00\x7c\x53\x0f\x00\x00\x00\x46\x69\x72\x6d\x77\x61\x72\x65", response=True)
        await client.write_gatt_char(uuid_chr1, b"\x56\x65\x72\x73\x69\x6f\x6e\x30\x4f", response=True) # firmware version
        await client.write_gatt_char(uuid_chr1, b"\x11\x03\x00\x00\x00\x00\x47\x5a", response=True) # run continous measurement
        
        # svcs = await client.get_services()
        # print(
        # for service in svcs:
        #     print(service)
        while True:        
                await asyncio.sleep(1200)
                # close all task (for stop execution)
                buffer_read()


                for task in asyncio.all_tasks():
                        task.cancel()

if __name__ == "__main__":
    
    log_dir = './logs'
    log_name = os.path.join(log_dir, 'Testo405i_'+ time.strftime("%Y-%m-%d_%H-%M-%S") + '.csv')
    log = open(log_name, 'w')
    log.write('Timestamp,Velocity m/s,Temperature C\n')
    try:
        asyncio.run(Testo405i(address))
    except asyncio.CancelledError:
        print('tasks was cancelled on device disconnected')
        log.close()