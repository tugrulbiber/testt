package com.example.commitscanner.service;

import jakarta.mail.internet.InternetAddress;
import jakarta.mail.internet.MimeMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;

@Service
public class EmailService {

    @Autowired
    private JavaMailSender mailSender;

    public void sendSimpleEmail(String to, String subject, String text) {
        try {
            MimeMessage mimeMessage = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(
                    mimeMessage,
                    false,
                    StandardCharsets.UTF_8.name() // kritik!
            );

            helper.setFrom(new InternetAddress("turulbiber@gmail.com", "CommitScanner Bot", StandardCharsets.UTF_8.name()));
            helper.setTo(to);
            helper.setSubject(subject);
            helper.setText(text, false); // plain text, HTML değil

            mailSender.send(mimeMessage);

            System.out.println(" Mail gönderildi: " + to);
        } catch (Exception e) {
            System.out.println(" Mail gönderilemedi: " + e.getMessage());
        }
    }

    public void sendCommitNotification(String author, String email, String commitHash, String message,
                                       String aiFeedback, String repoName, String fileName, int lineNumber) {
        String subject = "Şüpheli Commit Tespit Edildi";

        String body = "Merhaba " + author + ",\n\n" +
                "Bir commit incelemesi sırasında dikkat edilmesi gereken bir durum tespit edildi:\n\n" +
                " Repository: " + repoName + "\n" +
                " Dosya: " + fileName + "\n" +
                (lineNumber > 0 ? "🔹 Satır: " + lineNumber + "\n" : "") +
                " Commit ID: " + commitHash + "\n" +
                " Commit Mesajı: " + message + "\n\n" +
                " Yapay Zeka Açıklaması:\n" + aiFeedback + "\n\n" +
                "Lütfen bu dosyayı gözden geçir.\n\n" +
                "Teşekkürler,\nCommitScanner";


        sendSimpleEmail(email, subject, body);
    }
}
