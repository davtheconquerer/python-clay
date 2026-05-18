CC      ?= gcc
CFLAGS  ?= -O2
SRC     := clay_wrapper.c

ifeq ($(OS),Windows_NT)
    TARGET := clay.dll
    CFLAGS += -DCLAY_DLL -shared
else
    UNAME := $(shell uname -s)
    ifeq ($(UNAME),Linux)
        TARGET := libclay.so
        CFLAGS += -fPIC -shared
    else ifeq ($(UNAME),Darwin)
        TARGET := libclay.dylib
        CFLAGS += -fPIC -shared
    else
        $(error Unknown OS: $(UNAME))
    endif
endif

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $@ $^

clean:
	rm -f $(TARGET) *.o
