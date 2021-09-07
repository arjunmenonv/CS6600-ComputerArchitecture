#include <stdio.h>
#include "utlist.h"
#include "utils.h"

#include "memory_controller.h"
#include "scheduler_adaptive.h"
// Comments for self: Remove before committing
// memory_controller.h is included, hence dram_state can be accessed here
// use rd_ptr->dram_addr.row and dram_state.active_row to check for row hit or miss

extern long long int CYCLE_VAL;
// State Variables used in AdapPage:
int ctr_state[MAX_NUM_CHANNELS];
int is_hit_state[MAX_NUM_CHANNELS];
int is_open_state[MAX_NUM_CHANNELS];

void init_scheduler_vars()
{
	// initialize all scheduler variables here:
  // Initially ctr between HighThresh and LowThresh, use open page policy
  for(int i = 0; i<MAX_NUM_CHANNELS; i++){
    ctr_state[i] = (int)(HIGH_THRESH + LOW_THRESH)/2;
    is_open_state[i] = 1;
    is_hit_state[i] = 1; // init unnecessary
                     //  is_hit_state is set in schedule() in the first run before sat_ctr is called
  }
  return;
}

// write queue high water mark; begin draining writes if write queue exceeds this value
#define HI_WM 40

// end write queue drain once write queue has this many writes in it
#define LO_WM 20

#define HIGH_THRESH 10
#define LOW_THRESH 5
// 1 means we are in write-drain mode for that channel
int drain_writes[MAX_NUM_CHANNELS];

/* Each cycle it is possible to issue a valid command from the read or write queues
   OR
   a valid precharge command to any bank (issue_precharge_command())
   OR
   a valid precharge_all bank command to a rank (issue_all_bank_precharge_command())
   OR
   a power_down command (issue_powerdown_command()), programmed either for fast or slow exit mode
   OR
   a refresh command (issue_refresh_command())
   OR
   a power_up command (issue_powerup_command())
   OR
   an activate to a specific row (issue_activate_command()).

   If a COL-RD or COL-WR is picked for issue, the scheduler also has the
   option to issue an auto-precharge in this cycle (issue_autoprecharge()).

   Before issuing a command it is important to check if it is issuable. For the RD/WR queue resident commands, checking the "command_issuable" flag is necessary. To check if the other commands (mentioned above) can be issued, it is important to check one of the following functions: is_precharge_allowed, is_all_bank_precharge_allowed, is_powerdown_fast_allowed, is_powerdown_slow_allowed, is_powerup_allowed, is_refresh_allowed, is_autoprecharge_allowed, is_activate_allowed.
   */

int sat_ctr(int channel, int is_hit, int prev_is_open){
  /* Input: Variable to indicate Cache Hit or Miss; PrevPolicy; HighThresh, LowThresh
     Output: Policy var (open/closed)
  */
  int is_open;
  //Debug:
  if (prev_is_open){
    if(!(is_hit) && (ctr_state < 15)) ctr_state++;
    if(ctr_state[channel] >= HIGH_THRESH) is_open = 0;
    else is_open = 1;
  }
  else {
    if(is_hit && (ctr_state > 0)) ctr_state--;
    if(ctr_state[channel] <= LOW_THRESH) is_open = 1;
    else is_open = 0;
  }
  return is_open;
}

void schedule(int channel)
{
	request_t * rd_ptr = NULL;
	request_t * wr_ptr = NULL;


	// if in write drain mode, keep draining writes until the
	// write queue occupancy drops to LO_WM
	if (drain_writes[channel] && (write_queue_length[channel] > LO_WM)) {
	  drain_writes[channel] = 1; // Keep draining.
	}
	else {
	  drain_writes[channel] = 0; // No need to drain.
	}

	// initiate write drain if either the write queue occupancy
	// has reached the HI_WM , OR, if there are no pending read
	// requests
	if(write_queue_length[channel] > HI_WM)
	{
		drain_writes[channel] = 1;
	}
	else {
	  if (!read_queue_length[channel])
	    drain_writes[channel] = 1;
	}


	// If in write drain mode, look through all the write queue
	// elements (already arranged in the order of arrival), and
	// issue the command for the first request that is ready
	if(drain_writes[channel])
	{

		LL_FOREACH(write_queue_head[channel], wr_ptr)
		{
      int bank = wr_ptr->dram_addr.bank;
  		int rank = wr_ptr->dram_addr.rank;
  		int row = wr_ptr->dram_addr.row;
      is_hit_state[channel] = (row == dram_state[channel][rank][bank].active_row) ? 1:0;
      is_open_state[channel] = sat_ctr(is_hit_state[channel], is_open_state[channel]);
			if(wr_ptr->command_issuable)
			{
        if(is_open_state[channel]){
          issue_request_command(wr_ptr);
  				break;
        }
				else{
          issue_request_command(wr_ptr);
          if(is_autoprecharge_allowed(channel, rank, bank)){
            issue_autoprecharge(channel, rank, bank);
          }
        }
			}
		}
		return;
	}

	// Draining Reads
	// look through the queue and find the first request whose
	// command can be issued in this cycle and issue it
	// Simple FCFS
	if(!drain_writes[channel])
	{
		LL_FOREACH(read_queue_head[channel],rd_ptr)
		{
      int bank = rd_ptr->dram_addr.bank;
  		int rank = rd_ptr->dram_addr.rank;
  		int row = rd_ptr->dram_addr.row;
      is_hit_state[channel] = (row == dram_state[channel][rank][bank].active_row) ? 1:0;
      is_open_state[channel] = sat_ctr(is_hit_state[channel], is_open_state[channel]);
			if(rd_ptr->command_issuable)
			{
        if(is_open_state[channel]){
          issue_request_command(rd_ptr);
          break;
			  }
        else
        {
          issue_request_command(rd_ptr);
          if(is_autoprecharge_allowed(channel, rank, bank)){
            issue_autoprecharge(channel, rank, bank);
          }
		    }
		return;
	}
}

void scheduler_stats()
{
  /* Nothing to print for now. */
}
