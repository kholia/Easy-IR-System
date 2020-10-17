# https://github.com/arduino/arduino-cli/releases
# curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=~/local/bin sh

fqbn := digistump:avr:digispark-tiny

default:
	arduino-cli compile --fqbn=${fqbn} Easy-IR-Receiver

deps:
	arduino-cli lib install "dummy-dummy-dummy"

upload:
	arduino-cli compile --fqbn=${fqbn} Easy-IR-Receiver
	arduino-cli upload --fqbn=${fqbn} Easy-IR-Receiver

bootloader:
	arduino-cli burn-bootloader --fqbn=${fqbn}
