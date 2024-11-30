// Declare global variables
string positionStateFilePath = "PositionState.txt";
string lastPositionState = "";

// Function to update position state
void UpdatePositionState()
{
   // Determine the current position state based on open positions
   string currentPositionState = PositionsTotal() > 0 ? "opened" : "closed";

   // Check if the state has changed
   if (currentPositionState != lastPositionState)
   {
      int fileHandle = FileOpen(positionStateFilePath, FILE_WRITE | FILE_TXT | FILE_ANSI);

      if (fileHandle != INVALID_HANDLE)
      {
         FileWriteString(fileHandle, currentPositionState);
         Print("Position state updated: ", currentPositionState);
         FileClose(fileHandle);

         // Update the last tracked state
         lastPositionState = currentPositionState;
      }
      else
      {
         Print("Error writing position state to file. Error: ", GetLastError());
      }
   }
}

// OnTimer Event to periodically check position state
void OnTimer()
{
   UpdatePositionState();
}

// Initialization
int OnInit()
{
   // Set timer for periodic checks (e.g., every 5 seconds)
   EventSetTimer(5);
   return INIT_SUCCEEDED;
}

// Deinitialization
void OnDeinit(const int reason)
{
   EventKillTimer();
}
