package com.Qrec;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.StringTokenizer;
import java.util.concurrent.TimeUnit;

import org.ini4j.Ini;

public class ThreadManagement {


    public static void main(String[] args) {

        List<ProjectThread> threads = new ArrayList<ProjectThread>();
        long startTime = System.nanoTime();    

        try{
            File fileToParse = new File("config.ini");
            Ini ini = new Ini(fileToParse);
    
            
            String trainDirRelativePath = ini.get("User", "train_dir");
            int numWorkers = Integer.parseInt(ini.get("System", "num_cores"));
    
            //https://stackoverflow.com/questions/2683676/generating-a-canonical-path
            File trainDirFile = new File("src").getAbsoluteFile(); 
            String delimiters = "" + '\\' + '/';         
            StringTokenizer st = new StringTokenizer(trainDirRelativePath, delimiters);
            while(st.hasMoreTokens()) {
                String s = st.nextToken();
                if(s.trim().isEmpty() || s.equals(".")) 
                    continue;
                else if(s.equals("..")) 
                    trainDirFile = trainDirFile.getParentFile();
                else {
                    trainDirFile = new File(trainDirFile, s);
                    if(!trainDirFile.exists())
                        throw new RuntimeException("Data folder does not exist.");
                }
            }
    
            MainCSVFile mainCSVFile = new MainCSVFile();
            List<File> fileList = Arrays.asList(trainDirFile.listFiles());
            List<ProjectProcessingTask> projectProcessingTasks = fileList.stream().map( file -> {
                return new ProjectProcessingTask(file, mainCSVFile);}).toList();
    

            for (int i = 0; i < numWorkers; i++){
                ProjectThread thread = new ProjectThread(projectProcessingTasks, String.valueOf(i+1));
                threads.add(thread);
                thread.start();
            }
    
            //Wait for each thread to finish
            threads.forEach( thread -> {
                try {
                    thread.join();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            });
        }
    
        catch (Exception e){
            e.printStackTrace();
        }

        //clean up
        finally{
            long estimatedTime = System.nanoTime() - startTime;
            System.out.print("Cleaning up result files");
            threads.forEach(thread -> {
                String command = "rm -rf " + "thread_" + String.valueOf(thread.getThreadId()) + "_result" + ".csv";
                try {
                    Runtime.getRuntime().exec(command.toString(), null, new File("data"));
                } catch (IOException e) {
                    e.printStackTrace();
                } 
            });
            
            System.out.print("Finished. Elapsed time: " + String.valueOf(TimeUnit.MINUTES.convert(estimatedTime, TimeUnit.NANOSECONDS)) + " (min)");

        }

        
    }
}