package com.example.commitscanner.service;

import org.springframework.stereotype.Service;

@Service
public class AiAnalyzerService {

    private final AiAnalyzer aiAnalyzer = new AiAnalyzer();

    public String analyzeCommit(String commitMessage, String diff) {
        // 1. AI cevabını al
        String feedback = aiAnalyzer.analyze(commitMessage, diff);

        // 2. Windows path'lerini temizle (örnek: C:\Users\...)
        feedback = feedback.replaceAll("[A-Z]:\\\\[^\\s\n\r]+", "[local path]");

        // 3. Unix/Linux path'lerini temizle (örnek: /home/user/project)
        feedback = feedback.replaceAll("(/[\\w\\-./]+)+", "[repo path]");

        // 4. Temizlenmiş sonucu döndür
        return feedback;
    }
}
