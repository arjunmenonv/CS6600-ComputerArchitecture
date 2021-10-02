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

#define GPT_CTR_MAX  3
#define GPT_CTR_INIT 2
#define LPT_CTR_MAX  3
#define LPT_CTR_INIT 2
#define CPT_CTR_MAX  3
#define CPT_CTR_INIT 1
#define LHT_INIT     0
#define GHR_INIT     0

#define GPRED_LEN   14
#define LHIST_LEN   11
#define LPRED_LEN   14
#define CPRED_LEN   14

//NOTE competitors are allowed to change anything in this file

/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

class PREDICTOR{

 private:

  // GLOBAL Predictor related
  UINT32  ghr;           	// global history register
  UINT32  *gpt;          	// global predictor table
  UINT32  numGptEntries; 	// entries in gpt

  // LOCAL Predictor related
  UINT32  *lht; 		// local history table
  UINT32  numLhtEntries; 	// entries in lht
  UINT32  *lpt; 		// local predictor table  (for particular branch)
  UINT32  numLptEntries;        // entries in lpt 	  (for particular branch)

  // CHOICE Predictor related
  UINT32  *cpt; 		// choice predictor table
  UINT32  numCptEntries; 	// entries in cpt

 public:


  PREDICTOR(void);
  ~PREDICTOR();

  // The interface to the functions below CAN NOT be changed
  bool    GetPrediction(UINT64 PC);
  void    UpdatePredictor(UINT64 PC, OpType opType, bool resolveDir, bool predDir, UINT64 branchTarget);
  void    TrackOtherInst(UINT64 PC, OpType opType, bool branchDir, UINT64 branchTarget);

  // Contestants can define their own functions below
  void    TrackcptBias();

  // counters to track BP's behaviour
  UINT32 PredT;
  UINT32 PredNT;
  UINT32 TrueT;
  UINT32 TrueNT;
  UINT32 cptStateTrack[CPT_CTR_MAX + 1];
};

/////////////// STORAGE BUDGET JUSTIFICATION ////////////////
// Total storage budget: 16KB = 128Kbits
// Total GPT counters: 16384
// Total GPT size = 16384*2 = 32Kbits
// GHR size: 14 bits
// Total LPT counters: 16384
// Total LPT size = 16384*2 = 32Kbits
// Total LHT size = 2048*14 = 28Kbits
// Total CPT size = 16384*2 = 32Kbits
// Total Size = 124Kbits + 14bits
/////////////////////////////////////////////////////////////



/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

PREDICTOR::PREDICTOR(void){

  // Global Predictor
  ghr              	 = GHR_INIT;
  numGptEntries    	 = (1<< GPRED_LEN);
  gpt 			 = new UINT32[numGptEntries];
  for(UINT32 ii=0; ii< numGptEntries; ii++)
    gpt[ii]=GPT_CTR_INIT;

  // Local Predictor
  numLhtEntries          = (1<< LHIST_LEN);
  lht                	 = new UINT32[numLhtEntries];
  numLptEntries          = (1<< LPRED_LEN);
  lpt       		 = new UINT32[numLptEntries];
  for(UINT32 ii=0; ii< numLhtEntries; ii++)
    lht[ii]=LHT_INIT;
  for(UINT32 ii=0; ii< numLptEntries; ii++)
    lpt[ii]=LPT_CTR_INIT;

  // Choice Predictor
  numCptEntries     	 = (1<< CPRED_LEN);
  cpt                	 = new UINT32[numCptEntries];
  for(UINT32 ii=0; ii< numCptEntries; ii++)
    cpt[ii]=CPT_CTR_INIT;

  // init counters
  PredT = 0;
  PredNT = 0;
  TrueT = 0;
  TrueNT = 0;
  for(UINT32 ii = 0; ii<= CPT_CTR_MAX; ii++)
    cptStateTrack[ii] = 0;
}

PREDICTOR::~PREDICTOR(){
  // Destructor to deallocate dynamically allocated memory
  delete[] gpt;
  delete[] lht;
  delete[] lpt;
  delete[] cpt;
  // And reset global history register (optional)
  ghr = GHR_INIT;
}
/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

