package com.example.commitscanner.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;

@Service
public class EmailService {

    @Autowired
    private JavaMailSender mailSender;

    public void sendCommitNotification(String author, String email, String commitHash, String message,
                                       String aiFeedback, String repoName, String fileName, int lineNumber) {

        String subject = "Commit Review - AI Alert";

        StringBuilder bodyBuilder = new StringBuilder();
        bodyBuilder.append("A potential issue was detected during a commit review:\n\n")
                .append("Repository: ").append(repoName).append("\n")
                .append("File: ").append(fileName).append("\n");
        if (lineNumber > 0) {
            bodyBuilder.append("Line: ").append(lineNumber).append("\n");
        }
        if (commitHash != null && !commitHash.isBlank()) {
            bodyBuilder.append("Commit ID: ").append(commitHash).append("\n");
        }
        if (message != null && !message.isBlank()) {
            bodyBuilder.append("Commit Message: ").append(message).append("\n");
        }
        bodyBuilder.append("\nAI Explanation:\n").append(aiFeedback).append("\n\n")
                .append("Please review this file.\n\n")
                .append("Thank you,\nCommitScanner");

        try {
            MimeMessage mimeMessage = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(mimeMessage, false, "UTF-8");

            helper.setFrom("turulbiber@example.com"); //MAİL GÖNDEREN ADRESİ
            helper.setTo(email);
            helper.setSubject(subject);
            helper.setText(bodyBuilder.toString());

            mailSender.send(mimeMessage);
            System.out.println("Mail sent to: " + email);

        } catch (MessagingException e) {
            System.out.println("Failed to send mail: " + e.getMessage());
        }
    }
}
