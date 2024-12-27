package com.Qrec;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Reader;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;
import org.ini4j.Ini;
import org.ini4j.InvalidFileFormatException;

public class MainCSVFile {
    Ini ini;

    //For non original run
    File outputFile;

    //For orignal run
    File outputDataFile;
    File outputLabelFile;

    public MainCSVFile() throws InvalidFileFormatException, IOException{
            File fileToParse = new File("config.ini");
            this.ini = new Ini(fileToParse);
            String outputFileName = ini.get("User", "output_multi_thread_file_name");
            String is_original_run = ini.get("User", "is_original_run");

            if ("TRUE".equals(is_original_run.toUpperCase())){
                File outputDataFile = new File( new File("data").getCanonicalPath() + "/" + outputFileName.replaceAll(".csv","") + "data.csv" );
                File outputLabelFile = new File( new File("data").getCanonicalPath() + "/" + outputFileName.replaceAll(".csv","") + "label.csv" );

                this.outputDataFile = outputDataFile;
                this.outputLabelFile = outputLabelFile;

                if(outputDataFile.exists() && !outputDataFile.isDirectory()) {
                    outputDataFile.delete();
                }  

                if(outputLabelFile.exists() && !outputLabelFile.isDirectory()) {
                    outputLabelFile.delete();
                }  
            }
            else{
                File outputFile = new File( new File("data").getCanonicalPath() + "/" + outputFileName );
                this.outputFile = outputFile;
                
                //Delete the file if exist, so we can write new data into it later
                if(outputFile.exists() && !outputFile.isDirectory()) {
                    outputFile.delete();
                }  
            }
                  
    }
    public synchronized void writeToFile(String threadId, String resultFilePath) throws IOException{


            File outputFile = this.outputFile;
            File outputDataFile = this.outputDataFile;
            File outputLabelFile = this.outputLabelFile;

            FileWriter fw1; 
            FileWriter fw2;
            CSVFormat outputFileFormat1;
            CSVFormat outputFileFormat2;

            //Non-original run
            if (this.outputFile != null){
                String run_type = ini.get("User", "type");
                String [] headers_tobe_used;

                //Create headers
                if (run_type.equals("PYART")){
                    String [] headers = {"file_path","object","api","line_number","is_true_api","true_api","x1","x2","x3","x4"};
                    headers_tobe_used = headers;
                }
                else{
                    String [] headers = {"file_path","position","receiver","method","token_feature","parent_feature","sibling_feature","variable_usage_feature","variable_with_method_usage_feature"};
                    headers_tobe_used = headers;
                }          
                
                //Append to the main csv file if exists. So threads result won't override each other
                if(outputFile.exists() && !outputFile.isDirectory()) {                 
                    fw1 = new FileWriter(outputFile, true);
                    outputFileFormat1 = CSVFormat.DEFAULT.builder().setHeader(headers_tobe_used).setSkipHeaderRecord(true).build();
                }

                //Create the main csv file if it does not exist
                else{
                    fw1 = new FileWriter(outputFile);
                    outputFileFormat1 = CSVFormat.DEFAULT.builder()
                    .setHeader(headers_tobe_used)
                    .build();
                }  
                
                try (final Reader in = new FileReader(resultFilePath);
                final FileWriter fw_1 = fw1;
                final CSVPrinter printer = new CSVPrinter(fw_1, outputFileFormat1)) {
                    CSVFormat resultFileFormat = CSVFormat.DEFAULT.builder()
                        .setHeader(headers_tobe_used)
                        .setSkipHeaderRecord(true)
                        .build();

                    Iterable<CSVRecord> records = resultFileFormat.parse(in);                
                    printer.printRecords(records);
                }           
                
            }
            else{
                //Append to the main csv file if exists. So threads result won't override each other
                if( (outputDataFile.exists() && !outputDataFile.isDirectory()) || (outputLabelFile.exists() && !outputLabelFile.isDirectory()) ) {                 
                    fw1 = new FileWriter(outputDataFile, true);
                    outputFileFormat1 = CSVFormat.DEFAULT.builder().setSkipHeaderRecord(true).build();

                    fw2 = new FileWriter(outputLabelFile, true);
                    outputFileFormat2 = CSVFormat.DEFAULT.builder().setSkipHeaderRecord(true).build();
                }
                
                //Create the main csv file if it does not exist
                else{
                    fw1 = new FileWriter(outputDataFile);
                    outputFileFormat1 = CSVFormat.DEFAULT.builder().setSkipHeaderRecord(true).build();

                    fw2 = new FileWriter(outputLabelFile);
                    outputFileFormat2 = CSVFormat.DEFAULT.builder().setSkipHeaderRecord(true).build();
                } 
                
                String resultDataFilePath = resultFilePath.replaceAll(".csv","") + "_data.csv";
                String resultLabelFilePath = resultFilePath.replaceAll(".csv","") + "_label.csv";

                try (final Reader in1 = new FileReader(resultDataFilePath);
                     final Reader in2 = new FileReader(resultLabelFilePath);
                     final FileWriter fw_1 = fw1;
                     final FileWriter fw_2 = fw2;
                     final CSVPrinter printer1 = new CSVPrinter(fw_1, outputFileFormat1);
                     final CSVPrinter printer2 = new CSVPrinter(fw_2, outputFileFormat2);) {
                    
                        CSVFormat resultFileFormat = CSVFormat.DEFAULT.builder()
                        .setSkipHeaderRecord(true)
                        .build();

                        Iterable<CSVRecord> records = resultFileFormat.parse(in1);                
                        printer1.printRecords(records);
                    
                        records = resultFileFormat.parse(in2);                
                        printer2.printRecords(records);
                }           
            }            
    }
}
