package com.Qrec;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Reader;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;

public class MainCSVFile {
    public synchronized void writeToFile(String threadId, String resultFilePath) throws IOException{

            
            String [] headers = {"file_path","object","api","line_number","is_true_api","x1","x2","x3","x4"};

            //Create the main csv file if it does not exist
            File outputFile = new File( new File("data").getCanonicalPath() + "/main_result.csv" );
            FileWriter fw;
            CSVFormat outputFileFormat;
            if(outputFile.exists() && !outputFile.isDirectory()) {                 
                fw = new FileWriter(outputFile, true);
                outputFileFormat = CSVFormat.DEFAULT.builder().setSkipHeaderRecord(true).build();
            }

            else{
                fw = new FileWriter(outputFile);
                outputFileFormat = CSVFormat.DEFAULT.builder()
                .setHeader(headers)
                .build();
            }
            
            try (final CSVPrinter printer = new CSVPrinter(fw, outputFileFormat)) {
                
                // File resultFile = new File(resultFilePath);
                Reader in = new FileReader(resultFilePath);
                CSVFormat resultFileFormat = CSVFormat.DEFAULT.builder()
                    .setHeader(headers)
                    .setSkipHeaderRecord(true)
                    .build();

                Iterable<CSVRecord> records = resultFileFormat.parse(in);

                for (CSVRecord record : records) {

                    String file_path = record.get("file_path");
                    String object = record.get("object");
                    String api = record.get("api");
                    Integer line_number = Integer.valueOf(record.get("line_number"));
                    Integer is_true_api = Integer.valueOf(record.get("is_true_api"));
                    Float x1 = Float.valueOf(record.get("x1"));
                    Float x2 = Float.valueOf(record.get("x2"));
                    Float x3 = Float.valueOf(record.get("x3"));
                    Float x4 = Float.valueOf(record.get("x4"));

                    printer.printRecord(file_path, object,api,line_number,is_true_api,x1,x2,x3,x4);

                }
            }
        
            
    }
}
