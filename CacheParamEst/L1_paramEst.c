/*
  L1_paramEst.c
  L1 Cache Parameter Estimation through inspection of read access latencies
  Author: Arjun Menon Vadakkeveedu, ee18b104
          IIT Madras
  Assignment 1
  Computer Architecture, CS6600
  Aug- Nov 2021

  Description: - C program to estimate L1 Cache Block Size and Set Associativity of a PC system
               - Performed on Intel i5-8250U processor
               - Memory Access Latency for accessing contiguous bytes in a char array is evaluated in
                 the function 'est_blockSize()'. The latency is substantially higher at intervals of
                 64 bytes, when averaged over 100 runs, indicating a block size of 64B
               - In the function 'est_Asscvty()', blocks located at spacings of 32K (L1 cache size) are
                 accessed initially. This ensures that the latest accessed P blocks are present in L1
                 and have minimal access latency, where P is the associativity. All subsequent accesses
                 would involve a higher latency owing to the miss penalty.
*/
#include<stdio.h>
#include<stdlib.h>

#define N 1024
#define NUM_TESTS 10
#define CACHE_SIZE 1024*32        // 32K, extracted using lscpu command;
// for estimating associativity, any power of 2 > cache size will suffice

typedef unsigned long long int unsigned64;
typedef unsigned long int unsigned32;

static __inline__ unsigned64 rdtsc(void){
  /*
    Inline Assembly to run serialised rdtsc (disable OOO execution): cpuid is used to serialise the exec
    RDTSC returns 64-bit cycle number to {EDX, EAX} registers
  */
  unsigned32 low_word, high_word;
  __asm__ __volatile__ ("cpuid \n\t"
                        "rdtsc \n\t" : "= a"(low_word), "= d"(high_word));
  return ((unsigned64)low_word | ((unsigned64)high_word << 32));
}

void flushLine(volatile char *p){
  /*
    Inline Assembly to Flush the Cache Line corresponding to input address
    sfence instruction added to serialise CLFLUSH instruction (avoid OOO)
  */
  __asm__ __volatile__ ("sfence \n\t"
                        "clflush (%0) \n\t" :: "r"(p));
}

void est_blockSize()
{
  char *byte_ptr = (char *)malloc(N*sizeof(char));
  unsigned64 time0, time1;
  float acc_lat[N];
  FILE *file_ptr;
  char dummy;
  time0 = 0; time1 = 0;
  for (int i = 0; i<N; i++){
    *(byte_ptr + i) = 0;
    acc_lat[i] = 0;
  }

  for(int j = 0; j<NUM_TESTS; j++)
  {
    for (int i = 0; i<N; i++){
      flushLine(byte_ptr + i);
    }
    for (int i = 0; i<N; i++){
      time0 = rdtsc();
      dummy = *(byte_ptr + i);  // involves memory access and writing to a variable in cache
      time1 = rdtsc();
      acc_lat[i] += (float)(time1 - time0);
    }
  }
  file_ptr = fopen("acc_lat.txt", "w");
  for (int i = 0; i<N; i++){
    acc_lat[i] = acc_lat[i]/NUM_TESTS;
    fprintf(file_ptr, "\n %d, %f", i, acc_lat[i]);
  }
  fclose(file_ptr);
  free(byte_ptr);
}

void est_Asscvty(){
  int max_ways = 33;
  int way_est = 33;
  float acc_lat[way_est];
  unsigned64 time0, time1;
  FILE *file_ptr;
  char *base_ptr = (char *)malloc((max_ways)*CACHE_SIZE*sizeof(char));
  // way_est*32K chunk allocated in heap to avoid segfault
  char dummy;
  for(int i = 0; i< way_est; i++){
     acc_lat[i] = 0;
  }
  for (int j = 0; j<NUM_TESTS; j++){
    for(int i = 0; i< way_est; i++){
      int offset = i*CACHE_SIZE;
      dummy = *(base_ptr + offset);   // touch addresses at base, base+32K, base+64K ...
    }
    for(int i = 0; i< way_est; i++){
      int offset = (way_est - i)*CACHE_SIZE; // access blocks in rev order => latest block first
      time0 = rdtsc();
      dummy = *(base_ptr + offset);
      time1 = rdtsc();
      acc_lat[i] += (float)(time1 - time0);
    }
  }
  file_ptr = fopen("set_lat.txt", "w");
  for (int i = 0; i<way_est; i++){
    acc_lat[i] = acc_lat[i]/NUM_TESTS;
    fprintf(file_ptr, "\n %d, %f", i, acc_lat[i]);
  }
  fclose(file_ptr);
  free(base_ptr);
}

void main(){
  est_blockSize();
  est_Asscvty();
}
