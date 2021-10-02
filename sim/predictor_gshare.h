///////////////////////////////////////////////////////////////////////
////  Copyright 2015 Samsung Austin Semiconductor, LLC.                //
/////////////////////////////////////////////////////////////////////////
//
#ifndef _PREDICTOR_H_
#define _PREDICTOR_H_

#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <inttypes.h>
#include <math.h>
#include "utils.h"
#include "bt9.h"
#include "bt9_reader.h"

#define PHT_CTR_MAX  3
#define PHT_CTR_INIT 2

#define HIST_LEN   17

//NOTE competitors are allowed to change anything in this file

/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

class PREDICTOR{

  // The state is defined for Gshare, change for your design

 private:
  UINT32  ghr;           // global history register
  UINT32  *pht;          // pattern history table
  UINT32  historyLength; // history length
  UINT32  numPhtEntries; // entries in pht 

 public:


  PREDICTOR(void);
  // The interface to the functions below CAN NOT be changed
  bool    GetPrediction(UINT64 PC);  
  void    UpdatePredictor(UINT64 PC, OpType opType, bool resolveDir, bool predDir, UINT64 branchTarget);
  void    TrackOtherInst(UINT64 PC, OpType opType, bool branchDir, UINT64 branchTarget);

  // Contestants can define their own functions below
};

/////////////// STORAGE BUDGET JUSTIFICATION ////////////////
// Total storage budget: 32KB + 17 bits
// Total PHT counters: 2^17 
// Total PHT size = 2^17 * 2 bits/counter = 2^18 bits = 32KB
// GHR size: 17 bits
// Total Size = PHT size + GHR size
/////////////////////////////////////////////////////////////



/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

PREDICTOR::PREDICTOR(void){

  historyLength    = HIST_LEN;
  ghr              = 0;
  numPhtEntries    = (1<< HIST_LEN);

  pht = new UINT32[numPhtEntries];

  for(UINT32 ii=0; ii< numPhtEntries; ii++){
    pht[ii]=PHT_CTR_INIT; 
  }
  
}

/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

bool    PREDICTOR::GetPrediction(UINT64 PC){

  UINT32 phtIndex   = (PC^ghr) % (numPhtEntries);
  UINT32 phtCounter = pht[phtIndex];

//  printf(" ghr: %x index: %x counter: %d prediction: %d\n", ghr, phtIndex, phtCounter, phtCounter > PHT_CTR_MAX/2);

  if(phtCounter > (PHT_CTR_MAX/2)){ 
    return TAKEN; 
  }
  else{
    return NOT_TAKEN; 
  }
}


/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

void    PREDICTOR::UpdatePredictor(UINT64 PC, OpType opType, bool resolveDir, bool predDir, UINT64 branchTarget){

  UINT32 phtIndex   = (PC^ghr) % (numPhtEntries);
  UINT32 phtCounter = pht[phtIndex];

  if(resolveDir == TAKEN){
    pht[phtIndex] = SatIncrement(phtCounter, PHT_CTR_MAX);
  }else{
    pht[phtIndex] = SatDecrement(phtCounter);
  }

  // update the GHR
  ghr = (ghr << 1);

  if(resolveDir == TAKEN){
    ghr++; 
  }
}

/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

void    PREDICTOR::TrackOtherInst(UINT64 PC, OpType opType, bool branchDir, UINT64 branchTarget){

  // This function is called for instructions which are not
  // conditional branches, just in case someone decides to design
  // a predictor that uses information from such instructions.
  // We expect most contestants to leave this function untouched.

  return;
}

/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////


/***********************************************************/
#endif

