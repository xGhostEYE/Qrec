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
                Process proc = Runtime.getRuntime().exec("python3 parserproject.py");                        
                proc.waitFor();
                System.out.println("Thread id " + threadId + " finished executing project: " + projectFile.getAbsolutePath());

            } catch (Exception e) {
            } finally {
                this.isProcessed = true;
                lock.unlock();
            }

        }
    }