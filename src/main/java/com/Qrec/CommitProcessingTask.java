package com.Qrec;

import java.util.concurrent.locks.ReentrantLock;
import java.io.*;

public class CommitProcessingTask {

        private File commitFile;
        private ReentrantLock lock;
        private boolean isProcessed;
        private MainCSVFile mainCSVFile;

        public CommitProcessingTask(File commitFile, MainCSVFile mainCSVFile) {
            this.commitFile = commitFile;
            this.lock = new ReentrantLock();
            this.isProcessed = false;
            this.mainCSVFile = mainCSVFile;
        }

        public void process(String threadId){

            boolean isLockAcquired = lock.tryLock();
            
            if (!isLockAcquired || isProcessed){
                return;
            }

            try {                
                //Building command                                
                String resultFileName  = "thread_" + String.valueOf(threadId) + "_result" + ".csv";
                String resultFilePath  = new File("data").getCanonicalPath() + "/thread_" + String.valueOf(threadId) + "_result" + ".csv";
                StringBuilder command = new StringBuilder("python3 parserproject.py");  
                String relativeCommitFilePath = "../" + (new File("").toURI().relativize(commitFile.toURI()));
                System.out.print("check" + relativeCommitFilePath);
                command.append(" --commit " + relativeCommitFilePath);
                command.append(" --outputfile " + resultFileName);

                System.out.println("Thread id " + threadId + " is computing commit: " + commitFile.getAbsolutePath());

                //Executing command
                ProcessBuilder pb = new ProcessBuilder(command.toString().split(" ")).redirectErrorStream(true);
                pb.directory(new File("src"));
                Process process = pb.start();

                
                String logFilePath  = new File("data").getCanonicalPath() + "/thread_" + String.valueOf(threadId) + "_log" + ".txt";
                try (BufferedReader br = new BufferedReader(new InputStreamReader(process.getInputStream()));
                     BufferedWriter bw = new BufferedWriter(new FileWriter(logFilePath)))
                {
                    br.transferTo(bw);
                    while (true)
                    {
                        String line = br.readLine();
                        if (line == null)
                            break;
                        bw.write(line);
                        bw.newLine();
                        bw.flush(); 
                    }
                }
               
                int statusCode = process.waitFor();

                System.out.println("Thread id " + threadId + " finished computing commit: " + commitFile.getAbsolutePath() + " with status code: " + String.valueOf(statusCode));
                System.out.println("Thread id " + threadId + " is appending result of " + commitFile.getAbsolutePath() + " to the main csv file");

                mainCSVFile.writeToFile(threadId, resultFilePath);
                
                System.out.println("Thread id " + threadId + " finished processing commit " + commitFile.getAbsolutePath());
                

            } catch (Exception e) {
                System.out.println("Thread id " + threadId + " encountered an exception when executing commit: " + commitFile.getAbsolutePath());
                e.printStackTrace();
            } finally {
                this.isProcessed = true;
                lock.unlock();
            }

        }
    }