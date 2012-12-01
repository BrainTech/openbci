package org.signalml.app.util;
/**
 * A class to help benchmark code
 * It simulates a real stop watch
 */
public class Stopwatch {
  private long startTime = -1;
  private long lastTime = -1;
  private long cumTime;
  private int count = 0;
  
  
  public Stopwatch() {
	  this.reset();
  }
  public Stopwatch reset() {
	     startTime = -1;
	     cumTime = 0;
	     count = 0;
	     lastTime = 0;
	     return this;
	  }
  
  public void start() {
     startTime = System.currentTimeMillis();
     count += 1;
  }
  public void stop() {
	 lastTime = System.currentTimeMillis() - startTime;
     cumTime += lastTime;
  }
  
  /** returns elapsed time in milliseconds
    * if the watch has never been started then
    * return zero
    */
  public long getElapsedTime() {
     return cumTime;
  }
  
  public long getStartTime() {
	  return startTime;
  }
  public long getLastTime() {
	  return lastTime;
  }
  
  public String getElapsedTimeDesc() {
	  return this.getElapsedTimeDesc(cumTime);
  }

  public String getElapsedTimeDesc(long t) {
	  int sec = ((int)t)/1000;
	  int mils = ((int) t) - 1000*sec;
	  int mins = (int) sec/60;
	  sec = sec - 60*mins;
	  return "(m:s.mils) "+mins+":"+sec+"."+mils;
  };
  
  public int getElapsedCount() {
	  return count;
  }
}
