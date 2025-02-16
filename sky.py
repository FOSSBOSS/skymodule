#!/usr/bin/env python3
import spidev
import struct
import time

# Initialize SPI connection
spi = spidev.SpiDev()
spi.open(0, 0)  # Open bus 0, device 0
spi.max_speed_hz = 500000  # Adjust based on module specifications
spi.mode = 0  # Adjust if the module requires a different SPI mode

def calculate_crc(data):
    """Calculate CRC-16-CCITT."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF  # Ensure CRC remains 16-bit
    return crc

def construct_read_mem_command(tag_type, starting_block, num_blocks):
    """Construct a READ_MEM command following the SkyeTek Protocol V2."""
    FLAGS = 0x00  # Default FLAGS; adjust as needed
    COMMAND = 0x20  # READ_MEM command code
    # Construct the payload without CRC
    payload = struct.pack('>BBBHH', FLAGS, COMMAND, tag_type, starting_block, num_blocks)
    MSG_LEN = len(payload) + 3  # Payload length + MSG_LEN byte + CRC (2 bytes)
    # Prepend MSG_LEN to the payload
    message = struct.pack('>B', MSG_LEN) + payload
    # Calculate CRC over the entire message
    crc = calculate_crc(message)
    # Append CRC to the message
    message += struct.pack('>H', crc)
    return message

def send_command(command):
    """Send SPI command and receive response."""
    response = spi.xfer2(list(command))
    return response

def continuous_scan(tag_type, starting_block, num_blocks, scan_interval=1.0):
    """Continuously scan the SPI device at a set interval."""
    try:
        print("Starting continuous scan...")
        while True:
            command = construct_read_mem_command(tag_type, starting_block, num_blocks)
            response = send_command(command)
            print(f"Response: {response}")
            time.sleep(scan_interval)  # Wait before next scan
    except KeyboardInterrupt:
        print("\nScan stopped by user.")
    except Exception as e:
        print(f"Error during scan: {e}")
    finally:
        spi.close()

# Example Usage
if __name__ == "__main__":
    tag_type = 0x01  # Example tag type (adjust based on your module)
    starting_block = 0x0000  # Block to start reading from
    num_blocks = 0x0001  # Number of blocks to read
    continuous_scan(tag_type, starting_block, num_blocks, scan_interval=0.5)  # Scan every 0.5s

