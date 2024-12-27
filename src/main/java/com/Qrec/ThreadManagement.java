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

        List<CommitThread> threads = new ArrayList<CommitThread>();
        long startTime = System.nanoTime();    
        try{
            File fileToParse = new File("config.ini");
            Ini ini = new Ini(fileToParse);
    
            String dirRelativePath = ini.get("User", "multi_thread_dir");
            int numWorkers = Integer.parseInt(ini.get("System", "num_cores"));
            
            //https://stackoverflow.com/questions/2683676/generating-a-canonical-path
            File trainDirFile = new File("src").getAbsoluteFile(); 
            String delimiters = "" + '\\' + '/';         
            StringTokenizer st = new StringTokenizer(dirRelativePath, delimiters);
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
            List<CommitProcessingTask> projectProcessingTasks = fileList.stream().map( file -> {
                return new CommitProcessingTask(file, mainCSVFile);}).toList();
    

            for (int i = 0; i < numWorkers; i++){
                CommitThread thread = new CommitThread(projectProcessingTasks, String.valueOf(i+1));
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
            System.out.println("Cleaning up result files");
            threads.forEach(thread -> {
                File thread_result_file;
                File thread_log_file;
                try {
                    File fileToParse = new File("config.ini");
                    Ini ini = new Ini(fileToParse);
                    String is_original_run = ini.get("User", "is_original_run");

                    if ("TRUE".equals(is_original_run.toUpperCase())){
                        thread_result_file = new File( new File("data").getCanonicalPath() + "/thread_" + String.valueOf(thread.getThreadId()) + "_result_data" + ".csv");
                        thread_result_file = new File( new File("data").getCanonicalPath() + "/thread_" + String.valueOf(thread.getThreadId()) + "_result_label" + ".csv");
                    }
                    else{
                        thread_result_file = new File( new File("data").getCanonicalPath() + "/thread_" + String.valueOf(thread.getThreadId()) + "_result" + ".csv");
                        thread_result_file.delete();
                    }

                    thread_log_file = new File( new File("data").getCanonicalPath() + "/thread_" + String.valueOf(thread.getThreadId()) + "_log" + ".txt");
                    thread_log_file.delete();
                    
                } catch (IOException e) {
                    e.printStackTrace();
                }
            });
            
            System.out.println("Finished. Elapsed time: " + String.valueOf(TimeUnit.MINUTES.convert(estimatedTime, TimeUnit.NANOSECONDS)) + " (mins)");
        }

        
    }
}