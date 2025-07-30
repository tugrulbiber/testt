package com.example.commitscanner.service;

import org.springframework.stereotype.Service;

@Service
public class AiAnalyzerService {

    private final AiAnalyzer aiAnalyzer = new AiAnalyzer();

    public String analyzeCommit(String commitMessage, String diff) {
        String feedback = aiAnalyzer.analyze(commitMessage, diff);

        feedback = feedback.replaceAll("[A-Z]:\\\\[^\\s\n\r]+", "[local path]");

        feedback = feedback.replaceAll("(/[\\w\\-./]+)+", "[repo path]");

        return feedback;
    }
}
