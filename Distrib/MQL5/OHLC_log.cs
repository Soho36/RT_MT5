void OnTick()
{
   static datetime Old_Time;
   datetime New_Time[1];
   bool IsNewBar = false;

   int copied = CopyTime(_Symbol, _Period, 0, 1, New_Time);
   if (copied > 0)
   {
      if (Old_Time != New_Time[0])
      {
         IsNewBar = true;

         double open = iOpen(_Symbol, _Period, 1);
         double high = iHigh(_Symbol, _Period, 1);
         double low = iLow(_Symbol, _Period, 1);
         double close = iClose(_Symbol, _Period, 1);
         long volume = iVolume(_Symbol, _Period, 1); // Use long for volume

         Print(open, ";", high, ";", low, ";", close, ";", volume);
         SaveOHLCVToFile(open, high, low, close, volume);

         Old_Time = New_Time[0];
      }
   }
   else
   {
      Alert("Error in copying historical times data, error =", GetLastError());
      ResetLastError();
      return;
   }

   if (!IsNewBar)
   {
      return;
   }
}

// Function to save OHLCV data to a file
void SaveOHLCVToFile(double open, double high, double low, double close, long volume)
{
    // Specify the file path (it will save to MQL5/Files directory by default)
    int file_handle = FileOpen("OHLCVData_475.csv", FILE_WRITE | FILE_CSV | FILE_END, ";");
    if (file_handle != INVALID_HANDLE)
    {
        FileSeek(file_handle, 0, SEEK_END); // Move to the end of the file

        // Get the date and time as separate strings
        string date = TimeToString(TimeCurrent(), TIME_DATE);
        string time = TimeToString(TimeCurrent(), TIME_MINUTES);

        // Write the Date and Time as separate columns
        FileWrite(file_handle, _Symbol, EnumToString(_Period), date, time,
                  DoubleToString(open, _Digits), DoubleToString(high, _Digits),
                  DoubleToString(low, _Digits), DoubleToString(close, _Digits),
                  IntegerToString(volume)); // Use IntegerToString for long type

        FileClose(file_handle);
    }
    else
    {
        Print("Failed to open the file for writing, error: ", GetLastError());
    }
}
