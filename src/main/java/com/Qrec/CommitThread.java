package com.Qrec;

import java.util.List;

public class CommitThread extends Thread {


    private List<CommitProcessingTask> processingTasks;
    private String threadId;

    public CommitThread ( List<CommitProcessingTask> processingTasks, String threadId){            
        this.processingTasks = processingTasks;
        this.threadId = threadId;
    }
    
    public String getThreadId(){
        return this.threadId;
    }
    public void extractData(){
        for (CommitProcessingTask task : processingTasks){
            task.process(threadId);
            continue;
        }
    }
    
    public void run() {
        try{

            extractData();


        } catch (Exception e){
            e.printStackTrace();
        }
    }

}