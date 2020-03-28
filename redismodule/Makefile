SRC_C := ycsbe.c
OBJ_C := $(patsubst %.c, %.o, $(SRC_C))

#WERROR_FLAGS := -W -Wall -Wstrict-prototypes -Wmissing-prototypes
#WERROR_FLAGS += -Wmissing-declarations -Wold-style-definition -Wpointer-arith
#WERROR_FLAGS += -Wcast-align -Wnested-externs -Wcast-qual
#WERROR_FLAGS += -Wformat-nonliteral -Wformat-security
#WERROR_FLAGS += -Wundef -Wwrite-strings

CFLAGS :=  $(WERROR_FLAGS) -fPIC -g -O3
LDFLAGS = -shared

ycsbe.so: $(OBJ_C)
	$(CC) -o $@ $(OBJ_C) $(LDFLAGS)

clean:
	rm -f *.o

distclean:
	make clean
	rm -f ycsbe.so
