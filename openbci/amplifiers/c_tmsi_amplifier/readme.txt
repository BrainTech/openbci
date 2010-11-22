You need libbluetooth-dev package installed to compile this project
if you run "make" the following programs will be made:
tmsi_server
test_server
test_driver
dummy_receiver

Additionally you can run make fusbi_install to install fusbi device driver.
(fxload package is required for it to work properly, you will be noticed if this
package is not installed)

if you run make with "DEBUG=1" (i.e make tmsi_server DEBUG=1) a lot of debug messages will be printed to the stderr.
you should pipe them to the file and watch especially the beginning of the file.
When channel amplifier will start sending channel data, only interesting things will be at the end of file;


programs:
tmsi_server - connects to multiplexer and starts sending samples from TMSI Amplifier
            Available options:
                            "[-a multiplexer_addres] default="127.0.0.1"
                            "[-p port] defaut="31889"
                            "[-d device_path ] amplifier address default="/dev/fusbi0\"
                            "[-b bluetooth address] amplifier bluetooth address
                            "[-r file] file with stored amplifier responses (for debug)
                            "[-l nr_of_samples] print log message after number_of_samples
                            "[-D file] whole amplifier output will be dumped to file (for debug)
                            "[-s sampling_rate] set sampling rate in Hz (ignore hashtable)
                            "[-h] show this help message
test_server - connects to multiplexer and starts sending RANDOM samples (no amplifier needed)
            Available options:
                            "[-s sampling_rate] set sampling rate in Hz (ignore hashtable)

test_driver - connects to amplifier and reads/prints output samples
             Available options:
                            "[-d device_path ] amplifier address default="/dev/fusbi0\"
                            "[-b bluetooth address] amplifier bluetooth address
                            "[-r file] file with stored amplifier responses
                            "[-l nr_of_seconds] stop sampling after nr_of_seconds
                            "[-a file] whole amplifier output will be dumped to file
                            "[-f sampling_rate] set sampling rate in Hz
                            "[-c "channel_names"] set channels to send

dummy_receiver - receive amplifier samples from multiplexer and prints log_message
            Available options:
                            "[-h multiplexer_addres] default="127.0.0.1"
                            "[-p port] defaut="31889"
                            "[-l nr_of_samples] print log message after number_of_samples

Scripts:
start_tmsi_server - starts multiplexer, hashtable, dummy_receiver with logging every 1024 samples and tmsi_server with default settings

stop - kills alls above processes, plus test_server