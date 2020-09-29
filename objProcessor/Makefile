SOURCES = objProcessor.c cnovrsupport.c ../cLzCompressor/fastlz.c
CFLAGS = -Wall -Wextra -g -O3 -I../cLzCompressor
EXECUTABLE = objProcessor

.PHONY: all clean

all:
	gcc $(SOURCES) $(CFLAGS) -o $(EXECUTABLE) -lm

clean:
	-rm $(EXECUTABLE)
