
OUT = usimm
BINDIR = ../bin
OBJDIR = ../obj
OBJS = $(OBJDIR)/main.o $(OBJDIR)/memory_controller.o $(OBJDIR)/scheduler-close.o
CC = gcc -std=c99
DEBUG = -g
CFLAGS = -Wall -c $(DEBUG)
LFLAGS = -Wall $(DEBUG) -Wl,--allow-multiple-definition


$(BINDIR)/$(OUT): $(OBJS)
	$(CC) $(LFLAGS) $(OBJS) -o $(BINDIR)/$(OUT)
	chmod 777 $(BINDIR)/$(OUT)

$(OBJDIR)/main.o: main.c processor.h configfile.h memory_controller.h scheduler-close.h params.h
	$(CC) $(CFLAGS) main.c -o $(OBJDIR)/main.o
	chmod 777 $(OBJDIR)/main.o

$(OBJDIR)/memory_controller.o: memory_controller.c utlist.h utils.h params.h memory_controller.h scheduler-close.h processor.h
	$(CC) $(CFLAGS) memory_controller.c -o $(OBJDIR)/memory_controller.o
	chmod 777 $(OBJDIR)/memory_controller.o

$(OBJDIR)/scheduler-close.o: scheduler-close.c scheduler-close.h utlist.h utils.h memory_controller.h params.h
	$(CC) $(CFLAGS) scheduler-close.c -o $(OBJDIR)/scheduler-close.o
	chmod 777 $(OBJDIR)/scheduler-close.o

clean:
	rm -f $(BINDIR)/$(OUT) $(OBJS)

