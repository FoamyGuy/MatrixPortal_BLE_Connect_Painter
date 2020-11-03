import board
import displayio
import framebufferio
import rgbmatrix
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.button_packet import ButtonPacket
from adafruit_airlift.esp32 import ESP32

displayio.release_displays()

esp32 = ESP32()  # DEFAULT

cur_loc = [0, 0]
cur_color = 1
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=3,
    rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1,
              board.MTX_R2, board.MTX_G2, board.MTX_B2, ],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD],
    clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT, output_enable_pin=board.MTX_OE)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

main_group = displayio.Group(max_size=10)

color_bitmap = displayio.Bitmap(display.width, display.height, 10)
color_palette = displayio.Palette(10)
color_palette[0] = 0x000000
color_palette[1] = 0x220000
color_palette[2] = 0x002200
color_palette[3] = 0x000022
color_palette[4] = 0x002222
color_palette[5] = 0x222200
color_palette[6] = 0x220022

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)

main_group.append(bg_sprite)
display.show(main_group)

adapter = esp32.start_bluetooth()

ble = BLERadio(adapter)
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)
prev_color = 0

while True:
    ble.start_advertising(advertisement)
    print("waiting to connect")
    while not ble.connected:
        pass
    print("connected")
    # Loop and read packets
    while ble.connected:
        color_bitmap[cur_loc] = cur_color
        # Keeping trying until a good packet is received
        try:
            packet = Packet.from_stream(uart)
        except ValueError:
            continue

        # Only handle button packets
        if isinstance(packet, ButtonPacket) and packet.pressed:
            if packet.button == ButtonPacket.UP:
                print("Button UP")
                color_bitmap[cur_loc] = prev_color
                cur_loc[1] -= 1
                cur_loc[1] = max(0, cur_loc[1])
                prev_color = color_bitmap[cur_loc]
                color_bitmap[cur_loc] = cur_color
            if packet.button == ButtonPacket.DOWN:
                print("Button DOWN")
                color_bitmap[cur_loc] = prev_color
                cur_loc[1] += 1
                cur_loc[1] = min(display.height-1, cur_loc[1])
                prev_color = color_bitmap[cur_loc]
                color_bitmap[cur_loc] = cur_color
            if packet.button == ButtonPacket.LEFT:
                print("Button LEFT")
                color_bitmap[cur_loc] = prev_color
                cur_loc[0] -= 1
                cur_loc[0] = max(0, cur_loc[0])
                prev_color = color_bitmap[cur_loc]
                color_bitmap[cur_loc] = cur_color
            if packet.button == ButtonPacket.RIGHT:
                print("Button RIGHT")
                color_bitmap[cur_loc] = prev_color
                cur_loc[0] += 1
                cur_loc[0] = min(display.width-1, cur_loc[0])
                prev_color = color_bitmap[cur_loc]
                color_bitmap[cur_loc] = cur_color
            if packet.button == ButtonPacket.BUTTON_1:
                print("Button 1")
                cur_color -= 1
                cur_color = max(cur_color, 1)
            if packet.button == ButtonPacket.BUTTON_2:
                print("Button 2")
                cur_color += 1
                cur_color = min(cur_color, 6)
            if packet.button == ButtonPacket.BUTTON_3:
                print("Button 3")
                prev_color = cur_color
            if packet.button == ButtonPacket.BUTTON_4:
                print("Button 4")
                prev_color = 0
                prev_color = 0
    # Disconnected
    print("DISCONNECTED")