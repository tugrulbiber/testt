package com.example.commitscanner.service;

import java.io.BufferedReader;
import java.io.InputStreamReader;

public class AiAnalyzer {
    public String analyze(String commitMessage, String commitDiff) {
        ProcessBuilder pb;
        try {
            pb = new ProcessBuilder(
                    "python",
                    "src/main/python/analyze_commit_ai.py",
                    commitMessage,
                    commitDiff
            );

            // stdout + stderr birleşsin (hataları da okuyalım)
            pb.redirectErrorStream(true);

            Process process = pb.start();

            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream())
            );

            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append(System.lineSeparator());
            }

            process.waitFor();

            String result = output.toString().trim();
            return result.isEmpty()
                    ? "⚠️ AI analizinden sonuç alınamadı. Parametreler gitmemiş olabilir."
                    : result;

        } catch (Exception e) {
            e.printStackTrace();
            return " AI analiz hatası: " + e.getMessage();
        }
    }
}