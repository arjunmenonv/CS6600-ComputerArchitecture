#include <stdio.h>
#include "utlist.h"
#include "utils.h"

#include "memory_controller.h"
#include "scheduler_adaptive.h"
// Comments for self: Remove before committing
// memory_controller.h is included, hence dram_state can be accessed here
// use rd_ptr->dram_addr.row and dram_state.active_row to check for row hit or miss

extern long long int CYCLE_VAL;
#define HIGH_THRESH 10
#define LOW_THRESH 5
#define PLOT_HIST 1
typedef enum {OPEN_PAGE, CLOSE_PAGE} policy_t;

// State Variables used in AdapPage:
int counter[MAX_NUM_CHANNELS][MAX_NUM_RANKS][MAX_NUM_BANKS];
policy_t curr_policy[MAX_NUM_CHANNELS][MAX_NUM_RANKS][MAX_NUM_BANKS];
int prev_closed_row[MAX_NUM_CHANNELS][MAX_NUM_RANKS][MAX_NUM_BANKS];
int recent_colacc[MAX_NUM_CHANNELS][MAX_NUM_RANKS][MAX_NUM_BANKS];
// write policy history for (c,r,b) = (0, 0, 0) to a csv file
//
FILE *fptr;
int trackdC = 0; int trackdR = 0; int trackdB = 0;

void init_scheduler_vars(){
	// initialize all scheduler variables here:
	// Initially ctr between HighThresh and LowThresh, use open page policy
	for(int i = 0; i < MAX_NUM_CHANNELS; i++){
		for(int j = 0; j < MAX_NUM_CHANNELS; j++){
			for(int k = 0; k < MAX_NUM_CHANNELS; k++){
				counter[i][j][k] = (int)(HIGH_THRESH + LOW_THRESH)/2;
				curr_policy[i][j][k] = OPEN_PAGE;
				recent_colacc[i][j][k] = 0;
                prev_closed_row[i][j][k] = -1;
			}
		}
	}
	//printf("init sched vars ended\n");
	return;
}

// write queue high water mark; begin draining writes if write queue exceeds this value
#define HI_WM 40

// end write queue drain once write queue has this many writes in it
#define LO_WM 20


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

/*
 * Input: Variable to indicate Cache Hit or Miss; PrevPolicy; HighThresh, LowThresh
 * Output: Policy var (open/closed)
*/
policy_t get_policy(int channel, int rank, int bank, int hit, policy_t curr_policy){
	policy_t next_policy;

	if (curr_policy == OPEN_PAGE){
		if(!(hit) && (counter[channel][rank][bank] < 15))
			counter[channel][rank][bank]++;
		if(counter[channel][rank][bank] >= HIGH_THRESH)
			next_policy = CLOSE_PAGE;
		else
			next_policy = OPEN_PAGE;
	}
	else{
		if(hit && (counter[channel][rank][bank] > 0))
			counter[channel][rank][bank]--;
		if(counter[channel][rank][bank] <= LOW_THRESH)
			next_policy = OPEN_PAGE;
		else
			next_policy = CLOSE_PAGE;
	}
	/* printf("get_policy ended. Policy is:"); */
	/* if(next_policy == OPEN_PAGE) */
	/* 	printf("Open page\n"); */
	/* else */
	/* 	printf("Close page\n"); */
	return next_policy;
}

