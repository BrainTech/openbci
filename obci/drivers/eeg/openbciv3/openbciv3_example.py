from openbciv3 import *

def handle_sample(sample):
  print(sample)


if __name__ == '__main__':
    dummy = False
    active_channels = [0,1,2,3,4,5,6,7,8]
    sampling_frequency = 250
    port = "/dev/ttyUSB0"

    board = OpenBCIBoard()
    W = board.set_params(active_channels=active_channels, sampling_frequency=sampling_frequency, port=port, dummy=dummy)

    # board.print_register_settings()

    board.start(handle_sample)

