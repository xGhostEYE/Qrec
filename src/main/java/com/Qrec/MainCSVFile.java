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
    File outputFile;
    Ini ini;

    public MainCSVFile() throws InvalidFileFormatException, IOException{
            File fileToParse = new File("config.ini");
            this.ini = new Ini(fileToParse);
            String outputFileName = ini.get("User", "output_multi_thread_file_name");
            File outputFile = new File( new File("data").getCanonicalPath() + "/" + outputFileName );
            this.outputFile = outputFile;
            
            //Delete the file if exist, so we can write new data into it later
            if(outputFile.exists() && !outputFile.isDirectory()) {
                outputFile.delete();
            }                     
    }
    public synchronized void writeToFile(String threadId, String resultFilePath) throws IOException{

            
            String run_type = ini.get("User", "type");

            String [] headers_tobe_used;
            if (run_type.equals("PYART")){
                String [] headers = {"file_path","object","api","line_number","is_true_api","x1","x2","x3","x4"};
                headers_tobe_used = headers;
            }
            else{
                String [] headers = {"file_path","position","receiver","method","token_feature","parent_feature","sibling_feature","variable_usage_feature"};
                headers_tobe_used = headers;
            }
            
            FileWriter fw;
            CSVFormat outputFileFormat;
            File outputFile = this.outputFile;

            //Append to the main csv file if exists. So threads result won't override each other
            if(outputFile.exists() && !outputFile.isDirectory()) {                 
                fw = new FileWriter(outputFile, true);
                outputFileFormat = CSVFormat.DEFAULT.builder().setHeader(headers_tobe_used).setSkipHeaderRecord(true).build();
            }

            //Create the main csv file if it does not exist
            else{
                fw = new FileWriter(outputFile);
                outputFileFormat = CSVFormat.DEFAULT.builder()
                .setHeader(headers_tobe_used)
                .build();
            }
            
            try (final Reader in = new FileReader(resultFilePath);
                final FileWriter fw_2 = fw;
                final CSVPrinter printer = new CSVPrinter(fw_2, outputFileFormat)) {
                
                CSVFormat resultFileFormat = CSVFormat.DEFAULT.builder()
                    .setHeader(headers_tobe_used)
                    .setSkipHeaderRecord(true)
                    .build();

                Iterable<CSVRecord> records = resultFileFormat.parse(in);                
                printer.printRecords(records);
            }            
    }
}
