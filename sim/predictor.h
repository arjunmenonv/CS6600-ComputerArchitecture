/////////////////////////////////////////////////////////////////////////
// Tournament BPU
//
// Implemented by Akilesh Kannan, Arjun Menon V
/////////////////////////////////////////////////////////////////////////

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

#define GHT_CTR_MAX  3
#define GHT_CTR_INIT 2
#define LHT_CTR_MAX  3
#define LHT_CTR_INIT 2
#define CPT_CTR_MAX  3
#define CPT_CTR_INIT 2
#define LPT_INIT     0
#define CPT_INIT     1

#define GHIST_LEN   10
#define LHIST_LEN   10
#define LPRED_LEN   10
#define CPRED_LEN   10

//NOTE competitors are allowed to change anything in this file

/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

class PREDICTOR{

 private:

  // GLOBAL Predictor related
  UINT32  ghr;           	// global history register
  UINT32  *ght;          	// global history table
  UINT32  globalHistoryLength;  // history length
  UINT32  numGhtEntries; 	// entries in ght

  // LOCAL Predictor related
  UINT32  *lpt; 		// local predictor table
  UINT32  localPredictLength;   // local predictor length
  UINT32  numLptEntries; 	// entries in lpt
  UINT32  *lht; 		// local history table (for that particular branch)
  UINT32  localHistoryLength;   // local history length (for that particular branch)
  UINT32  numLhtEntries;        // entries in lht 	(for that particular branch)

  // CHOICE Predictor related
  UINT32  *cpt; 		// choice predictor table
  UINT32  choicePredictLength;  // choice predictor length
  UINT32  numCptEntries; 	// entries in cpt

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
// Total GHT counters: 2^17 
// Total GHT size = 2^17 * 2 bits/counter = 2^18 bits = 32KB
// GHR size: 17 bits
// Total Size = GHT size + GHR size
/////////////////////////////////////////////////////////////



/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

PREDICTOR::PREDICTOR(void){

  // Global Predictor
  globalHistoryLength    = GHIST_LEN;
  ghr              	 = 0;
  numGhtEntries    	 = (1<< GHIST_LEN);
  ght 			 = new UINT32[numGhtEntries];
  for(UINT32 ii=0; ii< numGhtEntries; ii++)
    ght[ii]=GHT_CTR_INIT; 

  // Local Predictor
  localPredictLength     = LPRED_LEN;
  localHistoryLength     = LHIST_LEN;
  numLhtEntries          = (1<< LHIST_LEN);
  numLptEntries          = (1<< LPRED_LEN);
  lht                	 = new UINT32[numLhtEntries];
  lpt       		 = new UINT32[numLptEntries];
  for(UINT32 ii=0; ii< numLptEntries; ii++)
    lpt[ii]=LPT_INIT;
  for(UINT32 ii=0; ii< numLhtEntries; ii++)
    lht[ii]=LHT_CTR_INIT;

  // Choice Predictor
  choicePredictLength    = CPRED_LEN;
  numCptEntries     	 = (1<< CPRED_LEN);
  cpt                	 = new UINT32[numCptEntries];
  for(UINT32 ii=0; ii< numCptEntries; ii++)
    cpt[ii]=CPT_INIT;  
}

/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

bool    PREDICTOR::GetPrediction(UINT64 PC){

  UINT32 ghtIndex   = (PC^ghr) % (numGhtEntries);
  UINT32 ghtCounter = ght[ghtIndex];

//  printf(" ghr: %x index: %x counter: %d prediction: %d\n", ghr, ghtIndex, ghtCounter, ghtCounter > GHT_CTR_MAX/2);

  if(ghtCounter > (GHT_CTR_MAX/2)){ 
    return TAKEN; 
  }
  else{
    return NOT_TAKEN; 
  }
}


/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

void    PREDICTOR::UpdatePredictor(UINT64 PC, OpType opType, bool resolveDir, bool predDir, UINT64 branchTarget){

  UINT32 ghtIndex   = (ghr) % (numGhtEntries);
  UINT32 ghtCounter = ght[ghtIndex];
  UINT32 gDecision  = (ghtCounter >= GHT_CTR_MAX/2) ? TAKEN : NOT_TAKEN;

  UINT32 lptIndex   = (PC) % (numLptEntries);
  UINT32 lhtIndex   = lpt[lptIndex];
  UINT32 lhtCounter = lht[lhtIndex];
  UINT32 lDecision  = (lhtCounter >= LHT_CTR_MAX/2) ? TAKEN : NOT_TAKEN;

  UINT32 cptIndex   = (ghr) % (numCptEntries);
  UINT32 cptCounter = cpt[cptIndex];

  // update local history table and global history table entries
  if(resolveDir == TAKEN){
    ght[ghtIndex] = SatIncrement(ghtCounter, GHT_CTR_MAX);
    lht[lhtIndex] = SatIncrement(lhtCounter, LHT_CTR_MAX);
  }else{
    ght[ghtIndex] = SatDecrement(ghtCounter);
    lht[lhtIndex] = SatDecrement(lhtCounter);
  }

  // update choice predictor
  if(lDecision != gDecision){ // both disagree
    if(resolveDir == lDecision) // local is correct - give more weight to local
      cpt[cptIndex] = SatDecrement(cptCounter);
    else // global is correct - give more weight to global
      cpt[cptIndex] = SatIncrement(cptCounter, CPT_CTR_MAX);
  }else{ // both agree
    if(lDecision == resolveDir){ // both are correct
      if(cptCounter >= CPT_CTR_MAX/2) // make global even stronger
	cpt[cptIndex] = SatIncrement(cptCounter, CPT_CTR_MAX);
      else
	cpt[cptIndex] = SatDecrement(cptCounter);
    }
  }

  // update the GHR, LPT Entry
  ghr = (ghr << 1);
  lpt[lptIndex] = lhtIndex << 1;

  if(resolveDir == TAKEN){
    ghr++; 
    lpt[lptIndex]++;
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

