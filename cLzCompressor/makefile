SOURCES = cLzCompressor.c fastlz.c
CFLAGS = -Wall -Wextra -g
EXECUTABLE = cLzCompressor

.PHONY: all clean

all:
	gcc $(SOURCES) $(CFLAGS) -o $(EXECUTABLE)

clean:
	-rm $(EXECUTABLE)