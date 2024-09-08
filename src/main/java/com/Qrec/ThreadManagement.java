package com.Qrec;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.StringTokenizer;

import org.ini4j.Ini;
import org.ini4j.InvalidFileFormatException;

public class ThreadManagement {


    public static void main(String[] args) throws InvalidFileFormatException, IOException {
        File fileToParse = new File("config.ini");
        Ini ini = new Ini(fileToParse);

        final int NUM_WORKERS = 8;
        
        String trainDirRelativePath = ini.get("User", "train_dir");

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

        List<File> fileList = Arrays.asList(trainDirFile.listFiles());
        List<ProjectProcessingTask> projectProcessingTasks = fileList.stream().map( file -> {
            return new ProjectProcessingTask(file);}).toList();

        
        for (int i = 0; i < NUM_WORKERS; i++){
            ProjectThread thread = new ProjectThread(projectProcessingTasks, String.valueOf(i+1));
            thread.start();
        }

        
    }
}