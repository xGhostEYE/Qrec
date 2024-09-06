package com.Qrec;

import java.io.File;
import java.io.IOException;
import java.util.StringTokenizer;

import org.ini4j.Ini;
import org.ini4j.InvalidFileFormatException;

public class ThreadManagement {
    public class ProjectThread extends Thread {

        private String projectPath;
        
        public ProjectThread (String projectPath){
            this.projectPath = projectPath;
        }
        public void run() {
            System.out.println("This code is running in a thread");
          }
    }

    public static void main(String[] args) throws InvalidFileFormatException, IOException {
        File fileToParse = new File("config.ini");
        Ini ini = new Ini(fileToParse);

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

        File filesList[] = trainDirFile.listFiles();

        System.out.println("List of files and directories in the specified directory:");
        for(File file : filesList) {
           System.out.println("File name: "+file.getName());
           System.out.println("File path: "+file.getAbsolutePath());
           System.out.println("Size :"+file.getTotalSpace());
           System.out.println(" ");
        }
    }
}
