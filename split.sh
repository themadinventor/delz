#!/bin/sh
dd count=1 bs=65536 if=sunray.bin of=bootloader.bin
dd count=1 skip=1 bs=65536 if=sunray.bin of=recovery.bin
dd skip=2 bs=65536 if=sunray.bin of=app.bin
