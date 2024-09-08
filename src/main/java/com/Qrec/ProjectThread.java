package com.Qrec;

import java.util.List;

public class ProjectThread extends Thread {


    private List<ProjectProcessingTask> processingTasks;
    private String threadId;

    public ProjectThread ( List<ProjectProcessingTask> processingTasks, String threadId){            
        this.processingTasks = processingTasks;
        this.threadId = threadId;
    }

    //TODO
    public static synchronized void writeToCSV() {
        
    }
     
    //TODO
    public void extractData(){
        for (ProjectProcessingTask task : processingTasks){
            task.process(threadId);
            continue;
        }
    }
    
    public void run() {
        try{

            extractData();

            //Write output of run to CSV
            synchronized(ProjectThread.class) {
                writeToCSV();
            }

        } catch (Exception e){
            e.printStackTrace();
        }
    }

}