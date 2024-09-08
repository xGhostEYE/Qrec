package com.Qrec;

import java.io.File;
import java.util.concurrent.locks.ReentrantLock;

public class ProjectProcessingTask {

        private File projectFile;
        private ReentrantLock lock;
        private boolean isProcessed;

        public ProjectProcessingTask(File projectFile) {
            this.projectFile = projectFile;
            this.lock = new ReentrantLock();
            this.isProcessed = false;
        }

        public void process(String threadId){

            boolean isLockAcquired = lock.tryLock();
            
            if (!isLockAcquired || isProcessed){
                return;
            }

            try {
                System.out.println("Thread id " + threadId + " is executing project: " + projectFile.getAbsolutePath());
                
                //Building command
                StringBuilder command = new StringBuilder("python3 parserproject.py");
                command.append(" --project " + projectFile.getCanonicalPath());
                command.append(" --outputfile " + "thread_" + String.valueOf(threadId) + "_result" + ".csv");

                System.out.println("Thread id " + threadId + " is executing project: " + projectFile.getAbsolutePath() + " with command: " + command.toString());
 
                Process proc = Runtime.getRuntime().exec(command.toString(), null, new File("src"));                                             
                
                int statusCode = proc.waitFor();
                System.out.println("Thread id " + threadId + " finished executing project: " + projectFile.getAbsolutePath() + " with status code: " + String.valueOf(statusCode));

            } catch (Exception e) {
                System.out.println("Thread id " + threadId + " encountered exception when executing project: " + projectFile.getAbsolutePath());
                e.printStackTrace();
            } finally {
                this.isProcessed = true;
                lock.unlock();
            }

        }
    }