bool    PREDICTOR::GetPrediction(UINT64 PC){
  /*
    REMARK: Should PC be right-shifted by 2 (or log(sizeof(instr))) first?
            - For current impl, check if there are registers in LPT that are never written
  */

  UINT32 lhtIndex = (PC>>2) % (numLhtEntries);
  UINT32 lptIndex = lht[lhtIndex] % (numLptEntries);
  UINT32 lptCounter = lpt[lptIndex];
  bool lDecision = (lptCounter > LPT_CTR_MAX/2) ? TAKEN : NOT_TAKEN;

  UINT32 gptIndex = (ghr) % (numGptEntries);
  UINT32 gptCounter = gpt[gptIndex];
  bool gDecision = (gptCounter > GPT_CTR_MAX/2) ? TAKEN :  NOT_TAKEN;

  UINT32 cptIndex = (ghr) % (numCptEntries);
  UINT32 cptCounter = cpt[cptIndex];
  bool cBias = (cptCounter > CPT_CTR_MAX/2) ? 1 : 0;

  if (cBias){
    if(gDecision == TAKEN)  PredT++;
    else PredNT++;
    return gDecision;
  }
  else {
    if(lDecision == TAKEN)  PredT++;
    else PredNT++;
    return lDecision;
  }
}


/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

void    PREDICTOR::UpdatePredictor(UINT64 PC, OpType opType, bool resolveDir, bool predDir, UINT64 branchTarget){
  /*
    REMARKS: - In hardware during update phase, the decision has to either be read again, or a data
               structure addressable by PC (dict) holding predicted direction has to be maintained

    Changes made by Arjun:
      - GetPredictor() return type is bool; using bool for g/lDecision for consistency
      - Decision assignment: > instead of >= (3/2 := 1)
  */
  UINT32 gptIndex   = (ghr) % (numGptEntries);
  UINT32 gptCounter = gpt[gptIndex];
  UINT32 gDecision  = (gptCounter > GPT_CTR_MAX/2) ? TAKEN : NOT_TAKEN;

  UINT32 lhtIndex   = (PC>>2) % (numLhtEntries);
  UINT32 lptIndex   = lht[lhtIndex] % (numLptEntries);
  UINT32 lptCounter = lpt[lptIndex];
  UINT32 lDecision  = (lptCounter > LPT_CTR_MAX/2) ? TAKEN : NOT_TAKEN;

  UINT32 cptIndex   = (ghr) % (numCptEntries);
  UINT32 cptCounter = cpt[cptIndex];

  // update local history table and global history table entries
  if(resolveDir == TAKEN){
    gpt[gptIndex] = SatIncrement(gptCounter, GPT_CTR_MAX);
    lpt[lptIndex] = SatIncrement(lptCounter, LPT_CTR_MAX);
    TrueT++;
  }else{
    gpt[gptIndex] = SatDecrement(gptCounter);
    lpt[lptIndex] = SatDecrement(lptCounter);
    TrueNT++;
  }

  // update choice predictor
  if(lDecision != gDecision){ // both disagree
    if(resolveDir == lDecision) // local is correct - give more weight to local
      cpt[cptIndex] = SatDecrement(cptCounter);
    else // global is correct - give more weight to global
      cpt[cptIndex] = SatIncrement(cptCounter, CPT_CTR_MAX);
  }else{ // both agree
    if(lDecision == resolveDir){ // both are correct
      if(cptCounter > CPT_CTR_MAX/2) // make global even stronger
	cpt[cptIndex] = SatIncrement(cptCounter, CPT_CTR_MAX);
      else
	cpt[cptIndex] = SatDecrement(cptCounter);
    }
  }

  // update the GHR, LPT Entry
  ghr = (ghr << 1);
  lht[lhtIndex] = lptIndex << 1;

  if(resolveDir == TAKEN){
    ghr++;
    lht[lhtIndex]++;
  }
}

/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////

void PREDICTOR::TrackcptBias(){
  for(UINT32 ii=0; ii< numCptEntries; ii++){
    UINT32 cptEntry = cpt[ii];
    if(cptEntry <= CPT_CTR_MAX)
      cptStateTrack[cptEntry]++;
    else
      printf("Erroneous state in CPT\n");
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
