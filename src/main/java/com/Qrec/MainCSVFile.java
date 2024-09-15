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

public class MainCSVFile {
    public synchronized void writeToFile(String threadId, String resultFilePath) throws IOException{

            
            String [] headers = {"file_path","object","api","line_number","is_true_api","x1","x2","x3","x4"};
            
            File fileToParse = new File("config.ini");
            Ini ini = new Ini(fileToParse);
            String outputFileName = ini.get("User", "output_multi_thread_file_name");
            File outputFile = new File( new File("data").getCanonicalPath() + "/" + outputFileName );

            FileWriter fw;
            CSVFormat outputFileFormat;
            
            if(outputFile.exists() && !outputFile.isDirectory()) {                 
                fw = new FileWriter(outputFile, true);
                outputFileFormat = CSVFormat.DEFAULT.builder().setHeader(headers).setSkipHeaderRecord(true).build();
            }

            //Create the main csv file if it does not exist
            else{
                fw = new FileWriter(outputFile);
                outputFileFormat = CSVFormat.DEFAULT.builder()
                .setHeader(headers)
                .build();
            }
            
            try (final Reader in = new FileReader(resultFilePath);
                final FileWriter fw_2 = fw;
                final CSVPrinter printer = new CSVPrinter(fw_2, outputFileFormat)) {
                
                CSVFormat resultFileFormat = CSVFormat.DEFAULT.builder()
                    .setHeader(headers)
                    .setSkipHeaderRecord(true)
                    .build();

                Iterable<CSVRecord> records = resultFileFormat.parse(in);                
                printer.printRecords(records);
            }            
    }
}