void schedule(int channel){
	request_t * rd_ptr = NULL;
	request_t * wr_ptr = NULL;

	if (PLOT_HIST) fptr = fopen("output/polHist.csv", "a");

	// if in write drain mode, keep draining writes until the
	// write queue occupancy drops to LO_WM
	if (drain_writes[channel] && (write_queue_length[channel] > LO_WM))
		drain_writes[channel] = 1; // Keep draining.
	else
		drain_writes[channel] = 0; // No need to drain.

	// initiate write drain if either the write queue occupancy
	// has reached the HI_WM , OR, if there are no pending read
	// requests
	if(write_queue_length[channel] > HI_WM)
		drain_writes[channel] = 1;
	else if (!read_queue_length[channel])
		drain_writes[channel] = 1;

	// If in write drain mode, look through all the write queue
	// elements (already arranged in the order of arrival), and
	// issue the command for the first request that is ready
	if(drain_writes[channel]){
		//printf("In write drain\n");
		LL_FOREACH(write_queue_head[channel], wr_ptr){
			int bank = wr_ptr->dram_addr.bank;
			int rank = wr_ptr->dram_addr.rank;
			int row = wr_ptr->dram_addr.row;

			int row_buffer_hit;
            int should_pre;
			if(wr_ptr->command_issuable){
                if(curr_policy[channel][rank][bank] == OPEN_PAGE){
                    if(row == dram_state[channel][rank][bank].active_row)
                        row_buffer_hit = 1;
                    else
                        row_buffer_hit = 0;
                    curr_policy[channel][rank][bank] = get_policy(channel, rank, bank, row_buffer_hit, curr_policy[channel][rank][bank]);
					issue_request_command(wr_ptr);
					if ((PLOT_HIST) && (channel == trackdC) && (rank == trackdR) && (bank == trackdB))
						fprintf(fptr, "%lld, %d \n", CYCLE_VAL, OPEN_PAGE);
					break;
                }
                else{
                    if(row == prev_closed_row[channel][rank][bank])
                        row_buffer_hit = 1;
                    else
                        row_buffer_hit = 0;
					/* Before issuing the command, see if this bank is now a candidate for closure (if it just did a column-rd/wr).
					If the bank just did an activate or precharge, it is not a candidate for closure. */
					if (wr_ptr->next_command == COL_WRITE_CMD){
                        should_pre = 1;
                        prev_closed_row[channel][rank][bank] = row;
                    }
					if (wr_ptr->next_command == ACT_CMD)
                        should_pre = 0;
					if (wr_ptr->next_command == PRE_CMD)
                        should_pre = 0;

                    curr_policy[channel][rank][bank] = get_policy(channel, rank, bank, row_buffer_hit, curr_policy[channel][rank][bank]);
					issue_request_command(wr_ptr);
					if ((PLOT_HIST) && (channel == trackdC) && (rank == trackdR) && (bank == trackdB))
						fprintf(fptr, "%lld, %d \n", CYCLE_VAL, CLOSE_PAGE);

					if(should_pre)
                        issue_autoprecharge(channel, rank, bank);
					break;
                }
			}
		}
	}

	// Draining Reads
	// look through the queue and find the first request whose
	// command can be issued in this cycle and issue it
	// Simple FCFS
	if(!drain_writes[channel]){
		/* printf("In read drain\n"); */
		LL_FOREACH(read_queue_head[channel],rd_ptr){
			int bank = rd_ptr->dram_addr.bank;
			int rank = rd_ptr->dram_addr.rank;
			int row = rd_ptr->dram_addr.row;

			int row_buffer_hit;
            int should_pre;
			if(rd_ptr->command_issuable){
				if(curr_policy[channel][rank][bank] == OPEN_PAGE){
                    if(row == dram_state[channel][rank][bank].active_row)
                        row_buffer_hit = 1;
                    else
                        row_buffer_hit = 0;

                    curr_policy[channel][rank][bank] = get_policy(channel, rank, bank, row_buffer_hit, curr_policy[channel][rank][bank]);
					issue_request_command(rd_ptr);
					if ((PLOT_HIST) && (channel == trackdC) && (rank == trackdR) && (bank == trackdB))
						fprintf(fptr, "%lld, %d \n", CYCLE_VAL, OPEN_PAGE);
					break;
				}
				else{
                    if(row == prev_closed_row[channel][rank][bank])
                        row_buffer_hit = 1;
                    else
                        row_buffer_hit = 0;
					/* Before issuing the command, see if this bank is now a candidate for closure (if it just did a column-rd/wr).
					If the bank just did an activate or precharge, it is not a candidate for closure. */
					if (rd_ptr->next_command == COL_READ_CMD){
                        should_pre = 1;
                        prev_closed_row[channel][rank][bank] = row;
                    }
					if (rd_ptr->next_command == ACT_CMD)
                        should_pre = 0;
					if (rd_ptr->next_command == PRE_CMD)
                        should_pre = 0;

                    curr_policy[channel][rank][bank] = get_policy(channel, rank, bank, row_buffer_hit, curr_policy[channel][rank][bank]);
					issue_request_command(rd_ptr);
					if ((PLOT_HIST) && (channel == trackdC) && (rank == trackdR) && (bank == trackdB))
						fprintf(fptr, "%lld, %d \n", CYCLE_VAL, CLOSE_PAGE);

					if(should_pre)
                        issue_autoprecharge(channel, rank, bank);
					break;
				}
			}
		}
	}
	if (PLOT_HIST) fclose(fptr);

}

void scheduler_stats(){
  /* Nothing to print for now. */
}
