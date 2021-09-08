
OUT = usimm
BINDIR = ../bin
OBJDIR = ../obj
OBJS = $(OBJDIR)/main.o $(OBJDIR)/memory_controller.o $(OBJDIR)/scheduler_adaptive.o
CC = gcc -std=c99
DEBUG = -g
CFLAGS = -Wall -c $(DEBUG)
LFLAGS = -Wall $(DEBUG) -Wl,--allow-multiple-definition


$(BINDIR)/$(OUT): $(OBJS)
	$(CC) $(LFLAGS) $(OBJS) -o $(BINDIR)/$(OUT)
	chmod 777 $(BINDIR)/$(OUT)

$(OBJDIR)/main.o: main.c processor.h configfile.h memory_controller.h scheduler_adaptive.h params.h
	$(CC) $(CFLAGS) main.c -o $(OBJDIR)/main.o
	chmod 777 $(OBJDIR)/main.o

$(OBJDIR)/memory_controller.o: memory_controller.c utlist.h utils.h params.h memory_controller.h scheduler_adaptive.h processor.h
	$(CC) $(CFLAGS) memory_controller.c -o $(OBJDIR)/memory_controller.o
	chmod 777 $(OBJDIR)/memory_controller.o

$(OBJDIR)/scheduler_adaptive.o: scheduler_adaptive.c scheduler_adaptive.h utlist.h utils.h memory_controller.h params.h
	$(CC) $(CFLAGS) scheduler_adaptive.c -o $(OBJDIR)/scheduler_adaptive.o
	chmod 777 $(OBJDIR)/scheduler_adaptive.o

clean:
	rm -f $(BINDIR)/$(OUT) $(OBJS)
