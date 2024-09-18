package com.Qrec;

import java.util.concurrent.locks.ReentrantLock;
import java.io.*;

public class ProjectProcessingTask {

        private File projectFile;
        private ReentrantLock lock;
        private boolean isProcessed;
        private MainCSVFile mainCSVFile;

        public ProjectProcessingTask(File projectFile, MainCSVFile mainCSVFile) {
            this.projectFile = projectFile;
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
                command.append(" --project " + projectFile.getCanonicalPath());
                command.append(" --outputfile " + resultFileName);

                System.out.println("Thread id " + threadId + " is computing project: " + projectFile.getAbsolutePath());

                //executing command
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

                System.out.println("Thread id " + threadId + " finished computing project: " + projectFile.getAbsolutePath() + " with status code: " + String.valueOf(statusCode));
                System.out.println("Thread id " + threadId + " is appending result of " + projectFile.getAbsolutePath() + " to the main csv file");

                mainCSVFile.writeToFile(threadId, resultFilePath);
                
                System.out.println("Thread id " + threadId + " finished processing project " + projectFile.getAbsolutePath());
                

            } catch (Exception e) {
                System.out.println("Thread id " + threadId + " encountered an exception when executing project: " + projectFile.getAbsolutePath());
                e.printStackTrace();
            } finally {
                this.isProcessed = true;
                lock.unlock();
            }

        }
    }