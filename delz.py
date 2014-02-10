#!/usr/bin/env python
#
# Sun Microsystems SunRay "Corona" Firmware Decompressor
# (c) 2014, Fredrik Ahlberg <kongo@df.lth.se>

class BitReservoir:

	def __init__(self, stream):
		self.__stream__ = stream
		self.__reservoir__ = 0
		self.__reslen__ = 0
	
	def bits(self, bits):
		while self.__reslen__ < bits:
			self.__reslen__ += 8
			self.__reservoir__ <<= 8
			self.__reservoir__ |= ord(self.__stream__.read(1))
		v = self.__reservoir__ >> self.__reslen__ - bits
		v &= (1 << bits) - 1
		self.__reslen__ -= bits
		#print 'Read %d bits: %x' % (bits, v)
		return v

	def size(self):
		return self.__reslen__

class SlidingWriter:

	def __init__(self, stream):
		self.__stream__ = stream
		self.__buffer__ = ''
	
	def put(self, ch):
		ch = chr(ch)
		self.__stream__.write(ch)
		self.__buffer__ += ch
		#print 'Wrote %x' % ord(ch)
		#print 'Buffer: ' + ' '.join(map(hex,map(ord,self.__buffer__)))
	
	def backref(self, distance, length):
		#print 'Backref %d,%d' % (distance, length)
		while length > 0:
			self.__stream__.write(self.__buffer__[-distance])
			self.__buffer__ += self.__buffer__[-distance]
			length -= 1
		#print 'Buffer: ' + ' '.join(map(hex,map(ord,self.__buffer__)))

def delz(ins, outs):
	br = BitReservoir(ins)
	sw = SlidingWriter(outs)

	if br.bits(8) != ord('L') or br.bits(8) != ord('Z'):
		raise Exception('Invalid stream header')

	while True:
		#print 'start'
		if br.bits(1) == 0:
			if br.size() == 8:
				sw.put(br.bits(8))
			else:
				sw.put(br.bits(7))
		else:
			if br.bits(1) == 0:
				if br.size() == 8:
					sw.put(br.bits(8))
				else:
					sw.put(0x80|br.bits(7))
			else:
				if br.bits(1) == 0:
					distance = br.bits(6)
				else:
					if br.bits(1) == 0:
						distance = 64 + br.bits(9)
					else:
						distance = 576 + br.bits(12)
						if distance > 4096+576-2:
							raise Exception('Suspicious distance %d' % distance)
				ll = 0
				while True:
					if br.bits(1) == 1:
						break
					if ll > 15:
						break
					ll += 1

				# if we've got > 15 ones, then we're probably at the end.


				if ll > 0:
					length = br.bits(ll)
				else:
					length = 0

				length += 2 + (1 << ll)

				#print 'distance %d, ll=%d, length=%d' % (distance, ll, length)
				sw.backref(distance, length)


	if br.bits(8) != ord('J') or br.bits(8) != ord('H'):
		raise Exception('Invalid stream footer')


if __name__ == '__main__':
	i = file('../recovery.bin')
	if i.read(4) != "\xab\xad\xbe\xef":
		raise Exception('Not a compressed firmware image')
	i.read(4)
	delz(i, file('recovery_decompressed.bin','w'))

