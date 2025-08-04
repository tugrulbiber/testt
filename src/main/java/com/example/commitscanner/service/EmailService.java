package com.example.commitscanner.service;

import org.springframework.http.*;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;

import java.util.HashMap;
import java.util.Map;

@Service
public class EmailService {

    private final JavaMailSender mailSender;
    private final RestTemplate restTemplate;
    private final String aiApiUrl = "http://localhost:8000/analyze";

    public EmailService(JavaMailSender mailSender) {
        this.mailSender = mailSender;
        this.restTemplate = new RestTemplate();
    }

    public void sendCommitNotification(String author, String email, String commitHash, String message,
                                       String repoName, String fileName, String commitDiff) {

        Map<String, Object> commitData = new HashMap<>();
        commitData.put("repo_name", repoName);
        commitData.put("file_name", fileName);
        commitData.put("commit_id", commitHash);
        commitData.put("commit_message", message);
        commitData.put("commit_diff", commitDiff);

        ResponseEntity<Map> response = restTemplate.postForEntity(aiApiUrl, commitData, Map.class);

        if (response.getStatusCode() != HttpStatus.OK || response.getBody() == null) {
            throw new RuntimeException("AI analysis failed or returned empty response");
        }

        Map<String, Object> aiResult = response.getBody();
        String aiFeedback = (String) aiResult.getOrDefault("aiExplanation", "No significant issues detected.");
        int affectedLine = (Integer) aiResult.getOrDefault("affectedLine", 0);

        String subject = "CommitScanner Alert – Suspicious Commit Detected";

        StringBuilder bodyBuilder = new StringBuilder();
        bodyBuilder.append("Hello ").append(author).append(",\n\n")
                .append("A potentially suspicious commit has been detected by the CommitScanner system.\n\n")
                .append("Commit Details:\n")
                .append("- Commit ID   : ").append(commitHash).append("\n")
                .append("- Author      : ").append(author).append("\n")
                .append("- Message     : ").append(message).append("\n");
        if (affectedLine > 0) {
            bodyBuilder.append("- Affected Line: ").append(affectedLine).append("\n");
        }
        bodyBuilder.append("\nAI Analysis Result:\n").append(aiFeedback).append("\n\n")
                .append("Recommended Action:\n")
                .append("Please review the related code and consider revising it if necessary.\n\n")
                .append("Best regards,\n")
                .append("CommitScanner Bot");

        try {
            MimeMessage mimeMessage = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(mimeMessage, false, "UTF-8");

            helper.setFrom("turulbiber@example.com");
            helper.setTo(email);
            helper.setSubject(subject);
            helper.setText(bodyBuilder.toString());

            mailSender.send(mimeMessage);

        } catch (MessagingException e) {
            throw new RuntimeException("Failed to send mail: " + e.getMessage(), e);
        }
    }
}
