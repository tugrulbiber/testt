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

        String subject = "Commit İncelemesi – Yapay Zeka Uyarısı";

        String body = "Merhaba " + author + ",\n\n" +
                "Bir commit incelemesi sırasında dikkat edilmesi gereken bir durum tespit edildi:\n\n" +
                " Repository: " + repoName + "\n" +
                " Dosya: " + fileName + "\n" +
                (lineNumber > 0 ? " Satır: " + lineNumber + "\n" : "") +
                " Commit ID: " + commitHash + "\n" +
                " Commit Mesajı: " + message + "\n\n" +
                " Yapay Zeka Açıklaması:\n" + aiFeedback + "\n\n" +
                "Lütfen bu dosyayı gözden geçir.\n\n" +
                "Teşekkürler,\nCommitScanner";

        try {
            MimeMessage mimeMessage = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(mimeMessage, false, "UTF-8");

            helper.setFrom("turulbiber@gmail.com");
            helper.setTo(email);
            helper.setSubject(subject);
            helper.setText(body);

            mailSender.send(mimeMessage);
            System.out.println(" Mail gönderildi: " + email);

        } catch (MessagingException e) {
            System.out.println(" Mail gönderilemedi: " + e.getMessage());
        }
    }
}
